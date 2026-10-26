"""Install the reviewed follow-up into another local project, preserving baseline results.

Usage: python3 install_followup.py /absolute/path/to/sepsis_shift
This is supplied for the user to run; it was not executed on the original project.
"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project',type=Path)
    a=p.parse_args()
    source=Path(__file__).resolve().parent
    target=a.project.resolve()
    if target==source or not (target/'data').is_dir() or not (target/'core.py').is_file():
        p.error('Choose the existing separate project containing core.py and data/')
    result_target=target/'results/priorities_20261026'
    if result_target.exists():
        p.error('Follow-up results already exist; refusing to overwrite them')
    if not (source/'results/priorities_20261026/followup_summary.md').exists():
        p.error('The follow-up package is incomplete')
    files=['core.py','run.py','verify_saved.py','summarize_revisions.py','compare_abstention.py',
           'requirements-analysis.txt','README.md','tests/test_pipeline.py',
           'docs/revision_protocol_20261026.md','docs/followup_verification_20261026.md']
    backup=target/'backups'/('before_followup_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for name in files:
        dst=target/name
        if dst.exists():
            saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,saved)
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source/name,dst)
    shutil.copytree(source/'vendor/official',target/'vendor/official',dirs_exist_ok=True)
    shutil.copytree(source/'results/priorities_20261026',result_target)
    print('Installed follow-up:',result_target)
    print('Previous source files backed up:',backup)
    print('Original results/real_seed42 was not changed.')


if __name__=='__main__':
    main()
