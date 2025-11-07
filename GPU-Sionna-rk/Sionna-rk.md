### Using Sionna-rk for Private 5G LDPC Testing (GPU on Jetson Orin AGX)

Follow NVIDIA’s quick start guide to set up a private software-defined 5G network with **Sionna Research Kit (sionna-rk)**:  
https://nvlabs.github.io/sionna/rk/quickstart.html

> **GPU requirement:** Running sionna-rk with GPU acceleration requires an **NVIDIA Jetson Orin AGX** device.

---

#### 1) Build sionna-rk
Follow the steps in the quick start link above to install prerequisites and build the project successfully.

---

#### 2) Navigate to the LDPC CUDA tests
After a successful build, go to:

    ~/sionna-rk/tutorials/ldpc_cuda/test

This folder contains example unit tests for LDPC.

---

#### 3) Drop-in enhanced test files
To extend functionality, we provide updated versions of the following:

- `conftest.py`
- `run_bler_test.py`
- `run_decoder_test.py`
- `run_tests.sh` (executable wrapper)

Place these files into:

    ~/sionna-rk/tutorials/ldpc_cuda/test

(Overwrite the existing files if prompted.)

---

#### 4) Test parameters (pytest CLI)
Our `conftest.py` exposes the following options:

    def pytest_addoption(parser):
        parser.addoption("--fast", action="store_true", default=False, help="Run fewer tests")
        parser.addoption("-I", "--iters", type=int, default=8, help="Number of decoder iterations")
        parser.addoption("-L", "--llrmag", type=int, default=32, help="LLR magnitude value")
        parser.addoption("-T", "--trials", type=int, default=1000, help="Number of monte carlo trials")
        parser.addoption("--timing", action="store_true", default=False, help="Measure decode timing.")
        parser.addoption("--repeats", type=int, default=15, help="Timing repeats per case.")
        parser.addoption("--csv", type=str, default="", help="Optional CSV path for timing rows.")

**Common examples:**

- Quick functional run (reduced coverage):
  
      pytest -q run_decoder_test.py --fast

- Increase decoder iterations and trials:
  
      pytest -q run_decoder_test.py --iters 16 --repeats 20000

- Measure timing with repeats and save CSV:
  
      pytest -q run_decoder_test.py --timing --repeats 20 --csv results_ldpc_timing.csv

- Sweep with custom LLR magnitude:
  
      pytest -q run_decoder_test.py --llrmag 48 --iters 10 --repeats 5000

---

#### 5) One-shot test runner
Use the provided executable wrapper to run a curated set of LDPC tests:

    ./run_tests.sh

**Notes:**
- `--csv` writes timing rows (one per case) to the specified file.
- `--timing` enables decode latency measurement; `--repeats` controls micro-benchmark loop count.
- GPU usage depends on your sionna-rk build and runtime environment on **Jetson Orin AGX**.

---

#### 6) Troubleshooting tips
- Ensure your environment matches the quick start’s CUDA/cuBLAS/cuDNN and driver guidance.
- If `pytest` cannot find tests, confirm you are in:
  
      ~/sionna-rk/tutorials/ldpc_cuda/test

- If GPU is not used, verify the Jetson build, drivers, and that TensorFlow/JAX (as applicable) detect CUDA.

---

This section lets you quickly validate and benchmark LDPC (CPU/GPU) inside sionna-rk, with convenient flags for **iterations**, **LLR magnitude**, **Monte-Carlo trials**, and **timing**/CSV logging.

