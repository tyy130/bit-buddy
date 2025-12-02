#!/usr/bin/env python3
"""
Bit Buddy Test Runner
Utility script for running tests with various configurations.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_tests(
    test_path: Optional[str] = None,
    markers: Optional[List[str]] = None,
    verbose: bool = False,
    coverage: bool = False,
    failfast: bool = False,
) -> int:
    """Run pytest with specified options

    Args:
        test_path: Specific test file or directory to run
        markers: Pytest markers to filter tests
        verbose: Enable verbose output
        coverage: Enable coverage reporting
        failfast: Stop on first failure

    Returns:
        Exit code from pytest
    """
    cmd = [sys.executable, "-m", "pytest"]

    # Test path
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    # Verbose output
    if verbose:
        cmd.append("-v")

    # Stop on first failure
    if failfast:
        cmd.append("-x")

    # Markers
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])

    # Coverage
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=html"])

    # Run tests
    print(f"🧪 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode


def run_unit_tests(verbose: bool = False) -> int:
    """Run only unit tests

    Args:
        verbose: Enable verbose output

    Returns:
        Exit code
    """
    return run_tests(markers=["not integration", "not performance"], verbose=verbose)


def run_integration_tests(verbose: bool = False) -> int:
    """Run integration tests

    Args:
        verbose: Enable verbose output

    Returns:
        Exit code
    """
    return run_tests(markers=["integration"], verbose=verbose)


def run_performance_tests(verbose: bool = False) -> int:
    """Run performance tests

    Args:
        verbose: Enable verbose output

    Returns:
        Exit code
    """
    return run_tests(markers=["performance"], verbose=verbose)


def run_all_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Run all tests

    Args:
        verbose: Enable verbose output
        coverage: Enable coverage reporting

    Returns:
        Exit code
    """
    return run_tests(verbose=verbose, coverage=coverage)


def check_test_imports() -> bool:
    """Check that all test imports work

    Returns:
        True if all imports successful
    """
    print("🔍 Checking test imports...")

    imports_to_check = [
        "pytest",
        "enhanced_buddy",
        "deploy",
        "mesh_network",
        "debug_tools",
    ]

    all_ok = True
    for module in imports_to_check:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            all_ok = False

    return all_ok


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Bit Buddy Test Runner")

    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Type of tests to run (default: all)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )

    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Enable coverage reporting"
    )

    parser.add_argument(
        "-x", "--failfast", action="store_true", help="Stop on first failure"
    )

    parser.add_argument(
        "-p", "--path", help="Specific test file or directory"
    )

    parser.add_argument(
        "--check-imports",
        action="store_true",
        help="Check test imports only",
    )

    args = parser.parse_args()

    # Check imports only
    if args.check_imports:
        success = check_test_imports()
        return 0 if success else 1

    # Run specified tests
    if args.path:
        return run_tests(
            test_path=args.path,
            verbose=args.verbose,
            coverage=args.coverage,
            failfast=args.failfast,
        )

    if args.test_type == "unit":
        return run_unit_tests(verbose=args.verbose)
    elif args.test_type == "integration":
        return run_integration_tests(verbose=args.verbose)
    elif args.test_type == "performance":
        return run_performance_tests(verbose=args.verbose)
    else:
        return run_all_tests(verbose=args.verbose, coverage=args.coverage)


if __name__ == "__main__":
    sys.exit(main())
