"""Verify the released subset, without requiring archive-only dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT, load_models=False):
    manifest = json.loads((root / 'artifacts/manifest.json').read_text(encoding='utf-8'))
    records = manifest['models'] + manifest['figures'] + manifest['evidence']
    for record in records:
        path = (root / record['path']).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Artifact path leaves repository')
        data = path.read_bytes()
        if len(data) != record['size_bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Artifact integrity mismatch: ' + record['path'])
    if load_models:
        import warnings
        import joblib
        from sklearn.exceptions import InconsistentVersionWarning
        # Verify ALL bytes before deserializing any released artifact.
        with warnings.catch_warnings():
            warnings.simplefilter('error', InconsistentVersionWarning)
            for record in manifest['models']:
                obj = joblib.load(root / record['path'])
                if record['kind'] == 'bundle':
                    assert list(obj['features']) == record['features']
                    assert obj['model'].n_features_in_ == len(record['features'])
                else:
                    assert obj.n_features_in_ == len(record['features'])
    return len(records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--load-models', action='store_true', help='Also deserialize trusted models after verifying hashes')
    args = parser.parse_args()
    print(f'Verified {verify(load_models=args.load_models)} released artifacts' + ('; models loaded' if args.load_models else ''))
