#
# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--fast", action="store_true", default=False, help="Run fewer tests")
    parser.addoption('-I', '--iters', type=int, default=8, help="Number of decoder iterations")
    parser.addoption('-L', '--llrmag', type=int, default=32, help="LLR magnitude value")
    parser.addoption('-T', '--trials', type=int, default=1000, help="Number of monte carlo trials")
    parser.addoption("--timing", action="store_true", default=False, help="Measure decode timing.")
    parser.addoption("--repeats", type=int, default=15, help="Timing repeats per case.")
    parser.addoption("--csv", type=str, default="", help="Optional CSV path for timing rows.")
