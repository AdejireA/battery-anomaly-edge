"""Phase 4C causality, fitting boundary, protocol integrity and scenario isolation."""

import hashlib
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from scripts.nasa_development import ROOT, load_development_data, nominal_training, read_config, clean_training_thresholds, anomaly_scores
from scripts.build_nasa_relative_features import build_relative_features, MANIFEST
from scripts.validate_nasa_relative_features import fit_relative, review_relative, relative_copy
from scripts.inject_nasa_anomalies import perturb_window


class RelativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_development_data()
        cls.relative=build_relative_features(cls.data)
        cls.nominal=nominal_training(cls.relative)
        cls.clean=cls.data.loc[cls.data.cell_id.eq('B0007')].reset_index(drop=True)
        cls.protocol=read_config('anomaly_injection_protocol.json')

    def test_exact_prior_window_and_no_current_leakage(self):
        source=self.clean.copy()
        source['duration_s']=np.arange(168,dtype=float)**2
        result=build_relative_features(source,[5])
        history=source.duration_s.iloc[5:10].to_numpy()
        median=np.median(history);mad=np.median(np.abs(history-median))
        self.assertEqual(result.duration_s_prior5_median.iloc[10],median)
        self.assertEqual(result.duration_s_prior5_mad.iloc[10],mad)
        self.assertAlmostEqual(result.duration_s_prior5_robust_residual.iloc[10],(100-median)/(1.4826*mad+1e-9))
        changed=source.copy();changed.loc[10,'duration_s']=999999
        other=build_relative_features(changed,[5])
        self.assertEqual(other.duration_s_prior5_median.iloc[10],median)
        self.assertEqual(other.duration_s_prior5_mad.iloc[10],mad)
        self.assertNotEqual(other.duration_s_prior5_robust_residual.iloc[10],result.duration_s_prior5_robust_residual.iloc[10])

    def test_no_future_leakage_and_prefix_invariance(self):
        original=build_relative_features(self.clean)
        altered=self.clean.copy()
        altered.loc[altered.cycle>60,read_config(MANIFEST)['base_features']]=99999
        changed=build_relative_features(altered)
        pd.testing.assert_frame_equal(original.iloc[:60],changed.iloc[:60])
        prefix=build_relative_features(self.clean.iloc[:60])
        pd.testing.assert_frame_equal(prefix,original.iloc[:60])

    def test_histories_do_not_cross_cells_and_missing_history_is_not_imputed(self):
        manifest=read_config(MANIFEST)
        for cell,group in self.relative.groupby('cell_id',sort=False):
            for k in [5,10,20]:
                self.assertTrue(group[f'duration_s_prior{k}_median'].iloc[:k].isna().all())
                self.assertTrue(group[f'capacity_slope_5_prior{k}_robust_residual'].iloc[:k+4].isna().all())
            individual=build_relative_features(self.data.loc[self.data.cell_id.eq(cell)])
            pd.testing.assert_frame_equal(group.reset_index(drop=True),individual)
        missing=self.clean.copy();missing.loc[20,'duration_s']=np.nan
        derived=build_relative_features(missing,[5])
        self.assertTrue(derived.duration_s_prior5_median.iloc[21:26].isna().all())
        self.assertTrue(pd.notna(derived.duration_s_prior5_median.iloc[26]))

    def test_epsilon_and_slope_change_definition(self):
        source=self.clean.copy();source.loc[:9,'duration_s']=100;source.loc[10,'duration_s']=101
        out=build_relative_features(source,[5])
        self.assertEqual(out.duration_s_prior5_mad.iloc[10],0)
        self.assertAlmostEqual(out.duration_s_prior5_robust_residual.iloc[10]/1e9,1)
        np.testing.assert_allclose(out.capacity_slope_change_prior5_ah_per_cycle,
                                   out.capacity_slope_5-out.capacity_slope_5_prior5_median,equal_nan=True)

    def test_no_test_cell_access_and_no_raw_features_in_model_manifest(self):
        real=pd.read_csv;paths=[]
        def reader(path,*args,**kwargs):
            self.assertNotIn('B0018',str(path));self.assertNotIn('nasa_discharge_features.csv',str(path));paths.append(str(path))
            return real(path,*args,**kwargs)
        with patch('scripts.nasa_development.pd.read_csv',side_effect=reader):
            load_development_data()
        self.assertEqual(len(paths),3)
        with self.assertRaises(ValueError):build_relative_features(self.clean.assign(cell_id='B0018'))
        for sets in read_config(MANIFEST)['feature_sets'].values():
            for features in sets.values():
                self.assertEqual(len(features),7)
                self.assertTrue(all(f.endswith('_robust_residual') for f in features))

    def test_scaler_and_model_only_fit_clean_nominal_relative_matrix(self):
        captured={};scaler_fit=StandardScaler.fit;forest_fit=IsolationForest.fit
        def scale(obj,X,y=None,**kwargs):
            self.assertIsNone(y);captured['scale']=X.copy();return scaler_fit(obj,X,y=y,**kwargs)
        def fit(obj,X,y=None,**kwargs):
            self.assertIsNone(y);captured['fit']=X.copy();return forest_fit(obj,X,y=y,**kwargs)
        with patch.object(StandardScaler,'fit',scale),patch.object(IsolationForest,'fit',fit):
            bundle=fit_relative(self.nominal,'RELATIVE_A',10,100,1.,42)
        expected=self.nominal[bundle['features']].dropna()
        pd.testing.assert_frame_equal(captured['scale'],expected)
        np.testing.assert_allclose(captured['fit'],bundle['scaler'].transform(expected))
        self.assertEqual(len(expected),72)
        ids=pd.DataFrame(bundle['provenance']['training_ids'])
        self.assertEqual(ids.groupby('cell_id').size().to_dict(),{'B0005':36,'B0006':36})
        self.assertTrue(ids.cycle.between(15,50).all())
        for bad in [self.nominal.assign(is_synthetic_anomaly=False),self.relative,self.nominal.assign(cell_id='B0007')]:
            with self.assertRaises(ValueError):fit_relative(bad,'RELATIVE_A',10,100,1.,42)

    def test_thresholds_training_only_and_review_rejects_synthetic_metrics(self):
        bundle=fit_relative(self.nominal,'RELATIVE_B',20,100,1.,42)
        scores,_=anomaly_scores(bundle,self.nominal)
        actual=clean_training_thresholds(bundle,self.nominal)
        np.testing.assert_allclose([t['threshold'] for t in actual],np.percentile(scores,[95,97.5,99]))
        with self.assertRaises(ValueError):clean_training_thresholds(bundle,self.relative)
        with self.assertRaises(ValueError):clean_training_thresholds(bundle,self.nominal.assign(is_synthetic_anomaly=True))
        rows=pd.DataFrame([dict(feature_set='RELATIVE_B',history_window=20,n_estimators=100,max_features=1.,seed=seed,percentile=p,clean_fpr=.04) for seed in [42,123,2026] for p in [95.,97.5,99.]])
        self.assertTrue(review_relative(rows).eligible.all())
        with self.assertRaises(ValueError):review_relative(rows.assign(f1=1.))

    def test_protocol_unchanged_and_sequential_baselines_isolated(self):
        path=ROOT/'config/anomaly_injection_protocol.json';before=hashlib.sha256(path.read_bytes()).hexdigest()
        original=self.clean.copy(deep=True)
        family='A4_SENSOR_DRIFT'
        injected=perturb_window(self.clean,family,'strong',30,self.protocol,'mean_temp_c',1)
        result=relative_copy(self.clean,injected,5)
        first_baseline=self.clean.mean_temp_c.iloc[25:30].median()
        self.assertAlmostEqual(result.mean_temp_c_prior5_median.iloc[0],first_baseline)
        self.assertAlmostEqual(result.mean_temp_c_prior5_median.iloc[7],injected.mean_temp_c.iloc[2:7].median())
        # A second independent scenario must not inherit any first scenario history.
        unrelated=perturb_window(self.clean,family,'mild',50,self.protocol,'mean_temp_c',-1)
        second=relative_copy(self.clean,unrelated,5)
        self.assertAlmostEqual(second.mean_temp_c_prior5_median.iloc[0],self.clean.mean_temp_c.iloc[45:50].median())
        pd.testing.assert_frame_equal(self.clean,original)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
        # A1 current slope is recomputed by frozen injection before relative baselines.
        ramp=perturb_window(self.clean,'A1_ACCELERATED_DEGRADATION','mild',30,self.protocol)
        relative=relative_copy(self.clean,ramp,10)
        self.assertAlmostEqual(relative.capacity_slope_5_prior10_median.iloc[15],ramp.capacity_slope_5.iloc[5:15].median())


if __name__=='__main__':unittest.main()
