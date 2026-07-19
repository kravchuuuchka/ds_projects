#!/bin/bash
python3 -m cProfile -s ncalls ../financial_enhanced.py 'MSFT' 'Total Revenue' > ../profiling-ncalls.txt