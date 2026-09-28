"""Freeze boundary and final evaluation invariants; tests never open test data."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import finalize_nasa as final
from nasa_burnin import prohibit_fitting
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


class FinalEvaluationTests(unittest.TestCase):
    def test_first_all_seed_eligible_percentile(self):
        d=pd.DataFrame([dict(seed=s,percentile=p,threshold=p/100,clean_fpr=.01) for p in [95.,97.5,99.] for s in [42,123,2026]])
        self.assertEqual(final.select_threshold(d),(95.,.95))
        d.loc[(d.percentile==95)&(d.seed==123),'clean_fpr']=.06
        self.assertEqual(final.select_threshold(d),(97.5,.975))
        d['clean_fpr']=.06
        with self.assertRaises(RuntimeError):final.select_threshold(d)

    def test_synthetic_metrics_cannot_enter_selection(self):
        d=pd.DataFrame(columns=['seed','percentile','threshold','clean_fpr','f1'])
        with self.assertRaises(ValueError):final.select_threshold(d)

    def test_test_access_blocked_before_freeze(self):
        with patch.object(final,'UNLOCKED',False):
            with self.assertRaises(RuntimeError):
                final.guard('open',(str(ROOT/'data/processed/nasa/B0018_discharge_features.csv'),'r',os.O_RDONLY))

    def test_final_configuration_cannot_be_rewritten_by_evaluation(self):
        with patch.object(final,'PROTECTED',{final.CONFIG.resolve()}):
            with self.assertRaises(RuntimeError):
                final.guard('open',(str(final.CONFIG),'w',os.O_WRONLY|os.O_TRUNC))
        if final.CONFIG.exists():
            before=final.digest(final.CONFIG)
            with self.assertRaises(FileExistsError):final.write_once(final.CONFIG,{'f1_selected':True})
            self.assertEqual(before,final.digest(final.CONFIG))

    def test_fitting_forbidden(self):
        with prohibit_fitting():
            for estimator in [StandardScaler(),IsolationForest()]:
                with self.assertRaises(RuntimeError):estimator.fit([[0.],[1.]])

    def test_authorization_does_not_change_relative_definition(self):
        # Fabricated values, no held-out data. Current/future leakage checked exactly.
        manifest=json.loads((ROOT/'config/nasa_relative_feature_manifest.json').read_text())
        d=pd.DataFrame({b:np.arange(25,dtype=float)**2 for b in manifest['base_features']})
        d['cell_id']='B0007';d['cycle']=np.arange(1,26)
        expected=final.build_relative_features(d,[10])
        d['cell_id']='B0018'
        actual=final.build_relative_features(d,[10],allowed_cells=('B0018',))
        pd.testing.assert_frame_equal(expected.drop(columns='cell_id'),actual.drop(columns='cell_id'))
        d.loc[10:,manifest['base_features']]=9999.
        changed=final.build_relative_features(d,[10],allowed_cells=('B0018',))
        self.assertEqual(actual.loc[10,'duration_s_prior10_median'],changed.loc[10,'duration_s_prior10_median'])

    def test_frozen_configuration_and_provenance(self):
        if not final.CONFIG.exists():self.skipTest('Stage 1 has not run')
        config=final.verify_freeze()
        self.assertEqual(config['features'],json.loads((ROOT/'config/nasa_relative_feature_manifest.json').read_text())['feature_sets']['10']['RELATIVE_B'])
        self.assertEqual(config['history_window'],10)
        self.assertEqual(config['random_seed'],42)
        self.assertTrue(all(r['cell_id'] in ['B0005','B0006'] and 11<=r['cycle']<=50 for r in config['scaler_provenance']['training_ids']))

    def test_post_test_integrity_and_order(self):
        path=final.OUT/'integrity_receipt.json'
        if not path.exists():self.skipTest('Stage 2 has not run')
        r=json.loads(path.read_text())
        self.assertEqual(r['before_hashes'],r['after_hashes'])
        self.assertEqual(r['threshold_before'],r['threshold_after'])
        self.assertTrue(r['no_test_rows_in_fitting'])
        self.assertEqual(r['freeze_receipt']['test_accesses_before_freeze'],[])
        self.assertTrue(all(a['utc']>r['freeze_receipt']['utc'] for a in r['test_access_log']))
        final.verify_freeze()


if __name__=='__main__':unittest.main()
