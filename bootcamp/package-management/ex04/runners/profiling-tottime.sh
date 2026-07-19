#!/bin/bash
python3 -m cProfile -s tottime ../financial.py 'MSFT' 'Total Revenue' > ../profiling-tottime.txt