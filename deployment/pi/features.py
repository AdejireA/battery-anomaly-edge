"""Streaming implementation of the frozen NASA prior-ten-cycle definition."""
from collections import deque
import numpy as np

BASE_FEATURES = (
    'duration_s', 'time_to_3_4v_s', 'mean_voltage_v', 'mean_current_a',
    'mean_temp_c', 'max_temp_c', 'delta_temp_c',
)
HISTORY = 10
FEATURE_NAMES = tuple(f'{name}_prior10_robust_residual' for name in BASE_FEATURES)
MAD_SCALE = 1.4826
EPSILON = 1e-9


def relative_vector(current, history):
    """History contains exactly ten PRIOR rows, never current or future rows."""
    prior = np.asarray(history, dtype=np.float64)
    current = np.asarray(current, dtype=np.float64)
    if prior.shape != (HISTORY, len(BASE_FEATURES)) or current.shape != (len(BASE_FEATURES),):
        raise ValueError('Expected ten prior rows and seven ordered measurements')
    if not np.isfinite(prior).all() or not np.isfinite(current).all():
        raise ValueError('Nonfinite measurements are not imputed')
    median = np.median(prior, axis=0)
    mad = np.median(np.abs(prior - median), axis=0)
    result = (current - median) / (MAD_SCALE * mad + EPSILON)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite relative feature')
    return result


class CausalHistory:
    """Independent state per cell; caller supplies strictly consecutive cycles."""
    def __init__(self):
        self.history = {}
        self.last_cycle = {}

    def push(self, row):
        cell = row.get('cell_id', '__single_cell__')
        if cell is None or not str(cell).strip():
            raise ValueError('Blank cell_id is not allowed')
        cell = str(cell)
        try:
            cycle = int(str(row['cycle']))
            current = np.array([float(row[name]) for name in BASE_FEATURES], dtype=np.float64)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('Missing/invalid cycle or required measurement') from exc
        if cycle < 1 or not np.isfinite(current).all():
            raise ValueError('Cycle must be positive; measurements must be finite')
        if cell in self.last_cycle and cycle != self.last_cycle[cell] + 1:
            raise ValueError(f'{cell}: duplicate, reversed or missing cycle; expected {self.last_cycle[cell] + 1}')
        history = self.history.setdefault(cell, deque(maxlen=HISTORY))
        vector = relative_vector(current, history) if len(history) == HISTORY else None
        # Compute BEFORE appending current observation.
        history.append(current)
        self.last_cycle[cell] = cycle
        return cell, cycle, vector
