"""Download public data and official scorer; stop on errors, never synthesize."""
import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

BASE = 'https://physionet.org/files/challenge-2019/1.0.0/'
SCORER = 'https://raw.githubusercontent.com/physionetchallenges/evaluation-2019/master/evaluate_sepsis_score.py'


def download(url, path):
    if path.exists():
        return
    temp = path.with_suffix(path.suffix+'.partial')
    try:
        with urllib.request.urlopen(url, timeout=60) as response, open(temp, 'wb') as target:
            shutil.copyfileobj(response, target)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, default=Path('data/physionet2019'))
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    sources = []
    for hospital in ('A', 'B'):
        archive = a.out/f'training_set{hospital}.zip'
        url = BASE+archive.name
        print('Downloading', url, flush=True)
        download(url, archive)
        destination = a.out/f'training_set{hospital}'
        destination.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            files = [info for info in z.infolist() if info.filename.endswith('.psv') and not info.filename.startswith('__MACOSX/')]
            names = [Path(info.filename).name for info in files]
            if not files or len(set(names)) != len(names):
                raise ValueError('Invalid archive: empty or duplicate PSV names')
            # Flatten under the known hospital directory, never trust archive paths.
            for info, name in zip(files, names):
                with z.open(info) as src, open(destination/name, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
        sources.append(dict(url=url, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), patients=len(files)))
    vendor = a.out/'official'
    vendor.mkdir(exist_ok=True)
    for url, name in ((SCORER, 'evaluate_sepsis_score.py'), (SCORER.rsplit('/',1)[0]+'/LICENSE.txt', 'LICENSE.txt')):
        download(url, vendor/name)
        sources.append(dict(url=url, sha256=hashlib.sha256((vendor/name).read_bytes()).hexdigest()))
    (a.out/'download_record.json').write_text(json.dumps(sources, indent=2)+'\n')
    print('Complete. Official scorer needs NumPy; pipeline itself uses Python standard library.')


if __name__ == '__main__':
    main()
