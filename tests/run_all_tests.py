#!/usr/bin/env python
# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Speakeasy Test Runner

This script runs all Speakeasy tests including:
- Original tests (test_*.py in tests/)
- Extended tests (tests/more_tests/)

Usage:
    python run_all_tests.py           # Run all tests
    python run_all_tests.py -v        # Verbose output
    python run_all_tests.py --quick   # Run only quick unit tests (more_tests)
"""

import sys
import os
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description='Run Speakeasy tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--quick', action='store_true',
                        help='Run only quick unit tests (more_tests)')
    parser.add_argument('--original', action='store_true',
                        help='Run only original tests')
    parser.add_argument('--extended', action='store_true',
                        help='Run only extended tests (more_tests)')
    args = parser.parse_args()

    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    # Determine which tests to run
    if args.quick or args.extended:
        # Run only more_tests (quick unit tests)
        cmd.append(os.path.join(tests_dir, 'more_tests'))
    elif args.original:
        # Run only original tests (excluding more_tests)
        cmd.append(tests_dir)
        cmd.extend(['--ignore', os.path.join(tests_dir, 'more_tests')])
    else:
        # Run all tests
        cmd.append(tests_dir)
    
    # Print what we're doing
    print("=" * 60)
    print("Speakeasy Test Runner")
    print("=" * 60)
    if args.quick or args.extended:
        print("Running: Extended unit tests (more_tests/)")
    elif args.original:
        print("Running: Original tests only")
    else:
        print("Running: All tests")
    print("=" * 60)
    print()
    
    # Run pytest
    result = subprocess.run(cmd, cwd=tests_dir)
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
