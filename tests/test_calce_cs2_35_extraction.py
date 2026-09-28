"""Counter reconstruction, duplicate ordering and interruption safety tests."""
import sys
from pathlib import Path
from datetime import date
import unittest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import extract_calce_cs2_35 as extraction


def trace(baseline=10.):
    frame=pd.DataFrame(0.,index=range(5),columns=extraction.FINGERPRINT_COLUMNS)
    frame['Data_Point']=np.arange(1,6);frame['Cycle_Index']=1
    frame['Step_Index']=[6,7,7,7,8]
    frame['Test_Time(s)']=[100.,110.,1900.,3700.,3760.]
    frame['Step_Time(s)']=[5.,10.,1800.,3600.,60.]
    frame['Date_Time']=pd.Timestamp('2010-01-01')+pd.to_timedelta(frame['Test_Time(s)'],unit='s')
    frame['Current(A)']=[0.,-1.1,-1.1,-1.1,0.]
    frame['Voltage(V)']=[4.2,4.1,3.6,2.6998,3.4]
    frame['Discharge_Capacity(Ah)']=[baseline,baseline+1.1*10/3600,baseline+.55,baseline+1.1,baseline+1.1]
    return frame


class CalceExtractionTests(unittest.TestCase):
    def test_counter_uses_pre_step_reference_and_integration_covers_initial_gap(self):
        d=trace();g,near=next(extraction.candidate_segments(d))
        r,t,v=extraction.segment_record(d,g,'example.xlsx',near)
        self.assertAlmostEqual(r['capacity_ah'],1.1)
        self.assertAlmostEqual(r['capacity_from_current_ah'],1.1)
        self.assertAlmostEqual(r['capacity_counter_initial_ah'],10.)
        self.assertEqual(r['first_sample_elapsed_s'],10.)
        self.assertEqual(r['duration_s'],3600.)
        self.assertEqual(r['rejection_reason'],'')

    def test_workbook_counter_offset_does_not_change_capacity(self):
        capacities=[]
        for baseline in [0.,10.,99.]:
            d=trace(baseline);g,near=next(extraction.candidate_segments(d))
            capacities.append(extraction.segment_record(d,g,'example.xlsx',near)[0]['capacity_ah'])
        np.testing.assert_allclose(capacities,1.1)

    def test_small_cross_clock_transition_offset_does_not_discard_complete_trace(self):
        d=trace();d.loc[0,'Test_Time(s)']+=.02
        g,near=next(extraction.candidate_segments(d));r,_,_=extraction.segment_record(d,g,'example.xlsx',near)
        self.assertAlmostEqual(r['pre_step_to_onset_gap_s'],-.02)
        self.assertEqual(r['rejection_reason'],'')
        self.assertAlmostEqual(r['capacity_ah'],1.1)

    def test_eof_and_flat_counter_are_flagged(self):
        d=trace().iloc[:-1].copy();d.loc[2,'Discharge_Capacity(Ah)']=d.loc[1,'Discharge_Capacity(Ah)']
        g,near=next(extraction.candidate_segments(d));r,_,_=extraction.segment_record(d,g,'example.xlsx',near)
        self.assertIn('end_of_file_while_discharging',r['rejection_reason'])
        self.assertIn('non_increasing_discharge_capacity_counter',r['rejection_reason'])

    def test_current_identification_checks_step_instead_of_assuming_seven(self):
        d=trace();d.loc[d.Step_Index.eq(7),'Step_Index']=12
        g,near=next(extraction.candidate_segments(d));r,_,_=extraction.segment_record(d,g,'example.xlsx',near)
        self.assertTrue(near)
        self.assertIn('unexpected_main_discharge_step_requires_review',r['rejection_reason'])

    def test_duplicate_selection_uses_measurement_time_then_filename_date(self):
        d=trace();later=d.copy();later['Date_Time']+=pd.Timedelta(days=10)
        # Paths are real only for raw-byte audit, which is patched to avoid fixture files.
        from unittest.mock import patch
        w=[dict(path=Path('later.xlsx'),date=date(2010,2,1),frame=d.copy()),dict(path=Path('earliest_copy.xlsx'),date=date(2010,1,2),frame=d.copy()),dict(path=Path('earlier_filename_but_later_data.xlsx'),date=date(2009,1,1),frame=later)]
        with patch.object(extraction,'sha',return_value='fixture'):
            kept,audit=extraction.order_and_deduplicate(w)
        self.assertEqual([x['path'].name for x in kept],['earliest_copy.xlsx','earlier_filename_but_later_data.xlsx'])
        self.assertEqual(audit.loc[~audit.included,'duplicate_of'].tolist(),['earliest_copy.xlsx'])
        altered=d.copy();altered.loc[1,'Voltage(V)']+=.01
        self.assertNotEqual(extraction.fingerprint(d),extraction.fingerprint(altered))

    def test_cutoff_rule_uses_observed_transition_cluster(self):
        candidates=pd.DataFrame(dict(next_step_index=[8]*12+[np.nan],near_1c=[True]*13,cutoff_final_voltage_v=[2.6995]*12+[3.4]))
        rule=extraction.completion_rule(candidates)
        self.assertEqual(rule['completion_upper_voltage_v'],2.7)
        self.assertEqual(rule['positive_voltage_tolerance_v'],0.)
        self.assertEqual(rule['observed_other_endpoints_v'],[3.4])


if __name__=='__main__':unittest.main()
