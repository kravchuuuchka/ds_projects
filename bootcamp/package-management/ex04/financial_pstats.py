#!/usr/bin/env python3
import cProfile
import pstats
import sys


def run_profiling(ticker: str, field_name: str) -> None:
    import financial_enhanced

    profiler = cProfile.Profile()
    profiler.enable()
    financial_enhanced.get_financial_data(ticker, field_name)
    profiler.disable()

    with open("pstats-cumulative.txt", "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats("cumulative")
        stats.print_stats(5)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./profile_pstats.py 'MSFT' 'Total Revenue'")
        sys.exit(1)

    try:
        run_profiling(sys.argv[1], sys.argv[2])
        print("Saved to pstats-cumulative.txt")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)