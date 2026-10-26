import copy
import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import DYNAMIC, FEATURES, VITALS, Logistic, Preprocessor, load, raw_features, read_patient, recent_vital_missingness, sirs, split
from evaluation import auc, matched_threshold, normalized, paired_bootstrap, utility, utility_parts
from make_synthetic import generate


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        generate(cls.tmp.name, 40)
        cls.patients = load(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_patient_split_is_disjoint_and_repeatable(self):
        a = [p for p in self.patients if p['hospital'] == 'A']
        one, two = split(a, 42), split(a, 42)
        sets = [set(p['id'] for p in v) for v in one.values()]
        self.assertEqual(sum(map(len, sets)), len(set.union(*sets)))
        self.assertEqual(one, two)
        self.assertTrue(all(p['hospital'] == 'A' for group in one.values() for p in group))

    def test_no_future_features(self):
        rows = copy.deepcopy(self.patients[0]['rows'])
        before = list(raw_features(rows))
        rows[-1]['HR'] = 9999
        after = list(raw_features(rows))
        self.assertEqual(before[:-1], after[:-1])

    def patient_with_hours(self, hours):
        rows = copy.deepcopy(self.patients[0]['rows'][:len(hours)])
        for row, hour in zip(rows, hours):
            row['ICULOS'] = hour
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'offset.psv'
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='|')
                writer.writeheader()
                writer.writerows({k: 'NaN' if v is None else v for k, v in row.items()} for row in rows)
            return read_patient(path, 'A')

    def test_iculos_offset_is_preserved(self):
        patient = self.patient_with_hours([2, 3, 4])
        self.assertEqual([row['ICULOS'] for row in patient['rows']], [2., 3., 4.])

    def test_invalid_iculos_is_rejected(self):
        for hours in ([2, 4], [2, 2], [0, 1], [2.5, 3.5], [None, 3]):
            with self.subTest(hours=hours), self.assertRaises(ValueError):
                self.patient_with_hours(hours)

    def test_no_backward_fill(self):
        rows = copy.deepcopy(self.patients[0]['rows'][:2])
        rows[0]['HR'], rows[1]['HR'] = None, 100.
        x = list(raw_features(rows))
        self.assertIsNone(x[0][len(DYNAMIC)])
        self.assertEqual(x[1][len(DYNAMIC)], 100.)

    def test_no_label_in_features(self):
        rows = copy.deepcopy(self.patients[0]['rows'])
        before = list(raw_features(rows))
        for row in rows:
            row['SepsisLabel'] = 1-row['SepsisLabel']
        self.assertEqual(before, list(raw_features(rows)))
        self.assertNotIn('SepsisLabel', FEATURES)

    def test_missingness_abstention(self):
        pre = Preprocessor().fit(self.patients[:10], cap=200)
        row = {c: None for c in DYNAMIC}
        self.assertTrue(pre.abstain(row))
        pre.missing95 = 1.
        self.assertTrue(pre.abstain(row, 'rate-pattern'))

    def test_recent_vitals_expire_without_future_fill(self):
        rows = [{c: None for c in DYNAMIC} for _ in range(8)]
        for c in VITALS:
            rows[1][c] = 1.
        rates = list(recent_vital_missingness(rows))
        self.assertEqual(rates, [1., 0., 0., 0., 0., 0., 0., 1.])
        rows[-1]['HR'] = 80.
        self.assertEqual(list(recent_vital_missingness(rows))[:-1], rates[:-1])

    def test_recent_vitals_hard_stop_when_legacy_cutoff_saturates(self):
        pre = Preprocessor().fit(self.patients[:10], cap=200)
        pre.missing95 = 1.
        row = {c: None for c in DYNAMIC}
        self.assertFalse(pre.abstain(row, 'rate'))
        self.assertTrue(pre.abstention_flags([row], 'recent-vitals')[0])
        self.assertLess(pre.recent_vitals95, 1.)

    def test_recent_vitals_accept_fresh_measurements(self):
        pre = Preprocessor().fit(self.patients[:10], cap=200)
        row = {c: None for c in DYNAMIC}
        row.update({c: 1. for c in VITALS})
        self.assertEqual(pre.abstention_flags([row], 'recent-vitals'), [False])

    def test_training_preprocessing_independent_of_evaluation(self):
        train = self.patients[:10]
        pre = Preprocessor().fit(train, cap=200)
        changed = copy.deepcopy(self.patients[20]['rows'])
        changed[0]['HR'] = 99999.
        original = pre.medians.copy()
        list(pre.transform(changed))
        self.assertEqual(original, pre.medians)

    def test_sirs_unknowns_do_not_count(self):
        row = {c: None for c in DYNAMIC}
        self.assertEqual(list(sirs([row])), [0])
        row.update(HR=100., Temp=39.)
        self.assertEqual(list(sirs([row])), [1])

    def test_published_utility_example(self):
        self.assertAlmostEqual(utility([0,0,0,0,1,1], [0,0,1,1,1,1]), 3.388888888888889)
        self.assertAlmostEqual(utility([0,0], [1,1]), -.1)

    def test_utility_tail_and_normalization(self):
        labels = [0]*10+[1]*20
        p = utility_parts(labels, [0]*30)
        self.assertEqual(normalized([p]), 0.)
        best = [int(4 <= t <= 19) for t in range(30)]
        self.assertAlmostEqual(normalized([utility_parts(labels, best)]), 1.)
        modified = best[:20]+[1]*10
        self.assertEqual(utility(labels, best), utility(labels, modified))

    def test_auc_ties_and_degenerate(self):
        self.assertEqual(auc([0,1], [.5,.5]), .5)
        self.assertEqual(auc([0,1], [.1,.9]), 1.)
        self.assertIsNone(auc([0,0], [.1,.9]))

    def test_conservative_threshold_ties(self):
        r = dict(labels=[0,0,0,1], scores=[.5,.5,.1,.9], sirs=[1,0,0,1])
        threshold, info = matched_threshold([r])
        self.assertGreater(threshold, .5)
        self.assertLessEqual(info['achieved_fpr'], info['target_fpr'])

    def test_bootstrap_is_paired_by_patient(self):
        r = dict(labels=[0,0,1,1], scores=[.1,.1,.8,.8], sirs=[0,0,1,1], abstain=[False]*4)
        ci = paired_bootstrap([r,r], .5, 'logistic', 20, 42)
        self.assertEqual(ci['utility_delta_vs_sirs_ci95'], [0.,0.])

    def test_logistic_learns_simple_relation(self):
        examples = [([-1.],0), ([1.],1)]*50
        m = Logistic().fit(examples, epochs=10)
        self.assertGreater(m.predict([1.]), .8)
        self.assertLess(m.predict([-1.]), .2)


if __name__ == '__main__':
    unittest.main()
