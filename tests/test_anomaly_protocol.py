"""Validate calibration isolation, exact reproducibility and physical directions."""

import json
import unittest

import numpy as np
import pandas as pd

from scripts.analyze_anomaly_ranges import ROOT, build_protocol, validation_rows


class AnomalyProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load only validation values for tests too; other-cell rows below are synthetic sentinels.
        cls.validation = validation_rows(pd.read_csv(ROOT / 'data/processed/nasa/nasa_discharge_features.csv'))
        cls.protocol = build_protocol(cls.validation)

    def test_no_test_statistics_and_frozen_reproducibility(self):
        sentinel = self.validation.copy()
        sentinel['cell_id'] = 'B0018'
        for column in sentinel.select_dtypes(include='number'):
            sentinel[column] = 1e99
        actual = build_protocol(pd.concat([self.validation, sentinel], ignore_index=True))
        self.assertEqual(actual, self.protocol)
        self.assertEqual(actual['calibration_cells'], ['B0007'])
        saved = json.loads((ROOT / 'config/anomaly_injection_protocol.json').read_text())
        self.assertEqual(saved, actual)

    def test_directions_severity_and_metadata(self):
        p = self.protocol
        for name, family in p['families'].items():
            self.assertFalse(set(family['affected_features']) & set(p['protected_fields']))
            if name.startswith(('A1_', 'A2_')):
                self.assertEqual(set(family['directions'].values()), {-1})
            elif name.startswith('A3_'):
                self.assertEqual(set(family['directions'].values()), {1})
            levels = family['severity']
            for feature in levels['mild']:
                values = [levels[level][feature] for level in ['mild', 'moderate', 'strong']]
                if isinstance(values[0], dict):
                    values = [v['decrease_at_validation_median'] for v in values]
                self.assertTrue(0 < values[0] < values[1] < values[2])

    def test_a2_positive_and_directionally_consistent(self):
        v = self.validation
        for changes in self.protocol['families']['A2_EARLY_VOLTAGE_COLLAPSE']['severity'].values():
            for feature, params in changes.items():
                self.assertTrue(0 < params['factor'] < 1)
                self.assertGreater(params['result_range'][0], 0)
            self.assertLessEqual(changes['time_to_3_4v_s']['factor'], changes['duration_s']['factor'])
            voltage = v.mean_voltage_v * changes['mean_voltage_v']['factor']
            self.assertTrue((voltage >= v.min_voltage_v).all())
            self.assertTrue((voltage <= v.max_voltage_v).all())

    def test_a3_temperature_identity_and_ordering(self):
        v = self.validation
        for changes in self.protocol['families']['A3_THERMAL_ABNORMALITY']['severity'].values():
            self.assertEqual(changes['max_temp_c'], changes['delta_temp_c'])
            maximum = v.max_temp_c + changes['max_temp_c']
            np.testing.assert_allclose(maximum - v.start_temp_c, v.delta_temp_c + changes['delta_temp_c'])
            self.assertTrue((maximum >= v.mean_temp_c + changes['mean_temp_c']).all())

    def test_a1_consistent_slope_and_a4_monotonic_offsets(self):
        a1 = self.protocol['families']['A1_ACCELERATED_DEGRADATION']
        for level, params in a1['severity'].items():
            expected = self.validation.capacity_ah.iloc[0] * params['retention_total_decrease'] / (a1['window_cycles'] - 1)
            self.assertAlmostEqual(expected, params['steady_slope_decrease_ah_per_cycle'])
            self.assertGreater(self.validation.capacity_retention.min() - params['retention_total_decrease'], 0)
        a4 = self.protocol['families']['A4_SENSOR_DRIFT']
        for params in a4['severity'].values():
            for magnitude in params.values():
                for sign in [-1, 1]:
                    offsets = sign * magnitude * np.arange(a4['window_cycles']) / (a4['window_cycles'] - 1)
                    self.assertTrue((sign * np.diff(offsets) > 0).all())
                    self.assertAlmostEqual(abs(offsets[-1]), magnitude)


if __name__ == '__main__':
    unittest.main()
