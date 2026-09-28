"""Burn-in temporal isolation, frozen model use and clean-only selection."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd

from scripts.nasa_development import load_development_data, read_config
from scripts.nasa_burnin import (saved_models, prohibit_fitting, split_clean_validation,
                                calibrate_and_evaluate_clean, eligible_for_review)
from scripts.inject_nasa_anomalies import generate_validation_copies, perturb_window


class BurninTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_development_data()
        cls.clean = cls.data.loc[cls.data.cell_id.eq('B0007')].reset_index(drop=True)
        cls.bundle = next(saved_models())[1]
        cls.protocol = read_config('anomaly_injection_protocol.json')

    def test_whitelisted_loader_never_accesses_test_cell(self):
        real = pd.read_csv
        accessed = []
        def guarded(path, *args, **kwargs):
            self.assertNotIn('B0018', str(path))
            self.assertNotIn('nasa_discharge_features.csv', str(path))
            accessed.append(str(path))
            return real(path, *args, **kwargs)
        with patch('scripts.nasa_development.pd.read_csv', side_effect=guarded):
            result = load_development_data()
        self.assertEqual(len(accessed), 3)
        self.assertEqual(set(result.cell_id), {'B0005','B0006','B0007'})

    def test_temporal_boundaries_counts_and_disjointness(self):
        previous = set()
        for fraction, boundary in [(.2,33),(.3,50),(.4,67)]:
            early, late, actual = split_clean_validation(self.clean, fraction)
            self.assertEqual(actual, boundary)
            self.assertEqual(early.cycle.tolist(), list(range(1,boundary+1)))
            self.assertEqual(late.cycle.tolist(), list(range(boundary+1,169)))
            self.assertFalse(set(early.cycle) & set(late.cycle))
            self.assertTrue(previous < set(early.cycle))
            previous = set(early.cycle)

    def test_no_refit_and_calibration_uses_only_early_clean_scores(self):
        state = joblib.hash(self.bundle)
        for fraction, boundary in [(.2,33),(.3,50),(.4,67)]:
            with prohibit_fitting():
                rows, early, late = calibrate_and_evaluate_clean(self.bundle, self.clean, fraction)
            self.assertEqual(len(early), boundary-4)
            self.assertEqual(len(late),168-boundary)
            np.testing.assert_allclose([r['threshold'] for r in rows],np.percentile(early,[95,97.5,99]))
            for r in rows:
                self.assertEqual(r['post_calibration_clean_fpr'],float((late > r['threshold']).mean()))
            changed = self.clean.copy()
            changed.loc[changed.cycle > boundary,self.bundle['features']] *= 2
            with prohibit_fitting():
                altered, _, _ = calibrate_and_evaluate_clean(self.bundle,changed,fraction)
            self.assertEqual([r['threshold'] for r in rows],[r['threshold'] for r in altered])
        self.assertEqual(joblib.hash(self.bundle),state)

    def test_synthetic_labels_and_wrong_cell_rejected_in_calibration(self):
        for bad in [self.clean.assign(is_synthetic_anomaly=False),self.clean.assign(severity='mild'),self.clean.assign(cell_id='B0018')]:
            with self.assertRaises(ValueError):
                calibrate_and_evaluate_clean(self.bundle,bad,.3)

    def test_real_perturbations_only_emit_postcalibration_cycles(self):
        snapshot = self.clean.copy(deep=True)
        for fraction in [.2,.3,.4]:
            early, late, boundary = split_clean_validation(self.clean,fraction)
            for family in self.protocol['families']:
                extra={'channel':'mean_temp_c','sign':1} if family.startswith('A4') else {}
                window=perturb_window(self.clean,family,'strong',boundary,self.protocol,**extra)
                self.assertTrue(window.source_cycle.gt(boundary).all())
                self.assertFalse(set(window.source_cycle) & set(early.cycle))
                self.assertEqual(window.source_cycle.iloc[0],boundary+1)
        pd.testing.assert_frame_equal(self.clean,snapshot)

    def test_generator_never_starts_windows_during_calibration(self):
        # Real A1 generation at the longest burn-in: exercises context at boundary.
        protocol=deepcopy(self.protocol)
        family='A1_ACCELERATED_DEGRADATION'
        protocol['families']={family:protocol['families'][family]}
        protocol['families'][family]['severity']={'mild':protocol['families'][family]['severity']['mild']}
        copied,counts=generate_validation_copies(self.clean,protocol,min_source_cycle=68)
        self.assertEqual(counts.accepted_windows.sum(),11)
        self.assertTrue(copied.source_cycle.gt(67).all())
        self.assertTrue(copied.window_start_cycle.gt(67).all())
        self.assertEqual(set(copied.window_start_cycle),set(range(68,79)))

    def test_clean_only_review_all_seeds_and_shorter_first(self):
        rows=[]
        for fraction in [.2,.3,.4]:
            for percentile in [95.,97.5,99.]:
                for seed in [42,123,2026]:
                    rate=.1 if fraction==.2 or percentile==95 else .04
                    rows.append(dict(feature_set='degradation_aware',n_estimators=100,max_features=1.,seed=seed,
                                     calibration_fraction=fraction,percentile=percentile,post_calibration_clean_fpr=rate))
        frame=pd.DataFrame(rows)
        _,eligible=eligible_for_review(frame)
        self.assertEqual(eligible.iloc[0].calibration_fraction,.3)
        self.assertEqual(eligible.iloc[0].percentile,97.5)
        with self.assertRaises(ValueError):
            eligible_for_review(frame.assign(f1=1.))
        _,empty=eligible_for_review(frame.assign(post_calibration_clean_fpr=.2))
        self.assertTrue(empty.empty)
        frame.loc[(frame.calibration_fraction==.3)&(frame.percentile==97.5)&(frame.seed==42),'post_calibration_clean_fpr']=.06
        _,eligible=eligible_for_review(frame)
        self.assertFalse(((eligible.calibration_fraction==.3)&(eligible.percentile==97.5)).any())


if __name__=='__main__':
    unittest.main()
