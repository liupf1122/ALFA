#!/usr/bin/env python
"""Recompute descriptive statistics from an evaluation metrics.csv."""
import argparse
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('metrics', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    table = pd.read_csv(args.metrics)
    summary = table.select_dtypes(include='number').agg(['count', 'mean', 'std', 'min', 'max']).T
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index_label='metric')
    print(summary.to_string())


if __name__ == '__main__':
    main()
