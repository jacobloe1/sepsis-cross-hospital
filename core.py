"""Dependency-free, causal PhysioNet 2019 preprocessing and logistic baseline."""
import csv
import hashlib
import math
import random
import statistics
from pathlib import Path

DYNAMIC = 'HR O2Sat Temp SBP MAP DBP Resp EtCO2 BaseExcess HCO3 FiO2 pH PaCO2 SaO2 AST BUN Alkalinephos Calcium Chloride Creatinine Bilirubin_direct Glucose Lactate Magnesium Phosphate Potassium Bilirubin_total TroponinI Hct Hgb PTT WBC Fibrinogen Platelets'.split()
STATIC = 'Age Gender Unit1 Unit2 HospAdmTime ICULOS'.split()
VITALS = 'HR O2Sat Temp SBP MAP DBP Resp'.split()
FEATURES = [f'{c}_{kind}' for kind in ('current', 'last', 'missing') for c in DYNAMIC] + STATIC


def finite(s):
    x = float(s)
    return x if math.isfinite(x) else None


def read_patient(path, hospital):
    with open(path) as f:
        reader = csv.DictReader(f, delimiter='|')
        required = set(DYNAMIC + STATIC + ['SepsisLabel'])
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'{path}: missing columns {required - set(reader.fieldnames or [])}')
        rows = [{k: finite(v) for k, v in row.items()} for row in reader]
    if not rows:
        raise ValueError(f'{path}: empty stay')
    labels = [r['SepsisLabel'] for r in rows]
    if any(y not in (0, 1) for y in labels) or labels != sorted(labels):
        raise ValueError(f'{path}: labels must be binary, nondecreasing')
    hours = [r['ICULOS'] for r in rows]
    # Some released stays begin after ICU hour 1. Preserve the recorded offset;
    # row indices, not the absolute ICULOS offset, define Challenge timing.
    if (any(h is None or h < 1 or not h.is_integer() for h in hours)
            or any(b != a + 1 for a, b in zip(hours, hours[1:]))):
        raise ValueError(f'{path}: expected positive, consecutive integer ICULOS values')
    return dict(id=f'{hospital}:{Path(path).stem}', hospital=hospital, rows=rows,
                labels=[int(y) for y in labels], sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def load(root):
    patients = []
    for hospital in ('A', 'B'):
        files = sorted((Path(root) / f'training_set{hospital}').rglob('*.psv'))
        if not files:
            raise ValueError(f'No PSV files in {root}/training_set{hospital}; see README.md')
        patients.extend(read_patient(p, hospital) for p in files)
    hashes = [p['sha256'] for p in patients]
    if len(set(hashes)) != len(hashes):
        raise ValueError('Duplicate patient file contents: remove duplicates before splitting')
    return patients


def split(patients, seed):
    """60/15/10/15, stratified by hospital and ever-positive status."""
    result = {k: [] for k in ('train', 'calibration', 'tune', 'test')}
    groups = {}
    for p in patients:
        groups.setdefault((p['hospital'], bool(any(p['labels']))), []).append(p)
    rng = random.Random(seed)
    for key in sorted(groups):
        group = sorted(groups[key], key=lambda p: p['id'])
        rng.shuffle(group)
        if len(group) < 8:
            raise ValueError(f'Stratum {key} needs at least 8 patients; got {len(group)}')
        n = len(group)
        a, b, c = int(n*.60), int(n*.75), int(n*.85)
        for name, chunk in zip(result, (group[:a], group[a:b], group[b:c], group[c:])):
            result[name].extend(chunk)
    ids = [p['id'] for group in result.values() for p in group]
    assert len(ids) == len(set(ids)) == len(patients)
    return result


def raw_features(rows):
    last = {c: None for c in DYNAMIC}
    for row in rows:
        for c in DYNAMIC:
            if row[c] is not None:
                last[c] = row[c]
        yield ([row[c] for c in DYNAMIC] + [last[c] for c in DYNAMIC]
               + [float(row[c] is None) for c in DYNAMIC] + [row[c] for c in STATIC])


def quantile(values, q):
    v = sorted(values)
    if not v:
        return None
    return v[min(len(v)-1, int(q*(len(v)-1)))]


def recent_vital_missingness(rows, window=6):
    """Fraction of seven vital signs not observed in current/previous 5 hours.

    No labs or future observations. Unobserved initial vitals stay missing.
    """
    last_seen = {}
    for t, row in enumerate(rows):
        for c in VITALS:
            if row[c] is not None:
                last_seen[c] = t
        yield sum(c not in last_seen or t-last_seen[c] >= window for c in VITALS)/len(VITALS)


class Preprocessor:
    def fit(self, patients, cap=50000, seed=0):
        # Reservoir is drawn only from training hours. Bounds memory for full cohort.
        rng, sample, seen = random.Random(seed), [], 0
        masks, missing, recent_counts = set(), [], [0]*(len(VITALS)+1)
        for p in patients:
            for value in recent_vital_missingness(p['rows']):
                recent_counts[round(value*len(VITALS))] += 1
            for row, x in zip(p['rows'], raw_features(p['rows'])):
                mask = tuple(row[c] is None for c in DYNAMIC)
                masks.add(mask)
                missing.append(sum(mask)/len(mask))
                seen += 1
                if len(sample) < cap:
                    sample.append(x)
                else:
                    j = rng.randrange(seen)
                    if j < cap:
                        sample[j] = x
        self.medians = []
        self.all_missing = []
        for j, name in enumerate(FEATURES):
            col = [x[j] for x in sample if x[j] is not None]
            self.medians.append(statistics.median(col) if col else 0.)
            if not col:
                self.all_missing.append(name)
        filled = [self.fill(x) for x in sample]
        self.means = [statistics.fmean(x[j] for x in filled) for j in range(len(FEATURES))]
        self.scales = [max(1e-6, math.sqrt(statistics.fmean((x[j]-self.means[j])**2 for x in filled))) for j in range(len(FEATURES))]
        self.missing95 = quantile(missing, .95)
        self.masks = masks
        # An all-missing current row is common for sparse labs. Instead require
        # recent vital evidence. All-seven-missing is an explicit hard stop;
        # estimate the reference 95th percentile only on training hours with
        # at least one recent vital, so that this cutoff cannot saturate at 1.
        supported = sum(recent_counts[:-1])
        if not supported:
            raise ValueError('Training contains no recently observed vital signs')
        rank, count = int(.95*(supported-1)), 0
        for j, frequency in enumerate(recent_counts[:-1]):
            count += frequency
            if count > rank:
                self.recent_vitals95 = j/len(VITALS)
                break
        self.recent_vitals_histogram = recent_counts
        self.training_hours = seen
        self.fit_sample_hours = len(sample)
        return self

    def fill(self, x):
        return [v if v is not None else self.medians[j] for j, v in enumerate(x)]

    def transform(self, rows):
        for x in raw_features(rows):
            yield [max(-10., min(10., (v-self.means[j])/self.scales[j])) for j, v in enumerate(self.fill(x))]

    def abstain(self, row, policy='rate'):
        mask = tuple(row[c] is None for c in DYNAMIC)
        return sum(mask)/len(mask) > self.missing95 or (policy == 'rate-pattern' and mask not in self.masks)

    def abstention_flags(self, rows, policy='rate'):
        if policy == 'recent-vitals':
            return [v == 1. or v > self.recent_vitals95 for v in recent_vital_missingness(rows)]
        return [self.abstain(row, policy) for row in rows]


def sirs(rows):
    """Partial SIRS proxy; no bands. Max age 6h vitals, 24h blood tests."""
    last, times = {}, {}
    for t, row in enumerate(rows):
        for c in ('HR', 'Temp', 'Resp', 'PaCO2', 'WBC'):
            if row[c] is not None:
                last[c], times[c] = row[c], t
        def value(c):
            limit = 24 if c in ('PaCO2', 'WBC') else 6
            return last.get(c) if c in times and t-times[c] <= limit else None
        hr, temp, resp, co2, wbc = [value(c) for c in ('HR', 'Temp', 'Resp', 'PaCO2', 'WBC')]
        criteria = [hr is not None and hr > 90,
                    temp is not None and (temp > 38 or temp < 36),
                    (resp is not None and resp > 20) or (co2 is not None and co2 < 32),
                    wbc is not None and (wbc > 12 or wbc < 4)]
        yield int(sum(criteria) >= 2)


def sigmoid(z):
    return 1/(1+math.exp(-max(-35., min(35., z))))


class Logistic:
    """Unweighted SGD for mean log loss plus (l2/2)*||weights||^2."""
    def fit(self, examples, epochs=15, l2=.001, seed=0):
        if not examples or len({y for x, y in examples}) < 2:
            raise ValueError('Logistic fit needs both classes')
        self.weights = [0.] * len(examples[0][0])
        prevalence = statistics.fmean(y for x, y in examples)
        self.bias = math.log(prevalence/(1-prevalence))
        rng = random.Random(seed)
        order = list(range(len(examples)))
        self.losses = []
        for epoch in range(epochs):
            rng.shuffle(order)
            rate, loss = .01/math.sqrt(1+epoch), 0.
            for i in order:
                x, y = examples[i]
                p = self.predict(x)
                loss -= y*math.log(max(1e-15, p)) + (1-y)*math.log(max(1e-15, 1-p))
                err = p-y
                for j, v in enumerate(x):
                    self.weights[j] -= rate*(err*v + l2*self.weights[j])
                self.bias -= rate*err
            self.losses.append(loss/len(examples))
        return self

    def logit(self, x):
        return self.bias + sum(w*v for w, v in zip(self.weights, x))

    def predict(self, x):
        return sigmoid(self.logit(x))


def reservoir_examples(patients, pre, cap, seed):
    rng, sample, seen = random.Random(seed), [], 0
    for p in patients:
        for x, y in zip(pre.transform(p['rows']), p['labels']):
            seen += 1
            if len(sample) < cap:
                sample.append((x, y))
            else:
                j = rng.randrange(seen)
                if j < cap:
                    sample[j] = (x, y)
    return sample
