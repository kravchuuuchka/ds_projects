#!/bin/bash
python3 -m cProfile -s tottime ../financial_enhanced.py 'MSFT' 'Total Revenue' > ../profiling-http.txt