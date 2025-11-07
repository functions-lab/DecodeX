#
# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import pytest

import numpy as np
from sionna.phy.fec.ldpc.encoding import LDPC5GEncoder
import ldpc_decoder
import time
import csv
from statistics import median
import os, csv

def _append_csv(csv_path, rows):
    if not csv_path or not rows: return
    fieldnames = list(rows[0].keys())
    write_header = (not os.path.exists(csv_path)) or (os.path.getsize(csv_path) == 0)
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header: w.writeheader()
        w.writerows(rows)

################################################################################
# Test against sionna encoder for different code parameters
# The decoder must be able to correctly reconstruct the encoded message
################################################################################


def _measure_decode_us(fn, repeats=10, warmup=3):
    """Time a no-arg callable. Returns list of durations in microseconds."""
    # Warmup
    for _ in range(warmup):
        fn()
    times_us = []
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        fn()
        t1 = time.perf_counter_ns()
        times_us.append((t1 - t0) / 1000.0)  # µs
    return times_us

def _summ_stats(us_list):
    us_list_sorted = sorted(us_list)
    n = len(us_list_sorted)
    p95 = us_list_sorted[int(0.95 * (n - 1))]
    return {
        "n": n,
        "mean_us": sum(us_list_sorted) / n,
        "median_us": median(us_list_sorted),
        "p95_us": p95,
        "min_us": us_list_sorted[0],
        "max_us": us_list_sorted[-1],
    }

print("test............")
all_Z_vals = np.array([  2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,
                        15,  16,  18,  20,  22,  24,  26,  28,  30,  32,  36,  40,  44,
                        48,  52,  56,  60,  64,  72,  80,  88,  96, 104, 112, 120, 128,
                       144, 160, 176, 192, 208, 224, 240, 256, 288, 320, 352, 384])

@pytest.mark.parametrize("Z", all_Z_vals)
def test_decoder(Z, pytestconfig, num_iter=None, llr_mag=None,
                 fast_testing=None, quiet=None):
    # ... existing option extraction ...
    timing = False
    repeats = 15
    csv_path = ""
    if pytestconfig is not None:
        timing = pytestconfig.getoption("timing")
        repeats = pytestconfig.getoption("repeats")
        csv_path = pytestconfig.getoption("csv") or ""
    if pytestconfig is not None:
        if num_iter is None:
            num_iter = pytestconfig.getoption('iters')
        if llr_mag is None:
            llr_mag = pytestconfig.getoption('llrmag')
        fast_testing = pytestconfig.getoption('fast')
        quiet = not pytestconfig.getoption('verbose')

    if not quiet: print(f'Start testing: {num_iter} iterations, LLR magnitude {llr_mag}')
    print(f'Start testing: {num_iter} iterations, LLR magnitude {llr_mag}')

    csv_rows = []

    kb = np.array([10,22]) if fast_testing else np.array([6,8,9,10,22])

    k_vals = np.sort(np.outer(np.array([Z]), kb).flatten())
    print("k vals are: ")
    print(k_vals)
    rates =  [.2,.34,.5,.66,.75,.88]

    total_test = 0
    for k in k_vals:
        for r in rates:
            n = int(np.ceil(k/r))
            r_actual = k / n
            if k <= 292 or (k <= 3824 and r_actual <= 2/3) or r_actual <= 1/4:
                BG = 2
            else:
                BG = 1
            # exclude the cases that are not supported in the standard
            if BG == 1 and (r_actual > 11/12 or r_actual < 1/3): continue
            if BG == 2 and (r_actual > 10/12 or r_actual < 1/5 or k >= 3824): continue

            enc = LDPC5GEncoder(k, n)
            BG_sionna = 1 if enc._bg == "bg1" else 2
            assert BG_sionna == BG

            u = np.random.randint(0,2,k)
            c = enc(np.expand_dims(u.astype(np.float64),0))[0].numpy()
            x = 1-2*c

            llr_ch = np.clip((llr_mag * x),-127,127).astype(np.int8)

            Zc = enc._z
            BG = 1 if enc._bg == "bg1" else 2
            num_vn = 68*Zc if BG == 1 else 52*Zc
            parity_start = 22*Zc if BG == 1 else 10*Zc


            if not quiet: print(f'K = {k:4}, N = {n:5}, BG = {BG:1}, Z = {Zc:3}... ', end='', flush=True )

            llr_input = np.zeros(num_vn,dtype=np.int8) # takes care of the punctured bits (initialized to 0 LLR)
            llr_input[2*Zc:k] =  llr_ch[:k-2*Zc] # unpunctured message bits
            llr_input[k:parity_start] = 127      # shortened bits
            llr_input[parity_start:parity_start+n-k+2*Zc] = llr_ch[k-2*Zc:] # parity bits
            
            print(f'BG = {BG:1}, Zc = {Zc:3}, K = {k:4}, iter = {num_iter}')

             # === Timing just the decode() call ===
            if timing:
                # Use a closure to avoid measuring argument setup
                def _decode_call():
                    ldpc_decoder.decode(BG, Zc, llr_input, k, num_iter)

                us_list = _measure_decode_us(_decode_call, repeats=repeats, warmup=3)
                stats = _summ_stats(us_list)
                us_per_bit = stats["median_us"] / k
                if not quiet:
                    print(f"  decode median: {stats['median_us']:.2f} µs "
                          f"(mean {stats['mean_us']:.2f}, p95 {stats['p95_us']:.2f}), "
                          f"~{us_per_bit:.4f} µs/bit")
                if csv_path:
                    csv_rows.append({
                        "BG": BG,
                        "Zc": Zc,
                        "K": k,
                        "N": n,
                        "rate": f"{k/n:.6f}",
                        "iters": num_iter,
                        "repeats": repeats,
                        "median_us": f"{stats['median_us']:.3f}",
                        "mean_us": f"{stats['mean_us']:.3f}",
                        "p95_us": f"{stats['p95_us']:.3f}",
                        "min_us": f"{stats['min_us']:.3f}",
                        "max_us": f"{stats['max_us']:.3f}",
                        "us_per_bit_med": f"{(stats['median_us']/k):.6f}",
                    })
        
            decoder_outputs = ldpc_decoder.decode(BG, Zc, llr_input, k, num_iter)
            total_test = total_test + 1

            u_hat = np.unpackbits(decoder_outputs.astype(np.uint8))[:k] # there may be a couple of extra bits if k is not a multiple of 8
            if np.all(u == u_hat):
                if not quiet: print('Check')
            else:
                if not quiet: print('Failed')
                raise AssertionError(f'Decoder output is incorrect for K = {k}, N = {n}, BG = {BG}, Z = {Zc}')
    

    # Write CSV if requested
    if csv_path and timing and csv_rows:
        _append_csv(csv_path, csv_rows)


    print("total num of tests are: ")
    print(total_test)

    if not quiet: print('done')
