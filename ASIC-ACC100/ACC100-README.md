## DPDK installation
  * [DPDK](http://core.dpdk.org/download/) version 21.11.1 lts
    Intel 40 GbE and Mellanox 100 GbE NICs in Agora.
  * It is required you enable hugepage support and run agora under sudo permissions (LD_LIBRARY_PATH=${LD_LIBRARY_PATH}).
    <pre>
    $ sudo sh -c "echo 4 > /sys/devices/system/node/node0/hugepages/hugepages-1048576kB/nr_hugepages"
    $ sudo sh -c "echo 4 > /sys/devices/system/node/node1/hugepages/hugepages-1048576kB/nr_hugepages"
    </pre>
    Make memory available for dpdk
    <pre>
    $ mkdir /mnt/huge
    $ mount -t hugetlbfs nodev /mnt/huge
    </pre>
    Check hugepage usage
    <pre>
    $ cat /proc/meminfo
    </pre>
    [Building] https://doc.dpdk.org/guides/linux_gsg/sys_reqs.html#building-dpdk-applications

  * Mellanox's DPDK support depends on libibverbs / libmlx5 / ibverbs-utils.
  * Intel NICs may require the user to bring down the interface and load a DPDK compatible driver (vfio / pci_generic)
  * To install version 21.11.1, run
    <pre>
    $ meson build && cd build && ninja
    $ sudo ninja install
    $ sudo ldconfig
    </pre>
    the MLX poll mode driver will be autodetected and installed if required
    
## ACC100 System requirements:
 * ACC100 requires PCI Express x16 slot. 
 * **NOTE** If you are trying to run virtual functions, please make sure BIOS is providing enough MMIO space.
 * **NOTE** Please make sure SR-IOV is enabled in BIOS: F2 BIOS > System BIOS > Integrated Devices > SR-IOV Global Enable
 * **NOTE** Please make sure the following is added to your GRUB settings:
   ```
    GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on amd_iommu=on quiet splash vfio-pci.ids=ca:00.0 vfio_pci.enable_sriov=1 vfio_pci.disable_idle_d3=1 hugepage=64"
    GRUB_CMDLINE_LINUX="intel_iommu=on amd_iommu=on iommu=pt"
    
## ACC100 initialization:
 * We will present how to use igb_uio as the driver to drive ACC100
 * Download [dpdk-kmods](http://git.dpdk.org/dpdk-kmods/commit/?id=e721c733cd24206399bebb8f0751b0387c4c1595). Please follow the instructions to install dpdk-dmods. 
   * To build igb_uio driver:
    ```
    $ cd <folder_location>/dpdk-kmods-e721c733cd24206399bebb8f0751b0387c4c1595/linux/igb_uio
    $ sudo make
    $ sudo modprove uio
    $ sudo insmod igb_uio.ko
    ```
* Identify ACC100 address, you can either use `lspci` or `dpdk-devbind.py --status`, example output is as follows:
   ```
   $ lspci 
   17:00.0 Processing accelerators: Intel Corporation Device 0d5c

   $ dpdk-devbind.py --status
   Baseband devices using Da PDK-compatible driver
   =============================================
   0000:17:00.0 'Device 0d5c' drv=igb_uio unused=vfio-pci
   ```
* Set up ACC100 by binding the driver to the device and updating the device:
  ```
  $ modprobe igb_uio
  # to make sure igb_uio is there
  $ lsmod 
  Module                  Size  Used by
  igb_uio                24576  0
  uio                    20480  1 igb_uio
  vtsspp                532480  0

  $ sudo dpdk-devbind.py -b igb_uio <ACC100_ADDR>
  $ echo <X> | sudo tee /sys/bus/pci/devices/<ACC100_ADDR>/max_vfs
  ```
  where X is the number of VFs you want to configure. In this tutorial, we provide the case with 16 VFs. 
* Configure the card using [pf_bb_config](https://github.com/intel/pf-bb-config).
  ```
  $ cd <pf_bb_config folder>
  $ sudo ./pf_bb_config ACC100 -c acc100/acc100_config_16vf_4g5g.cfg
  == pf_bb_config Version v23.03-0-gb27a4f8 ==
  More than one device found. Please select which device you would like to use from the list:
  [1]: 0000:17:00.0
  [2]: 0000:98:00.0
  > 1
  Tue Feb 25 20:28:30 2025:INFO:Queue Groups: 2 5GUL, 2 5GDL, 2 4GUL, 2 4GDL
  Tue Feb 25 20:28:30 2025:INFO:Configuration in VF mode
  Tue Feb 25 20:28:31 2025:INFO: ROM version MM 99AD92
  Tue Feb 25 20:28:31 2025:INFO:PF ACC100 configuration complete
  Tue Feb 25 20:28:31 2025:INFO:ACC100 PF [0000:17:00.0] configuration complete!
  ```
  We provide an example config file with acc100_config_16vf_4g5g.cfg in this repo.
  After pf-bb-config produces a configuration complete message, go ahead to set up the igb_uio driver for every VF.
  ```
  $ sudo dpdk-devbind.py -b igb_uio <ACC100_VF_ADDR>
  ```
* An example output for checking all configured VFs is as follows:
  ```
  dpdk-devbind.py --status
  Network devices using kernel driver
  ===================================
  0000:04:00.0 'NetXtreme BCM5720 2-port Gigabit Ethernet PCIe 165f' if=eno8303 drv=tg3 unused=igb_uio,vfio-pci *Active*
  0000:04:00.1 'NetXtreme BCM5720 2-port Gigabit Ethernet PCIe 165f' if=eno8403 drv=tg3 unused=igb_uio,vfio-pci 
  0000:31:00.0 'MT27800 Family [ConnectX-5] 1017' if=eno12399np0 drv=mlx5_core unused=igb_uio,vfio-pci 
  0000:31:00.1 'MT27800 Family [ConnectX-5] 1017' if=eno12409np1 drv=mlx5_core unused=igb_uio,vfio-pci 
  0000:ca:00.0 'MT27800 Family [ConnectX-5] 1017' if=ens7f0np0 drv=mlx5_core unused=igb_uio,vfio-pci 
  0000:ca:00.1 'MT27800 Family [ConnectX-5] 1017' if=ens7f1np1 drv=mlx5_core unused=igb_uio,vfio-pci 
  Baseband devices using DPDK-compatible driver
  =============================================
  0000:17:00.0 'Device 0d5c' drv=igb_uio unused=vfio-pci
  0000:18:00.0 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.1 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.2 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.3 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.4 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.5 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.6 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:00.7 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.0 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.1 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.2 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.3 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.4 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.5 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.6 'Device 0d5d' drv=igb_uio unused=vfio-pci
  0000:18:01.7 'Device 0d5d' drv=igb_uio unused=vfio-pci
  Other Baseband devices
  ======================
  0000:98:00.0 'Device 0d5c' unused=igb_uio,vfio-pci
  ```
  
## Running default validation test:
* Please quickly run the default validation test several times to make sure ALL ACC100 VFs work normally on your device:
  ```
  $ cd <dpdk_folder>/app/test-bbdev
  $ sudo dpdk-test-bbdev -c F0 -a <ACC100_VF_ADDR> -- -c validation -v ./ldpc_dec_default.data
  
  # You are expected to see the following, which indicates you passed the validation test:
  ===========================================================
  Starting Test Suite : BBdev Validation Tests
  Test vector file = ./ldpc_dec_default.data
  + ------------------------------------------------------- +
  == test: validation
  dev:18:00.0, burst size: 32, num ops: 64, op type: RTE_BBDEV_OP_LDPC_DEC
  Operation latency:
  	avg: 68312 cycles, 26.2738 us
  	min: 62482 cycles, 24.0315 us
  	max: 74142 cycles, 28.5162 us
  TestCase [ 0] : validation_tc passed
   + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
   + Test Suite Summary : BBdev Validation Tests
   + Tests Total :        1
   + Tests Skipped :      0
   + Tests Passed :       1
   + Tests Failed :       0
   + Tests Lasted :       51.9312 ms
   + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
  ```
  **NOTE** If the total elapsed time takes too long, please double check with your system settings

## Build own test case:
* You are able to also build your own testcases for your own program.
   * Please refer to BBDEV official [documents](https://doc.dpdk.org/guides/prog_guide/bbdev.html) and also 3GPP [protocol](https://www.etsi.org/deliver/etsi_ts/138200_138299/138212/15.02.00_60/ts_138212v150200p.pdf). Users may need to calculated some of the parameters manually, we will provide a tool to generate testcases automatically for users with provided coderate, modulation scheme and input size, this feature is **[coming up]**
* We have provided example testcases w.r.t different MCS in `mcs_enc_dec_pair`. Inside this folder, you will find:
   * encoding and decoding testcases for MCS10-MCS19 as an example {specifically for 5G mmWave FR2 Numeorology 3 100MHz}. 
   * A program called `test_bbdev_perf.c` based on DPDK's bbdev program.
   * To test encoding:
      ```
      $ sudo dpdk-test-bbdev -c F0 -a <ACC100_ADDR> -- -c validation -n 1 -b 1 -l 1 -v <folder>/mcs_enc_dec_pair/mcs<x>_ldpc_enc.data

      # You are expected to see the following which indicates you passed the validation test:
      --------------------LDPC_ENC---------------------
      Operation latency:
     	avg: 13286.1 cycles, 5.11005 us
     	min: 12606 cycles, 4.84846 us
     	max: 19700 cycles, 7.57692 us
     TestCase [ 0] : validation_tc passed
      + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
      + Test Suite Summary : BBdev Validation Tests
      + Tests Total :        1
      + Tests Skipped :      0
      + Tests Passed :       1
      + Tests Failed :       0
      + Tests Lasted :       29.493 ms
      + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
      ```
      Passing the validation indicates that this testcase is valid and the parameters are as expected. 
     
   * To test decoding:
     ```
     $ sudo dpdk-test-bbdev -c F0 -a <ACC100_ADDR> -- -c bler -n 1 -b 1 -l 1 -s 30 -v <folder>/mcs_enc_dec_pair/mcs<x>_ldpc_dec.data 
     
     # You are expected to see the following which indicates you passed the validation test:
     time per u-second is: 31.937692
     num_ops here is: <# of {enq-deq} pairs DEFAULT 16>
     time_array[0] = 31.937693 // # of iterations, if you have 10 iterations in the same run, you are expcted to see 10 values
     Core4 BLER 0.0 % - Iters 6.0 - Tp 1146.2 Mbps <testcase you specified>
     SNR 30.00 BLER 0.0 % - Iterations 6.0 6 - Tp 1146.2 Mbps <testcase you specified>
     TestCase [ 0] : bler_tc passed
      + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
      + Test Suite Summary : BBdev BLER Tests
      + Tests Total :        1
      + Tests Skipped :      0
      + Tests Passed :       1
      + Tests Failed :       0
      + Tests Lasted :       40.9054 ms
      + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +
     ```
     You are expected to get the **decoder output** the same as the **encoder input** (which results in 0.0& BLER). **Notice**, the decoder input is not the same as the encoder output, as the encoder output are encoded bits, where the decoder takes in LLR values.
        * We set the default mode of the program to run 1 time and with 16 {enq-deq} paris. If you wish to change those values, please refer to `line 3639` to change how many iterations you wish to run the program; please refer to `line 2575` and `line 2599` to change how many {enq-deq} pairs you want to push to the card.
        * To vary SNR, simply change the value after -s <SNR value>


