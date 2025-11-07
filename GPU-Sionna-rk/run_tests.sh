#!/bin/bash

# Values to sweep
LLRMAG_VALUES=$(seq 0 2 28)
ITERS_VALUES=(1)

# Repeat count
REPEATS=10000

for llrmag in $LLRMAG_VALUES; do
  for iters in "${ITERS_VALUES[@]}"; do
    OUTFILE="decode_times_iter${iters}_repeat_${REPEATS}_llrmag${llrmag}_2ndRound.csv"
    echo "Running with llrmag=${llrmag}, iters=${iters}, output=${OUTFILE}"
    
    pytest -q run_decoder_test.py \
      --iters ${iters} \
      --timing \
      --repeats ${REPEATS} \
      --csv ${OUTFILE} \
      -s \
      --llrmag ${llrmag}
  done
done

