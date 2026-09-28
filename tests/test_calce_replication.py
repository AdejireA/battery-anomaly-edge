"""CALCE causality, training provenance, clean gate and test lock."""
import sys
import json
import os
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import joblib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import calce_replication as r
from build_calce_relative_features import build_relative,features,load_development


class CalceReplicationTests(unittest.TestCase):
    def test_prior_only_current_and_future_excluded(self):
        d=pd.DataFrame({b:np.arange(25,dtype=float) for b in r.config()['base_features']})
        d['cell_id']='CS2-37';d['global_cycle']=np.arange(1,26)
        a=build_relative(d);self.assertTrue(a[features()].iloc[:10].isna().all().all())
        self.assertEqual(a.duration_s_prior10_median.iloc[10],4.5)
        d.loc[10:,'duration_s']=999
        b=build_relative(d);self.assertEqual(b.duration_s_prior10_median.iloc[10],4.5)
        pd.testing.assert_frame_equal(a.iloc[:10],b.iloc[:10])

    def test_cell_histories_isolated(self):
        d=pd.DataFrame({b:np.arange(15,dtype=float) for b in r.config()['base_features']});d['cell_id']='CS2-35';d['global_cycle']=np.arange(1,16)
        other=d.copy();other['cell_id']='CS2-36';other[r.config()['base_features']]+=100
        result=build_relative(pd.concat([d,other]))
        self.assertEqual(result.loc[result.cell_id.eq('CS2-36'),'duration_s_prior10_median'].iloc[10],104.5)
        other['cell_id']='CS2-38'
        with self.assertRaises(ValueError):build_relative(other)

    def test_nominal_provenance_and_saved_scaler(self):
        train=r.nominal(build_relative(load_development()))
        self.assertEqual(train.groupby('cell_id').size().to_dict(),{'CS2-35':254,'CS2-36':281})
        for seed in [42,123,2026]:
            bundle=joblib.load(r.MODELS/f'DEVELOPMENT_CALCE_seed{seed}.joblib')
            self.assertEqual(bundle['training_ids'],train[['cell_id','global_cycle']].to_dict('records'))
            np.testing.assert_allclose(bundle['scaler'].mean_,train[features()].mean().to_numpy())
            self.assertEqual(bundle['model'].random_state,seed)
        bad=train.assign(is_synthetic_anomaly=True)
        with self.assertRaises(ValueError):r.fit_model(bad,42)

    def test_clean_only_gate(self):
        d=pd.read_csv(r.OUT/'thresholds.csv')
        self.assertEqual(r.select_threshold(d[['seed','percentile','clean_fpr']]),95)
        with self.assertRaises(ValueError):r.select_threshold(d[['seed','percentile','clean_fpr']].assign(f1=1))

    def test_test_access_blocked_without_open(self):
        for name in ['CS2_38_discharge_features.csv','calce_cs2_discharge_features.csv']:
            with self.assertRaises(RuntimeError):r.access_guard('open',(str(ROOT/'data/processed/calce'/name),'r',os.O_RDONLY))

    def test_protocol_calibration_direction_and_severity(self):
        p=json.loads((ROOT/'config/calce_anomaly_injection_protocol.json').read_text())
        self.assertEqual(p['calibration_cell'],'CS2-37')
        values=[p['severity'][s] for s in ['mild','moderate','strong']]
        self.assertTrue(all(0<v['timing_factor']<1 and v['voltage_offset_v']>0 for v in values))
        self.assertTrue(values[0]['timing_factor']>values[1]['timing_factor']>values[2]['timing_factor'])
        self.assertTrue(values[0]['voltage_offset_v']<values[1]['voltage_offset_v']<values[2]['voltage_offset_v'])
        self.assertTrue(all('capacity_ah' not in s['affected_features'] for s in p['families'].values()))

    def test_synthetic_copies_preserve_sources_and_monotonic_drift(self):
        clean=load_development().loc[lambda d:d.cell_id.eq('CS2-37')].head(20).reset_index(drop=True)
        original=clean.copy(deep=True)
        protocol=json.loads((ROOT/'config/calce_anomaly_injection_protocol.json').read_text())
        copies,_=r.injected_copies(clean,protocol)
        pd.testing.assert_frame_equal(clean,original)
        for _,g in copies.groupby('scenario_id'):
            source=clean.set_index('global_cycle').loc[g.source_cycle]
            np.testing.assert_allclose(g.capacity_ah,source.capacity_ah)
            self.assertEqual(g.start_timestamp.tolist(),source.start_timestamp.tolist())
            if 'A4' in g.anomaly_family.iloc[0]:
                offsets=g.mean_voltage_v.to_numpy()-source.mean_voltage_v.to_numpy()
                self.assertAlmostEqual(offsets[0],0.)
                self.assertTrue((np.diff(offsets)*g.drift_sign.iloc[0]>=-1e-12).all())
            else:
                self.assertTrue((g.duration_s.to_numpy()<source.duration_s.to_numpy()).all())
                self.assertTrue(g.time_to_3_4v_s.le(g.duration_s).all())

    def test_nasa_and_sources_unchanged(self):
        path=r.OUT/'integrity_checks.json'
        if not path.exists():self.skipTest('Experiment still running')
        integrity=json.loads(path.read_text())
        self.assertEqual(integrity['nasa_before'],integrity['nasa_after'])
        self.assertEqual(r.nasa_hashes(),integrity['nasa_before'])
        self.assertFalse(integrity['test_cell_accessed'])
        self.assertFalse(any('CS2_38' in p for p in integrity['repository_reads']))


if __name__=='__main__':unittest.main()
