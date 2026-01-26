# TSAS Simulation for TMA Tan Son Nhat (VVTS)

This repository contains BlueSky fast-time simulation scenarios
used to evaluate the applicability of Terminal Sequencing and
Spacing System (TSAS) at Tan Son Nhat TMA.

## Contents
- VVTS_BASELINE_LOG.scn: Baseline scenario without TSAS
- VVTS_TSAS_LOG.scn: TSAS scenario using RTA-based metering
- analyze_bluesky_landing.py: Script to compute landing spacing metrics

## How to run
1. Open BlueSky
2. Load scenario:
   IC VVTS_BASELINE_LOG.scn
   or
   IC VVTS_TSAS_LOG.scn
3. Run simulation:
   OP
   FF

## Application
This simulation supports an academic study on congestion mitigation
and arrival flow management in TMA Tan Son Nhat.
