# DecodeX Exploring and Benchmarking of LDPC Decoding across CPU, GPU, and ASIC Platforms

This repository presents DecodeX, a unified benchmarking framework for evaluating low-density parity-check (LDPC) decoding acceleration across different hardware platforms. DecodeX integrates a comprehensive suite of LDPC decoder implementations, including kernels, APIs, and test vectors for CPUs (FlexRAN), GPUs (Aerial and Sionna-RK), and ASIC (ACC100), and can be readily extended to additional architectures and configurations.

Current supported benchmarking frameworks consists of the following: 

|    Hardware      |        Implementation        |         Platform        |
| ---------------- | -----------------------------|-------------------------|
|     CPU          |            [FlexRAN](CPU-FlexRAN/CPU-FlexRAN-README.md)           |        Intel Xeon       |
|     CPU          |            OAI               |        Intel Xeon       |
|     ASIC         |            DPDK-BBDev        |        ACC100           |
|     GPU          |            Sionna-rk         |     Jetson AGX Orin     |
|     GPU          |            Aerial            |           H200          |
|     GPU          |            Aerial            |        RTX 3090         |
|     GPU          |            Aerial            |      RTX 6000 Ada       |

