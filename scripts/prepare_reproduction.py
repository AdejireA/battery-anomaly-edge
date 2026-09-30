"""Prepare a fresh, ignored experiment directory without historical outputs."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def prepare(destination):
    destination = Path(destination).resolve()
    if not destination.is_relative_to((ROOT / 'output').resolve()) or destination == (ROOT / 'output').resolve():
        raise ValueError('Choose a new subdirectory inside this repository output/')
    if destination.exists():
        raise FileExistsError('Experiment directory must not already exist')
    destination.mkdir(parents=True)
    for directory in ['scripts', 'tests', 'config']:
        (destination / directory).mkdir()
        pattern = '*.json' if directory == 'config' else '*.py'
        for source in (ROOT / directory).glob(pattern):
            if source.name in ['final_nasa_model.json', 'final_calce_model.json',
                               'test_v02_reproducibility.py', 'prepare_reproduction.py', 'verify_artifacts.py']:
                continue
            shutil.copyfile(source, destination / directory / source.name)
    for name in ['requirements.txt', 'requirements-lock.txt']:
        shutil.copyfile(ROOT / name, destination / name)
    for directory in ['results', 'data/raw/nasa', 'data/raw/calce', 'data/processed']:
        (destination / directory).mkdir(parents=True, exist_ok=True)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=ROOT / 'output/reproduction')
    args = parser.parse_args()
    print(prepare(args.destination))
    print('Place independently acquired raw data here; follow docs/reproduction.md in the release root.')
