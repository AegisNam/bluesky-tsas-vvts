#!/usr/bin/env python3
"""
Parse BlueSky command-window text (copied/exported) to compute simple KPIs for TSAS vs Baseline.

Expected to find lines containing: LAND <ACID>
and a timestamp at start of line like: 00:12:34.56 (or 00:12:34.56> ...)

Usage:
  python analyze_bluesky_landing.py baseline_log.txt tsas_log.txt

Outputs a small table of:
- landing count
- mean landing interval (s)
- std landing interval (s)
- mean landing time from sim start (s)
- TSAS RTA error stats if it finds an 'RTA <ACID> THR25R <hh:mm:ss>' line (optional)
"""
import re, sys, math
from statistics import mean, pstdev

TIME_RE = re.compile(r'(?P<t>\d\d:\d\d:\d\d(?:\.\d\d)?)')
LAND_RE = re.compile(r'\bLAND\s+(?P<acid>[A-Z0-9]+)\b')
RTA_RE  = re.compile(r'\bRTA\s+(?P<acid>[A-Z0-9]+)\s+\S+\s+(?P<rt>\d\d:\d\d:\d\d(?:\.\d\d)?)')

def to_seconds(hms: str) -> float:
    # hms can be HH:MM:SS or HH:MM:SS.xx
    parts = hms.split(':')
    hh = int(parts[0]); mm = int(parts[1])
    ss = float(parts[2])
    return hh*3600 + mm*60 + ss

def parse_file(path: str):
    land_times = {}  # acid -> time_s
    rta_times = {}   # acid -> rta_s
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            tm = TIME_RE.search(line)
            if not tm:
                continue
            t_s = to_seconds(tm.group('t'))
            lm = LAND_RE.search(line)
            if lm:
                acid = lm.group('acid')
                # keep first occurrence
                land_times.setdefault(acid, t_s)
            rm = RTA_RE.search(line)
            if rm:
                acid = rm.group('acid')
                rta_times[acid] = to_seconds(rm.group('rt'))
    return land_times, rta_times

def summarize(label: str, land_times: dict, rta_times: dict | None = None):
    acids = sorted(land_times.keys(), key=lambda a: land_times[a])
    times = [land_times[a] for a in acids]
    intervals = [times[i]-times[i-1] for i in range(1, len(times))]
    print(f"\n=== {label} ===")
    print(f"Landings: {len(times)}")
    if intervals:
        print(f"Mean landing interval: {mean(intervals):.1f} s")
        print(f"Std landing interval:  {pstdev(intervals):.1f} s")
    if times:
        print(f"Mean landing time from start: {mean(times):.1f} s")
    if rta_times:
        # compute error only for flights with both
        errs = []
        for a, lt in land_times.items():
            if a in rta_times:
                errs.append(lt - rta_times[a])
        if errs:
            print(f"RTA error (actual - planned): mean {mean(errs):.1f} s, std {pstdev(errs):.1f} s, max {max(errs):.1f} s, min {min(errs):.1f} s")

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_bluesky_landing.py baseline_log.txt tsas_log.txt")
        sys.exit(2)
    base_land, _ = parse_file(sys.argv[1])
    tsas_land, tsas_rta = parse_file(sys.argv[2])

    summarize("BASELINE", base_land, None)
    summarize("TSAS", tsas_land, tsas_rta)

    # Simple delta
    if base_land and tsas_land:
        base_times = sorted(base_land.values())
        tsas_times = sorted(tsas_land.values())
        # compare spacing stability
        def spacing_stats(times):
            ints=[times[i]-times[i-1] for i in range(1,len(times))]
            return (mean(ints), pstdev(ints)) if ints else (float('nan'), float('nan'))
        bmu,bsd=spacing_stats(base_times)
        tmu,tsd=spacing_stats(tsas_times)
        print("\n=== DELTA (TSAS - BASELINE) ===")
        if not math.isnan(bsd) and not math.isnan(tsd):
            print(f"Landing interval std change: {tsd-bsd:+.1f} s (negative = more stable)")
        if not math.isnan(bmu) and not math.isnan(tmu):
            print(f"Mean landing interval change: {tmu-bmu:+.1f} s")

if __name__ == "__main__":
    main()
