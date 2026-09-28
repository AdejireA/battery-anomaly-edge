"""Repeat immutable playback contexts; never benchmark fitting or change history."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
import platform
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone
from infer import FrozenRunner, HERE, read_rows
from features import BASE_FEATURES, HISTORY, CausalHistory, relative_vector
import numpy as np


def memory():
    """Bytes: psutil RSS preferred, native counters when psutil is unavailable."""
    rss = peak = None
    method = []
    try:
        import psutil
        info = psutil.Process().memory_info()
        rss = info.rss
        peak = getattr(info, 'peak_wset', None)
        method.append('psutil')
    except ImportError:
        pass
    if os.name == 'nt' and (rss is None or peak is None):
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in ['PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
                 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage']]
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        api = ctypes.WinDLL('psapi', use_last_error=True)
        api.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        counter = Counters(); counter.cb = ctypes.sizeof(counter)
        if api.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counter), counter.cb):
            rss, peak = counter.WorkingSetSize, counter.PeakWorkingSetSize
            method.append('Windows GetProcessMemoryInfo')
    if sys.platform.startswith('linux'):
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        if rss is None:
            rss = int(Path('/proc/self/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
        method.append('Linux ru_maxrss/proc')
    return dict(rss_bytes=rss, peak_rss_bytes=peak, method='; '.join(method) or 'unavailable')


def stats(seconds):
    a = np.asarray(seconds) * 1000
    return dict(mean_ms=float(a.mean()), median_ms=float(np.median(a)), std_ms=float(a.std(ddof=1)),
                p95_ms=float(np.percentile(a, 95)), p99_ms=float(np.percentile(a, 99)), min_ms=float(a.min()), max_ms=float(a.max()))


def contexts(rows):
    state = CausalHistory()
    output = []
    for row in rows:
        cell = str(row.get('cell_id', '__single_cell__'))
        prior = np.array(state.history.get(cell, []), dtype=float)
        _, _, vector = state.push(row)
        if vector is not None:
            output.append((np.array([float(row[b]) for b in BASE_FEATURES]), prior))
    if not output:
        raise ValueError('No observations with ten prior cycles')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--repeats', type=int, default=1000)
    parser.add_argument('--warmup', type=int, default=100)
    parser.add_argument('--output-prefix', type=Path, default=HERE / 'results/pi_benchmark')
    parser.add_argument('--label', default='device measurement; identify hardware from platform fields')
    parser.add_argument('--load-probe', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.load_probe:
        begin = time.perf_counter(); FrozenRunner()
        print(json.dumps({'cold_load_seconds': time.perf_counter() - begin}))
        return
    if not args.input or args.repeats < 1000 or args.warmup < 1:
        parser.error('--input is required; --repeats must be >=1000; --warmup >=1')
    start = time.perf_counter()
    probe = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--load-probe'], check=True, capture_output=True, text=True)
    startup = time.perf_counter() - start
    cold = json.loads(probe.stdout)
    runner = FrozenRunner()
    examples = contexts(list(read_rows(args.input)))
    for i in range(args.warmup):
        current, history = examples[i % len(examples)]
        runner.score_vector(relative_vector(current, history))
    before = memory()
    feature_times, model_times, total_times = [], [], []
    cpu_start = os.times(); begin = time.perf_counter()
    for i in range(args.repeats):
        current, history = examples[i % len(examples)]
        t0 = time.perf_counter()
        vector = relative_vector(current, history)
        t1 = time.perf_counter()
        value = runner.score_vector(vector)
        prediction = 'ALERT' if value > runner.threshold else 'NORMAL'
        t2 = time.perf_counter()
        feature_times.append(t1 - t0); model_times.append(t2 - t1); total_times.append(t2 - t0)
    wall = time.perf_counter() - begin; cpu_end = os.times(); after = memory()
    artifacts = HERE / 'artifacts'
    sizes = {p.name: p.stat().st_size for p in artifacts.iterdir() if p.is_file()}
    result = dict(label=args.label, timestamp_utc=datetime.now(timezone.utc).isoformat(),
        platform=platform.platform(), machine=platform.machine(), processor=platform.processor(), python=sys.version,
        logical_cpus=os.cpu_count(), dependencies=__import__('infer').EXPECTED_VERSIONS,
        repeats=args.repeats, warmup=args.warmup, distinct_playback_contexts=len(examples),
        cold_load_seconds=cold['cold_load_seconds'], cold_process_startup_seconds=startup,
        cold_definition='Fresh subprocess; load includes hash checks, sklearn imports and deserialization. OS disk cache is not flushed. Full startup additionally includes interpreter and base imports.',
        feature_computation=stats(feature_times), model_inference=stats(model_times), combined=stats(total_times),
        wall_seconds=wall, throughput_observations_per_second=args.repeats / wall,
        cpu_percent_one_core=100 * ((cpu_end.user + cpu_end.system) - (cpu_start.user + cpu_start.system)) / wall,
        memory_before=before, memory_after=after, artifact_sizes_bytes=sizes,
        timing_scope='One observation at a time; feature arithmetic, scaler.transform, score_samples and threshold comparison. CSV I/O/context preparation excluded. Repeat isolated pre-recorded histories; do not feed replayed observations into a continuing live history.',
        power_consumption='Not measured', no_training=True)
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    args.output_prefix.with_suffix('.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    lines = [f'NASA edge benchmark: {args.label}', f'Hardware: {result["platform"]} / {result["machine"]}',
             f'Fresh-process artifact load: {cold["cold_load_seconds"]:.6f} s; full process startup: {startup:.6f} s',
             f'Warm calls: {args.repeats}; warm-up: {args.warmup}',
             'Feature computation (ms): ' + json.dumps(result['feature_computation']),
             'Model inference (ms): ' + json.dumps(result['model_inference']),
             'Combined latency (ms): ' + json.dumps(result['combined']),
             f'Throughput: {result["throughput_observations_per_second"]:.3f} observations/s',
             f'Process CPU (100% = one logical core): {result["cpu_percent_one_core"]:.2f}%',
             'Memory after: ' + json.dumps(after), 'Artifact bytes: ' + json.dumps(sizes),
             result['cold_definition'], result['timing_scope'], 'Power consumption: not measured.']
    text = '\n'.join(lines) + '\n'
    args.output_prefix.with_suffix('.txt').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
