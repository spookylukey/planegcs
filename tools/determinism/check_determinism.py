#!/usr/bin/env python3
"""Measure reproducibility of the solver's output.

Builds the same sketch many times - in this process and, with --subprocess,
in fresh processes - and reports how many distinct answers came out.  Anything
above 1 means the result depends on the heap layout rather than the sketch.

    ./check_determinism.py 20 --nsides 100
    ./check_determinism.py 20 --nsides 100 --equal --recycle
    ./check_determinism.py 10 --mode diagnose --redundant
    ./check_determinism.py 10 --subprocess
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sensitive_sketch import Options, diagnose_result, digest, solve_result  # noqa: E402


def run_one(opts: Options, mode: str) -> list[float]:
    return solve_result(opts) if mode == "solve" else diagnose_result(opts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trials", type=int, nargs="?", default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--nsides", type=int, default=100)
    ap.add_argument("--mode", choices=["solve", "diagnose"], default="solve")
    ap.add_argument("--equal", action="store_true")
    ap.add_argument("--recycle", action="store_true")
    ap.add_argument("--redundant", action="store_true")
    ap.add_argument("--subprocess", action="store_true", help="one fresh process per trial")
    ap.add_argument("--emit", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    base = Options(
        nsides=args.nsides, equal=args.equal, recycle=args.recycle, redundant=args.redundant
    )

    if args.emit:
        base.churn = rng.randrange(0, 300)
        print(digest(run_one(base, args.mode)))
        return 0

    results: Counter[str] = Counter()
    values: dict[str, list[float]] = {}
    for trial in range(args.trials):
        if args.subprocess:
            cmd = [sys.executable, __file__, "1", "--emit", "--seed", str(rng.randrange(1 << 30))]
            cmd += ["--nsides", str(args.nsides), "--mode", args.mode]
            for flag in ("equal", "recycle", "redundant"):
                if getattr(args, flag):
                    cmd.append(f"--{flag}")
            d = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
            vals: list[float] = []
        else:
            junk = [bytearray(rng.randrange(1, 4096)) for _ in range(rng.randrange(0, 200))]
            base.churn = rng.randrange(0, 300)
            vals = run_one(base, args.mode)
            del junk
            d = digest(vals)
        results[d] += 1
        values[d] = vals
        del trial

    spread = 0.0
    if len(values) > 1 and all(values.values()):
        vs = list(values.values())
        spread = max(abs(a - b) for v in vs[1:] for a, b in zip(vs[0], v, strict=True))
    print(
        f"mode={args.mode} nsides={args.nsides} equal={args.equal} recycle={args.recycle} "
        f"redundant={args.redundant} subprocess={args.subprocess}: "
        f"trials={args.trials} distinct={len(results)} max spread={spread:.4g}"
    )
    if args.verbose:
        for d, n in results.most_common():
            print(f"  {d}  x{n}")
    return 0 if len(results) == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
