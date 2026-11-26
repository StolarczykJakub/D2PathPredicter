"""Validate and score manual D2R automap annotations entirely offline."""

import argparse
import json
from pathlib import Path
import platform
import sys
from time import perf_counter_ns

from .dataset import FILES, load_dataset
from .evaluate import percentile, run
from .predict import predict


def peak_working_set():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("size", wintypes.DWORD), ("faults", wintypes.DWORD),
                ("peak", ctypes.c_size_t), ("working_set", ctypes.c_size_t),
                ("other_counters", ctypes.c_size_t * 6),
            ]

        get_process = ctypes.WinDLL("kernel32").GetCurrentProcess
        get_process.restype = wintypes.HANDLE
        get_info = ctypes.WinDLL("psapi").GetProcessMemoryInfo
        get_info.argtypes = (wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD)
        get_info.restype = wintypes.BOOL
        counters = Counters(size=ctypes.sizeof(Counters))
        if get_info(get_process(), ctypes.byref(counters), counters.size):
            return counters.peak
        return None
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return peak if sys.platform == "darwin" else peak * 1024
    return None


def profile_predictions(cases):
    timings = {}
    for method in ("entrance", "geometry"):
        for model, obs in cases:
            predict(model, obs, method)
        samples = []
        for _ in range(25):
            for model, obs in cases:
                start = perf_counter_ns()
                predict(model, obs, method)
                samples.append((perf_counter_ns() - start) / 1_000_000)
        timings[method] = {
            "samples": len(samples),
            "p50_ms": percentile(samples, 0.5),
            "p95_ms": percentile(samples, 0.95),
            "max_ms": max(samples),
        }
    return timings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="check the annotation files and layout split")
    validate.add_argument("dataset", type=Path)
    benchmark = commands.add_parser("benchmark", help="evaluate directions per target and checkpoint")
    benchmark.add_argument("dataset", type=Path)
    benchmark.add_argument("--development", action="store_true", help="replay development by leaving one layout out")
    benchmark.add_argument("--shuffle-training", action="store_true", help="run the fixed-seed negative control")
    benchmark.add_argument("--profile", action="store_true", help="include measured runtime and peak memory")
    benchmark.add_argument("--output", type=Path, help="write the JSON report to a file")
    args = parser.parse_args(argv)
    try:
        start = perf_counter_ns()
        dataset = load_dataset(args.dataset)
        load_ms = (perf_counter_ns() - start) / 1_000_000
        if args.command == "validate":
            print(f"{dataset.dataset_id} [{dataset.kind}]: {len(dataset.splits)} layouts, {len(dataset.frames)} frames")
            return 0
        if args.output and args.output.resolve() in {(args.dataset / name).resolve() for name in FILES}:
            parser.error("report path would overwrite a dataset input")
        report, fit_ms, cases = run(dataset, development=args.development, shuffle=args.shuffle_training)
        if args.profile:
            report["profile"] = {
                "platform": platform.platform(), "python": platform.python_version(),
                "load_validate_ms": load_ms, "fit_ms": fit_ms,
                "warm_prediction": profile_predictions(cases),
                "peak_working_set_bytes": peak_working_set(),
            }
        result = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(result, encoding="utf-8")
        else:
            print(result, end="")
        return 0
    except (ValueError, OSError) as error:
        print(f"Dataset or report error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
