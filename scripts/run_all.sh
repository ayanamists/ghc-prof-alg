#!/usr/bin/env sh

./scripts/run_slow.sh
./scripts/run_fast.sh

python3 scripts/analyze.py results/fast.log
python3 scripts/analyze.py results/slow.log
