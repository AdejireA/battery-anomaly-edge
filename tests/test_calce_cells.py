"""Four-cell artifact invariants and no-training safety checks."""
import sys
import json
import ast
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import extract_calce as e


class CalceCellsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=pd.read_csv(ROOT/'data/processed/calce/calce_cs2_discharge_features.csv',parse_dates=['start_timestamp','end_timestamp'])

    def test_cell_identity_and_combined_table(self):
        self.assertEqual(set(self.data.cell_id),set(e.CELLS))
        for cell in e.CELLS:
            separate=pd.read_csv(ROOT/'data/processed/calce'/f'{cell.replace("-","_")}_discharge_features.csv')
            self.assertEqual(set(separate.cell_id),{cell})
            group=self.data.loc[self.data.cell_id.eq(cell)]
            self.assertEqual(len(group),len(separate))
            np.testing.assert_allclose(group.capacity_ah,separate.capacity_ah,rtol=1e-12)
            self.assertTrue(group.source_workbook.str.startswith(cell.replace('-','_')+'_').all())

    def test_order_and_positive_capacities(self):
        for _,g in self.data.groupby('cell_id'):
            self.assertEqual(g.global_cycle.tolist(),list(range(1,len(g)+1)))
            self.assertTrue(g.start_timestamp.is_monotonic_increasing)
            self.assertTrue((g.end_timestamp.shift()<g.start_timestamp).iloc[1:].all())
            self.assertTrue(g.capacity_ah.gt(0).all())

    def test_integration_agreement(self):
        self.assertLessEqual(self.data.capacity_integration_error_pct.abs().max(),.01)
        np.testing.assert_allclose(self.data.capacity_ah,self.data.capacity_counter_final_ah-self.data.capacity_counter_initial_ah,atol=1e-12)

    def test_duplicates_and_incomplete_excluded(self):
        for cell,g in self.data.groupby('cell_id'):
            directory=e.OUT/cell.replace('-','_')
            workbooks=pd.read_csv(directory/'workbook_audit.csv')
            self.assertFalse(g.source_workbook.isin(workbooks.loc[~workbooks.included,'source_workbook']).any())
            candidates=pd.read_csv(directory/'candidate_discharge_audit.csv').fillna({'rejection_reason':''})
            accepted=candidates.loc[candidates.rejection_reason.eq('')]
            self.assertTrue(accepted.next_step_index.eq(8).all())
            self.assertFalse(accepted.end_of_file.any())
            self.assertTrue(accepted.cutoff_final_voltage_v.le(2.7).all())
            self.assertEqual(set(zip(g.source_workbook,g.source_cycle_index)),set(zip(accepted.source_workbook,accepted.source_cycle_index)))

    def test_duplicate_selection_deterministic(self):
        from test_calce_cs2_35_extraction import trace
        from unittest.mock import patch
        from datetime import date
        rows=[dict(path=Path('b.xlsx'),date=date(2011,2,10),frame=trace()),dict(path=Path('a.xlsx'),date=date(2011,2,4),frame=trace())]
        with patch.object(e.base,'sha',return_value='fixture'):
            a,_=e.base.order_and_deduplicate(rows);b,_=e.base.order_and_deduplicate(rows[::-1])
        self.assertEqual(a[0]['path'],b[0]['path'])
        self.assertEqual(a[0]['path'].name,'a.xlsx')

    def test_nasa_original_artifacts_unchanged(self):
        saved=json.loads((e.OUT/'extraction_integrity.json').read_text())
        self.assertEqual(saved['nasa_before'],saved['nasa_after'])
        for path,digest in saved['nasa_before'].items():self.assertEqual(e.base.sha(ROOT/path),digest,path)

    def test_no_ml_calls_or_model_imports(self):
        for filename in ['extract_calce.py','audit_calce_cells.py','extract_calce_cs2_35.py']:
            tree=ast.parse((ROOT/'scripts'/filename).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):self.assertFalse(any(n.name.startswith(('sklearn','torch','tensorflow')) for n in node.names))
                if isinstance(node,ast.ImportFrom):self.assertFalse((node.module or '').startswith(('sklearn','torch','tensorflow')))
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,['fit','fit_transform','partial_fit'])


if __name__=='__main__':unittest.main()
