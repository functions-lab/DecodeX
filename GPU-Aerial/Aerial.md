### NVIDIA AI Aerial (pyAerial) for LDPC Testing

NVIDIA **AI Aerial** requires an NVIDIA Developer account to access the SDK and related resources.  
Please request access here:  
https://developer.nvidia.com/industries/telecommunications/ai-aerial

---

#### Version Tested
(Please fill these based on your setup)
- AI Aerial Version Tested: aerial-cuda-accelerated-ran:25-2-cubb
- CUDA Version: 13.0
- NVIDIA Driver Version: 580.65.06 
- OS / Platform: Ubuntu 24.04.3 LTS

---

#### Using pyAerial

We use **pyAerial** for a more convenient Python-based LDPC testing workflow:

pyAerial Getting Started:  
https://docs.nvidia.com/aerial/cuda-accelerated-ran/latest/pyaerial/getting_started.html

Example LDPC coding notebook:  
https://docs.nvidia.com/aerial/cuda-accelerated-ran/latest/content/notebooks/example_ldpc_coding.html

Follow the “Getting Started” guide to complete the environment setup. Once pyAerial is installed, open the LDPC example notebook and modify the parameters as shown below.

---

#### Example Parameter Configuration (edit directly inside the LDPC example)

    num_slots = 10000
    min_num_tb_errors = 250

    # Numerology and frame structure (TS 38.211)
    num_prb = 100              # Number of allocated PRBs (affects TB size and rate-matching)
    start_sym = 0              # PDSCH start symbol
    num_symbols = 14           # Symbols per slot
    num_slots_per_frame = 20   # Slots per frame
    num_layers = 1
    dmrs_sym = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]

    # Rate matching includes scrambling if True
    enable_scrambling = True

    # Scrambling init based on RNTI and data scrambling ID (TS 38.211)
    rnti = 20000
    data_scid = 41
    cinit = (rnti << 15) + data_scid

    # Redundancy version / MCS (TS 38.214)
    rv = 0
    mcs = 9

    # Derive modulation order and code rate
    mod_order, code_rate = get_mcs(mcs)
    code_rate /= 1024.0

This configuration impacts the decoded transport block size, BLER performance curves, and SNR ranges to test.

---

#### Decoding Mode Notes

The provided pyAerial LDPC example performs **single-stream decoding**, meaning transport blocks (TBs) are decoded **sequentially**.

To perform **parallel decoding of multiple TBs simultaneously**, please contact the **DecodeX** author for integration support, as that functionality is outside the scope of the default pyAerial notebook.

---

#### Troubleshooting Tips

- Ensure your NVIDIA Developer access is approved, otherwise documentation/software links may appear restricted.
- Verify CUDA toolkit, GPU drivers, and pyAerial version compatibility.
- If GPU acceleration does not activate, confirm your environment is running on a supported platform (e.g., NVIDIA Jetson Orin AGX for embedded setups).
- Adjust SNR sweep ranges when changing `mcs` or `code_rate` to ensure meaningful BLER curves.

---

