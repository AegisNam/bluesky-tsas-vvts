"""TSAS Simple Plugin for BlueSky
Author: Aegis Nam (adapted)

Simple, easy-to-read TSAS logic for teaching/demo purposes:
 - estimate ETA to a target point
 - sequence by ETA and assign STA using time separation
 - apply simple speed control to absorb small delays

This plugin intentionally keeps the logic simple and self-contained
so students can read and modify it.
"""

from math import radians, sin, cos, sqrt, atan2
from bluesky import traf, stack

# =========================
# CONFIG
# =========================

TARGET_LAT = 10.75     # target point (runway threshold / merge point)
TARGET_LON = 106.65

SEPARATION_S = 90.0    # time separation (seconds)
MIN_SPEED_KTS = 180.0
MAX_SPEED_KTS = 250.0

# Toggle verbose logging from the plugin
VERBOSE = False


def haversine_nm(lat1, lon1, lat2, lon2):
    """Return great-circle distance in nautical miles between two lat/lon points."""
    R = 6371e3  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    meters = R * c
    return meters / 1852.0


def compute_eta_seconds(ac_lat, ac_lon, speed_ms, tgt_lat=TARGET_LAT, tgt_lon=TARGET_LON):
    """Estimate ETA (seconds) from current position to target using ground speed (m/s).

    Returns a large number if speed is zero to deprioritize stationary aircraft.
    """
    if speed_ms <= 0.1:
        return 1e9
    dist_nm = haversine_nm(ac_lat, ac_lon, tgt_lat, tgt_lon)
    # convert speed m/s to knots: 1 m/s = 1.943844 knots
    speed_kts = speed_ms * 1.943844
    if speed_kts <= 0:
        return 1e9
    # time in seconds = (distance_nm / speed_kts) * 3600
    return (dist_nm / speed_kts) * 3600.0


def sequence_by_eta(ac_list):
    return sorted(ac_list, key=lambda x: x['eta_s'])


def assign_sta_seconds(sorted_list, separation_s=SEPARATION_S):
    for i, ac in enumerate(sorted_list):
        if i == 0:
            ac['sta_s'] = ac['eta_s']
        else:
            prev = sorted_list[i - 1]
            ac['sta_s'] = max(ac['eta_s'], prev['sta_s'] + separation_s)


def compute_new_speed_kts(ac):
    """Simple proportional speed control based on time delta (sta - eta).

    Returns new speed in knots (clamped).
    Positive delta -> need to slow down (reduce speed). Negative -> speed up.
    """
    delta = ac['sta_s'] - ac['eta_s']
    current = ac['speed_kts']

    # small tolerance: no change
    if abs(delta) < 5.0:
        return current

    # if positive delta => need to absorb delay => slow down
    if delta > 0:
        # reduce up to 15% depending on delta, limited to MIN_SPEED_KTS
        factor = max(0.85, 1.0 - min(delta / 180.0, 0.15))
        new = current * factor
    else:
        # negative delta (aircraft late) => speed up modestly
        factor = 1.0 + min(abs(delta) / 180.0, 0.1)
        new = current * factor

    # clamp
    new = max(MIN_SPEED_KTS, min(MAX_SPEED_KTS, new))
    return new


def update():
    """Main update called by BlueSky plugin loop.

    Collects traffic from bluesky.traf, computes ETA/STA and applies simple speed control.
    """
    if traf.ntraf == 0:
        return

    ac_list = []

    # collect basic data from BlueSky traffic arrays
    for i in range(traf.ntraf):
        eta = compute_eta_seconds(traf.lat[i], traf.lon[i], traf.tas[i])
        # store speed in knots for easier logic
        speed_kts = traf.tas[i] * 1.943844

        ac_list.append({
            'id': traf.id[i],
            'index': i,
            'eta_s': eta,
            'speed_kts': speed_kts,
        })

    # sequencing and scheduling
    sorted_list = sequence_by_eta(ac_list)
    assign_sta_seconds(sorted_list)

    # apply speed adjustments
    for ac in sorted_list:
        new_kts = compute_new_speed_kts(ac)
        # convert knots back to m/s for BlueSky
        new_ms = new_kts / 1.943844
        traf.tas[ac['index']] = new_ms

        if VERBOSE:
            print(f"{ac['id']} idx={ac['index']} ETA={ac['eta_s']:.1f}s STA={ac['sta_s']:.1f}s SPD={new_kts:.1f}kts")


def init_plugin():
    stack.stack('ECHO TSAS SIMPLE ACTIVE')
    if VERBOSE:
        print('TSAS SIMPLE PLUGIN LOADED (verbose)')
