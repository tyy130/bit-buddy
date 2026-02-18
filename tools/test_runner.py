#!/usr/bin/env python3
"""
Bit Buddy Test Runner - Comprehensive testing utilities
"""

import logging
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

import pytest


def setup_test_environment():
    """Setup isolated test environment"""
    # Create temporary directories
    test_root = Path(tempfile.mkdtemp(prefix="bitbuddy_test_"))

    test_dirs = {
        "buddy_dir": test_root / "buddy",
        "watch_dir": test_root / "watch",
        "models_dir": test_root / "models",
        "debug_dir": test_root / "debug",
    }

    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True)

    # Create test files
    test_files = {
        "watch_dir/document1.txt": "This is a test document about machine learning",
        "watch_dir/document2.md": "# Project Notes\n\nSome important project information",
        "watch_dir/code/test.py": "import numpy as np\nprint('Hello World')",
        "watch_dir/photos/vacation.jpg": "",  # Empty file for testing
        "watch_dir/data/results.csv": "name,value\ntest1,100\ntest2,200",
    }

    for file_path, content in test_files.items():
        full_path = test_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    return test_root, test_dirs


def cleanup_test_environment(test_root: Path):
    """Clean up test environment"""
    try:
        shutil.rmtree(test_root)
        print(f"✅ Cleaned up test environment: {test_root}")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up {test_root}: {e}")


