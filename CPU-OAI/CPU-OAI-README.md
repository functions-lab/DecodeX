### Using OAI (OpenAirInterface) for LDPC Testing

If installing FlexRAN and its dependencies is inconvenient, an alternative is to use the open-source **OpenAirInterface (OAI)** platform to test 5G NR LDPC decoding performance.

OAI Repository:  
https://gitlab.eurecom.fr/oai/openairinterface5g

---

#### 1. Install OAI

Follow the official installation instructions in the OAI repository.  
Make sure NR components (gNB / UE) and required dependencies are installed.

---

#### 2. Build OAI with LDPC Test Support

Run the following:

    cd ~/openairinterface5g/cmake_targets
    ./build_oai -w USRP --ninja --nrUE --gNB --build-lib "nrscope" -c

This builds OAI with NR LDPC libraries and includes the LDPC test binary.

---

#### 3. Locate the `ldpctest` Executable

After compilation, the binary will be located at:

    ~/openairinterface5g/cmake_targets/ran_build/build/ldpctest

You should also see the LDPC shared library:

    libldpc.so

---

#### 4. Display Help and Usage

    cd ~/openairinterface5g/cmake_targets/ran_build/build
    ./ldpctest -h

Example help output (key fields):

    CURRENTLY SUPPORTED CODE RATES:
      BG1 (K' > 3840): 1/3, 2/3, 22/25 (~8/9)
      BG2 (K' ≤ 3840): 1/5, 1/3, 2/3

    Options:
      -h  Show help
      -q  Quantization bits (default: 8)
      -r  Rate numerator (1, 2, 22) (default: 1)
      -d  Rate denominator (3, 5, 25) (default: 3)
      -l  Payload length K' [1–8448] (default: 8448)
      -G  Enable CUDA/GPU decoder (1 = GPU, default: 0 = CPU)
      -n  Number of simulation trials (default: 1)
      -s  Eb/N0 in dB (default: -2)
      -S  Number of segments (max: 8, default: 1)
      -t  SNR sweep step (default: 0.1)
      -i  Max decoder iterations (default: 5)
      -u  Interpret SNR as per coded bit (default: 0)
      -v  Select LDPC shared library version (uses libldpc_<version>.so)

---

#### 5. Example Usage

**Run LDPC decoding on CPU:**

    ./ldpctest

**Run LDPC decoding on GPU (requires CUDA-enabled build):**

    ./ldpctest -G 1

You can vary parameters (e.g., `-l`, `-r`, `-d`, `-s`, `-i`) to test different block sizes, code rates, SNR levels, and iteration limits.

---

This provides a clean and lightweight alternative to FlexRAN for evaluating NR LDPC decoding performance on both **CPU** and **GPU** platforms.