class TestRunner:
    """Advanced test runner for bit buddy system"""

    def __init__(self, test_dir: Path = None):
        self.test_dir = test_dir or Path(__file__).parent / "tests"
        self.results = {}
        self.test_env = None

    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests"""
        print("🧪 Running unit tests...")

        args = ["-v"] if verbose else ["-q"]
        args.extend(
            [
                str(self.test_dir / "test_buddy_system.py"),
                "-m",
                "not integration and not performance",
            ]
        )

        result = pytest.main(args)

        self.results["unit_tests"] = {
            "exit_code": result,
            "status": "passed" if result == 0 else "failed",
        }

        return self.results["unit_tests"]

    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running integration tests...")

        # Setup test environment
        self.test_env, test_dirs = setup_test_environment()

        try:
            args = ["-v"] if verbose else ["-q"]
            args.extend(
                [
                    str(self.test_dir / "test_buddy_system.py"),
                    "-m",
                    "integration",
                ]
            )

            result = pytest.main(args)

            self.results["integration_tests"] = {
                "exit_code": result,
                "status": "passed" if result == 0 else "failed",
                "test_env": str(self.test_env),
            }

        finally:
            # Cleanup
            if self.test_env:
                cleanup_test_environment(self.test_env)

        return self.results["integration_tests"]

    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests"""
        print("🚀 Running performance tests...")

        args = ["-v"] if verbose else ["-q"]
        args.extend([str(self.test_dir / "test_buddy_system.py"), "-m", "performance"])

        result = pytest.main(args)

        self.results["performance_tests"] = {
            "exit_code": result,
            "status": "passed" if result == 0 else "failed",
        }

        return self.results["performance_tests"]

    def run_model_tests(self, model_path: Path = None, verbose: bool = False) -> Dict[str, Any]:
        """Run tests that require AI models"""
        if not model_path or not model_path.exists():
            print("⚠️  Skipping model tests - no model file provided")
            self.results["model_tests"] = {
                "status": "skipped",
                "reason": "No model file available",
            }
            return self.results["model_tests"]

        print(f"🧠 Running model tests with: {model_path}")

        # Set environment variable for tests
        os.environ["TEST_MODEL_PATH"] = str(model_path)

        try:
            args = ["-v"] if verbose else ["-q"]
            args.extend(
                [
                    str(self.test_dir / "test_buddy_system.py"),
                    "-m",
                    "requires_model",
                ]
            )

            result = pytest.main(args)

            self.results["model_tests"] = {
                "exit_code": result,
                "status": "passed" if result == 0 else "failed",
                "model_path": str(model_path),
            }

        finally:
            # Clean up environment
            if "TEST_MODEL_PATH" in os.environ:
                del os.environ["TEST_MODEL_PATH"]

        return self.results["model_tests"]

    def run_stress_tests(self, duration: int = 60) -> Dict[str, Any]:
        """Run stress tests to check system under load"""
        print(f"💪 Running stress tests for {duration} seconds...")

        # Setup test environment
        test_root, test_dirs = setup_test_environment()

        try:
            # Import buddy system
            sys.path.insert(0, str(Path(__file__).parent))
            from debug_tools import BitBuddyDebugger
            from enhanced_buddy import EnhancedBitBuddy

            # Create buddy
            buddy = EnhancedBitBuddy(
                test_dirs["buddy_dir"], test_dirs["watch_dir"], model_path=None
            )

            # Setup debugger
            debugger = BitBuddyDebugger(buddy, test_dirs["debug_dir"])
            debugger.start_debug_session()

            start_time = time.time()
            operations = 0
            errors = []

            # Stress test loop
            while time.time() - start_time < duration:
                try:
                    # Perform various operations
                    buddy.rag.index_files()
                    operations += 1

                    buddy.ask("What files do you see?")
                    operations += 1

                    buddy.rag.search_files("test")
                    operations += 1

                    # Add some delay
                    time.sleep(0.1)

                except Exception as e:
                    errors.append(str(e))
                    logging.error(f"Stress test error: {e}")

            # Get final performance data
            health = debugger.run_health_check()
            debugger.stop_debug_session()

            self.results["stress_tests"] = {
                "duration": time.time() - start_time,
                "operations_completed": operations,
                "errors": errors,
                "final_health": health["overall_status"],
                "status": "passed" if len(errors) == 0 else "warning",
            }

        except Exception as e:
            self.results["stress_tests"] = {
                "status": "failed",
                "error": str(e),
            }

        finally:
            cleanup_test_environment(test_root)

        return self.results["stress_tests"]

    def run_compatibility_tests(self) -> Dict[str, Any]:
        """Test compatibility with different Python versions and dependencies"""
        print("🐍 Running compatibility tests...")

        import importlib
        import sys

        compatibility = {
            "python_version": sys.version,
            "platform": sys.platform,
            "required_packages": {},
            "optional_packages": {},
            "status": "passed",
        }

        # Test required packages
        required_packages = [
            "fastapi",
            "uvicorn",
            "watchdog",
            "requests",
            "cryptography",
            "psutil",
            "pydantic",
        ]

        for package in required_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, "__version__", "unknown")
                compatibility["required_packages"][package] = {
                    "status": "available",
                    "version": version,
                }
            except ImportError:
                compatibility["required_packages"][package] = {
                    "status": "missing",
                    "version": None,
                }
                compatibility["status"] = "failed"

        # Test optional packages
        optional_packages = [
            "sentence_transformers",
            "chromadb",
            "torch",
            "transformers",
            "llama_cpp",
        ]

        for package in optional_packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, "__version__", "unknown")
                compatibility["optional_packages"][package] = {
                    "status": "available",
                    "version": version,
                }
            except ImportError:
                compatibility["optional_packages"][package] = {
                    "status": "missing",
                    "version": None,
                }

        self.results["compatibility_tests"] = compatibility
        return compatibility

    def run_all_tests(
        self,
        include_integration: bool = True,
        include_performance: bool = False,
        include_stress: bool = False,
        model_path: Path = None,
        stress_duration: int = 30,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🎯 Running comprehensive test suite...")
        start_time = time.time()

        # Always run these
        self.run_unit_tests(verbose)
        self.run_compatibility_tests()

        # Optional test suites
        if include_integration:
            self.run_integration_tests(verbose)

        if include_performance:
            self.run_performance_tests(verbose)

        if model_path:
            self.run_model_tests(model_path, verbose)

        if include_stress:
            self.run_stress_tests(stress_duration)

        # Summary
        total_time = time.time() - start_time

        summary = {
            "total_duration": total_time,
            "tests_run": list(self.results.keys()),
            "overall_status": self._calculate_overall_status(),
            "results": self.results,
        }

        self._print_test_summary(summary)

        return summary

    def _calculate_overall_status(self) -> str:
        """Calculate overall test status"""
        statuses = [result.get("status", "unknown") for result in self.results.values()]

        if any(status == "failed" for status in statuses):
            return "failed"
        elif any(status == "warning" for status in statuses):
            return "warning"
        elif all(status in ["passed", "skipped"] for status in statuses):
            return "passed"
        else:
            return "unknown"

    def _print_test_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUITE SUMMARY")
        print("=" * 60)

        status_emoji = {
            "passed": "✅",
            "failed": "❌",
            "warning": "⚠️",
            "skipped": "⏭️",
            "unknown": "❓",
        }

        overall_emoji = status_emoji.get(summary["overall_status"], "❓")
        print(f"{overall_emoji} Overall Status: {summary['overall_status'].upper()}")
        print(f"⏱️  Total Duration: {summary['total_duration']:.1f}s")
        print()

        # Individual test results
        for test_name, result in summary["results"].items():
            status = result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            print(f"{emoji} {test_name}: {status}")

            if status == "failed" and "error" in result:
                print(f"    Error: {result['error']}")
            elif "exit_code" in result:
                print(f"    Exit code: {result['exit_code']}")

        print("\n" + "=" * 60)


def main():
    """CLI interface for test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Bit Buddy Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--stress", action="store_true", help="Run stress tests")
    parser.add_argument("--model", type=Path, help="Path to AI model for model tests")
    parser.add_argument(
        "--stress-duration",
        type=int,
        default=30,
        help="Stress test duration (seconds)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    runner = TestRunner()

    if args.unit:
        runner.run_unit_tests(args.verbose)
    elif args.integration:
        runner.run_integration_tests(args.verbose)
    elif args.performance:
        runner.run_performance_tests(args.verbose)
    elif args.stress:
        runner.run_stress_tests(args.stress_duration)
    elif args.all:
        runner.run_all_tests(
            include_integration=True,
            include_performance=True,
            include_stress=True,
            model_path=args.model,
            stress_duration=args.stress_duration,
            verbose=args.verbose,
        )
    else:
        # Default: run basic tests
        runner.run_all_tests(
            include_integration=True,
            include_performance=False,
            include_stress=False,
            model_path=args.model,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()
