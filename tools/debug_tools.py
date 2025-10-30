#!/usr/bin/env python3
"""
Bit Buddy Debug Tools - Comprehensive debugging and monitoring utilities
"""

import json
import logging
import os
import threading
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psutil


@dataclass
class DebugSession:
    """Debug session information"""

    session_id: str
    buddy_name: str
    start_time: float
    watch_dir: str
    model_path: str
    issues: List[str]
    performance_metrics: Dict[str, Any]
    log_file: str


class BitBuddyDebugger:
    """Comprehensive debugging system for bit buddies"""

    def __init__(self, buddy=None, debug_dir: Path = None):
        self.buddy = buddy
        self.debug_dir = debug_dir or (Path.home() / ".bit_buddies" / "debug")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logger()

        # Performance monitoring
        self.performance_data = {}
        self.monitoring_active = False
        self.monitor_thread = None

        # Debug session
        self.session = None

        # Issue tracker
        self.issues = []

    def _setup_logger(self) -> logging.Logger:
        """Setup debug logger"""
        logger = logging.getLogger(f"buddy_debug_{id(self)}")
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler
        log_file = self.debug_dir / f"debug_{int(time.time())}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def start_debug_session(self, buddy_name: str = None):
        """Start a new debug session"""
        session_id = f"debug_{int(time.time())}"

        if self.buddy:
            buddy_name = buddy_name or getattr(
                self.buddy.personality, "name", "unknown"
            )
            watch_dir = str(self.buddy.watch_dir)
            model_path = str(getattr(self.buddy, "model_path", "none"))
        else:
            buddy_name = buddy_name or "standalone"
            watch_dir = "unknown"
            model_path = "unknown"

        self.session = DebugSession(
            session_id=session_id,
            buddy_name=buddy_name,
            start_time=time.time(),
            watch_dir=watch_dir,
            model_path=model_path,
            issues=[],
            performance_metrics={},
            log_file=str(
                [
                    h.baseFilename
                    for h in self.logger.handlers
                    if hasattr(h, "baseFilename")
                ][0]
            ),
        )

        self.logger.info(f"🐛 Debug session started: {session_id}")
        self.logger.info(f"   Buddy: {buddy_name}")
        self.logger.info(f"   Watch dir: {watch_dir}")
        self.logger.info(f"   Model: {model_path}")

        # Start performance monitoring
        self.start_performance_monitoring()

        return session_id

    def start_performance_monitoring(self):
        """Start background performance monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._performance_monitor, daemon=True
        )
        self.monitor_thread.start()

        self.logger.info("📊 Performance monitoring started")

    def _performance_monitor(self):
        """Background performance monitoring loop"""
        while self.monitoring_active:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                # Process metrics (if we have a buddy)
                process_metrics = {}
                if self.buddy:
                    try:
                        process = psutil.Process()
                        process_metrics = {
                            "cpu_percent": process.cpu_percent(),
                            "memory_mb": process.memory_info().rss
                            / 1024
                            / 1024,
                            "num_threads": process.num_threads(),
                            "open_files": len(process.open_files()),
                        }
                    except Exception:
                        # Ignore process-specific errors (access, zombie
                        # process, etc.)
                        pass

                # Store metrics
                timestamp = time.time()
                self.performance_data[timestamp] = {
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available_gb": memory.available / (1024**3),
                        "disk_percent": disk.percent,
                    },
                    "process": process_metrics,
                }

                # Check for issues
                self._check_performance_issues(
                    cpu_percent, memory.percent, process_metrics
                )

                # Cleanup old data (keep last hour)
                cutoff_time = timestamp - 3600
                self.performance_data = {
                    k: v
                    for k, v in self.performance_data.items()
                    if k > cutoff_time
                }

            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

            time.sleep(5)  # Check every 5 seconds

    def _check_performance_issues(
        self, cpu_percent: float, memory_percent: float, process_metrics: Dict
    ):
        """Check for performance issues"""
        issues_found = []

        # High CPU usage
        if cpu_percent > 80:
            issues_found.append(f"High CPU usage: {cpu_percent:.1f}%")

        # High memory usage
        if memory_percent > 85:
            issues_found.append(
                f"High system memory usage: {memory_percent:.1f}%"
            )

        # High process memory (if available)
        if process_metrics.get("memory_mb", 0) > 1000:  # >1GB
            issues_found.append(
                f"High process memory: {process_metrics['memory_mb']:.1f}MB"
            )

        # Too many open files
        if process_metrics.get("open_files", 0) > 100:
            issues_found.append(
                f"Many open files: {process_metrics['open_files']}"
            )

        # Log new issues
        for issue in issues_found:
            if issue not in self.issues:
                self.issues.append(issue)
                self.logger.warning(f"⚠️  Performance issue detected: {issue}")

    def log_buddy_action(
        self, action: str, details: Dict = None, duration: float = None
    ):
        """Log a buddy action for debugging"""
        # Log the action (keep simple; avoid unused local variables)
        self.logger.info(
            f"🤖 Action: {action} {f'({duration*1000:.1f}ms)' if duration else ''}"
        )
        if details:
            self.logger.debug(f"   Details: {json.dumps(details, indent=2)}")

    def log_error(self, error: Exception, context: str = None):
        """Log an error with full context"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": time.time(),
            "traceback": traceback.format_exc(),
        }

        self.issues.append(
            f"{error_info['error_type']}: {error_info['error_message']}"
        )

        self.logger.error(
            f"❌ Error in {context or 'unknown context'}: {error}"
        )
        self.logger.debug(f"   Traceback:\n{error_info['traceback']}")

    def debug_file_system(self) -> Dict[str, Any]:
        """Debug file system related issues"""
        if not self.buddy:
            return {"error": "No buddy attached to debugger"}

        debug_info = {
            "watch_directory": {
                "path": str(self.buddy.watch_dir),
                "exists": self.buddy.watch_dir.exists(),
                "is_directory": (
                    self.buddy.watch_dir.is_dir()
                    if self.buddy.watch_dir.exists()
                    else False
                ),
                "permissions": self._check_directory_permissions(
                    self.buddy.watch_dir
                ),
                "file_count": (
                    len(list(self.buddy.watch_dir.rglob("*")))
                    if self.buddy.watch_dir.exists()
                    else 0
                ),
            },
            "buddy_directory": {
                "path": str(self.buddy.buddy_dir),
                "exists": self.buddy.buddy_dir.exists(),
                "files": (
                    list(self.buddy.buddy_dir.glob("*"))
                    if self.buddy.buddy_dir.exists()
                    else []
                ),
            },
            "rag_system": self._debug_rag_system(),
            "file_monitoring": self._debug_file_monitoring(),
        }

        self.logger.info("🔍 File system debug completed")
        return debug_info

    def _check_directory_permissions(self, directory: Path) -> Dict[str, bool]:
        """Check directory permissions"""
        if not directory.exists():
            return {"readable": False, "writable": False, "executable": False}

        return {
            "readable": os.access(directory, os.R_OK),
            "writable": os.access(directory, os.W_OK),
            "executable": os.access(directory, os.X_OK),
        }

    def _debug_rag_system(self) -> Dict[str, Any]:
        """Debug RAG system"""
        if not hasattr(self.buddy, "rag"):
            return {"error": "No RAG system found"}

        rag = self.buddy.rag

        try:
            # Check database
            cursor = rag.conn.execute("SELECT COUNT(*) FROM files")
            indexed_files = cursor.fetchone()[0]

            cursor = rag.conn.execute(
                "SELECT file_path, content_preview FROM files LIMIT 5"
            )
            sample_files = cursor.fetchall()

            # Check vector database
            vector_count = 0
            try:
                if hasattr(rag, "vector_db") and rag.vector_db:
                    # This is ChromaDB specific
                    collection = rag.vector_db.get_collection("file_chunks")
                    vector_count = collection.count()
            except Exception as e:
                self.logger.debug(f"Could not check vector database: {e}")

            return {
                "database_file": str(rag.db_path),
                "indexed_files": indexed_files,
                "vector_embeddings": vector_count,
                "sample_files": [
                    {"path": row[0], "preview": row[1][:100]}
                    for row in sample_files
                ],
                "status": (
                    "healthy" if indexed_files > 0 else "no_files_indexed"
                ),
            }

        except Exception as e:
            self.log_error(e, "RAG system debug")
            return {"error": str(e)}

    def _debug_file_monitoring(self) -> Dict[str, Any]:
        """Debug file monitoring system"""
        if not hasattr(self.buddy, "file_monitor"):
            return {"status": "no_file_monitor"}

        monitor = self.buddy.file_monitor

        return {
            "is_running": getattr(monitor, "is_alive", lambda: False)(),
            "watch_path": str(getattr(monitor, "watch_path", "unknown")),
            "event_count": getattr(monitor, "event_count", 0),
        }

    def debug_personality_system(self) -> Dict[str, Any]:
        """Debug personality system"""
        if not self.buddy or not hasattr(self.buddy, "personality"):
            return {"error": "No personality system found"}

        personality = self.buddy.personality

        debug_info = {
            "basic_info": {
                "name": personality.name,
                "buddy_dir": str(personality.buddy_dir),
            },
            "traits": {
                "humor": personality.humor,
                "curiosity": personality.curiosity,
                "formality": personality.formality,
                "empathy": getattr(personality, "empathy", "unknown"),
                "temperature": personality.temperature,
                "specialties": personality.specialties,
            },
            "files": {
                "personality_file": (
                    personality.buddy_dir / "personality.json"
                ).exists(),
                "experience_file": (
                    personality.buddy_dir / "experience.json"
                ).exists(),
            },
            "experience": {
                "total_events": len(personality.experience_log),
                "recent_events": (
                    personality.experience_log[-5:]
                    if personality.experience_log
                    else []
                ),
            },
        }

        return debug_info

    def debug_model_system(self) -> Dict[str, Any]:
        """Debug AI model system"""
        if not self.buddy:
            return {"error": "No buddy attached"}

        debug_info = {
            "model_path": str(getattr(self.buddy, "model_path", "none")),
            "brain_system": "not_implemented",
        }

        # Check if model file exists
        if hasattr(self.buddy, "model_path") and self.buddy.model_path:
            model_path = Path(self.buddy.model_path)
            debug_info["model_file"] = {
                "exists": model_path.exists(),
                "size_mb": (
                    model_path.stat().st_size / (1024 * 1024)
                    if model_path.exists()
                    else 0
                ),
                "readable": (
                    os.access(model_path, os.R_OK)
                    if model_path.exists()
                    else False
                ),
            }

        # Check brain system
        if hasattr(self.buddy, "brain"):
            debug_info["brain_system"] = {
                "type": type(self.buddy.brain).__name__,
                "model_loaded": getattr(
                    self.buddy.brain, "model_loaded", False
                ),
                "last_error": getattr(self.buddy.brain, "last_error", None),
            }

        return debug_info

    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        health = {
            "overall_status": "healthy",
            "timestamp": time.time(),
            "checks": {},
            "issues": self.issues.copy(),
            "recommendations": [],
        }

        # File system check
        fs_debug = self.debug_file_system()
        health["checks"]["file_system"] = {
            "status": (
                "healthy"
                if fs_debug.get("watch_directory", {}).get("exists")
                else "error"
            ),
            "details": fs_debug,
        }

        # Personality check
        personality_debug = self.debug_personality_system()
        health["checks"]["personality"] = {
            "status": (
                "healthy" if "error" not in personality_debug else "error"
            ),
            "details": personality_debug,
        }

        # Model check
        model_debug = self.debug_model_system()
        health["checks"]["model"] = {
            "status": "healthy" if "error" not in model_debug else "warning",
            "details": model_debug,
        }

        # Performance check
        if self.performance_data:
            latest_perf = list(self.performance_data.values())[-1]
            cpu_ok = latest_perf["system"]["cpu_percent"] < 80
            memory_ok = latest_perf["system"]["memory_percent"] < 85

            health["checks"]["performance"] = {
                "status": "healthy" if cpu_ok and memory_ok else "warning",
                "details": latest_perf,
            }

        # Generate recommendations
        if (
            not health["checks"]["file_system"]["details"]
            .get("watch_directory", {})
            .get("exists")
        ):
            health["recommendations"].append(
                "Watch directory does not exist - check path configuration"
            )

        if (
            health["checks"]["file_system"]["details"]
            .get("rag_system", {})
            .get("indexed_files", 0)
            == 0
        ):
            health["recommendations"].append(
                "No files indexed - run file indexing"
            )

        if len(health["issues"]) > 0:
            health["overall_status"] = "warning"

        if any(
            check["status"] == "error" for check in health["checks"].values()
        ):
            health["overall_status"] = "error"

        return health

    def generate_debug_report(self) -> str:
        """Generate comprehensive debug report"""
        if not self.session:
            self.start_debug_session()

        report_lines = [
            "🐛 BIT BUDDY DEBUG REPORT",
            "=" * 50,
            f"Session ID: {self.session.session_id}",
            f"Buddy Name: {self.session.buddy_name}",
            f"Start Time: {datetime.fromtimestamp(self.session.start_time)}",
            f"Duration: {time.time() - self.session.start_time:.1f}s",
            "",
            "📊 PERFORMANCE SUMMARY",
            "-" * 25,
        ]

        # Performance summary
        if self.performance_data:
            cpu_values = [
                d["system"]["cpu_percent"]
                for d in self.performance_data.values()
            ]
            memory_values = [
                d["system"]["memory_percent"]
                for d in self.performance_data.values()
            ]

            report_lines.extend(
                [
                    f"Average CPU: {sum(cpu_values)/len(cpu_values):.1f}%",
                    f"Peak CPU: {max(cpu_values):.1f}%",
                    f"Average Memory: {sum(memory_values)/len(memory_values):.1f}%",
                    f"Peak Memory: {max(memory_values):.1f}%",
                ])
        else:
            report_lines.append("No performance data collected")

        # Issues
        report_lines.extend(["", "⚠️  ISSUES FOUND", "-" * 15])

        if self.issues:
            for issue in self.issues:
                report_lines.append(f"• {issue}")
        else:
            report_lines.append("No issues detected")

        # Health check
        health = self.run_health_check()
        report_lines.extend(
            [
                "",
                f"🏥 HEALTH STATUS: {health['overall_status'].upper()}",
                "-" * 20,
            ]
        )

        for check_name, check_info in health["checks"].items():
            status_emoji = (
                "✅"
                if check_info["status"] == "healthy"
                else "⚠️" if check_info["status"] == "warning" else "❌"
            )
            report_lines.append(
                f"{status_emoji} {check_name}: {check_info['status']}"
            )

        # Recommendations
        if health["recommendations"]:
            report_lines.extend(["", "💡 RECOMMENDATIONS", "-" * 17])
            for rec in health["recommendations"]:
                report_lines.append(f"• {rec}")

        report_content = "\n".join(report_lines)

        # Save report
        report_file = self.debug_dir / f"report_{self.session.session_id}.txt"
        report_file.write_text(report_content)

        self.logger.info(f"📋 Debug report saved to: {report_file}")

        return report_content

    def stop_debug_session(self):
        """Stop debug session and cleanup"""
        if self.session:
            duration = time.time() - self.session.start_time
            self.logger.info(
                f"🏁 Debug session ended: {self.session.session_id} (duration: {duration:.1f}s)"
            )

        # Stop monitoring
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        # Generate final report
        if self.session:
            self.generate_debug_report()


# Debugging context manager
class DebugContext:
    """Context manager for debugging buddy operations"""

    def __init__(self, debugger: BitBuddyDebugger, operation_name: str):
        self.debugger = debugger
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.debugger.logger.debug(
            f"🚀 Starting operation: {self.operation_name}"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type:
            self.debugger.log_error(exc_val, self.operation_name)
        else:
            self.debugger.log_buddy_action(
                self.operation_name, duration=duration
            )


# Utility functions for quick debugging


def quick_debug_buddy(buddy, operation: str = None):
    """Quick debug a buddy instance"""
    debugger = BitBuddyDebugger(buddy)
    session_id = debugger.start_debug_session()

    print(f"🐛 Quick debug session: {session_id}")

    if operation:
        print(f"⚙️  Testing operation: {operation}")
        # You can add specific operation tests here

    # Run health check
    health = debugger.run_health_check()
    print(f"🏥 Health status: {health['overall_status']}")

    if health["issues"]:
        print("⚠️  Issues found:")
        for issue in health["issues"]:
            print(f"   • {issue}")

    if health["recommendations"]:
        print("💡 Recommendations:")
        for rec in health["recommendations"]:
            print(f"   • {rec}")

    # Generate report
    report = debugger.generate_debug_report()
    debugger.stop_debug_session()

    return report


def debug_file_operations(watch_dir: Path):
    """Debug file system operations"""
    print(f"🔍 Debugging file operations in: {watch_dir}")

    # Check directory
    if not watch_dir.exists():
        print(f"❌ Directory doesn't exist: {watch_dir}")
        return

    if not watch_dir.is_dir():
        print(f"❌ Path is not a directory: {watch_dir}")
        return

    # Check permissions
    perms = {
        "readable": os.access(watch_dir, os.R_OK),
        "writable": os.access(watch_dir, os.W_OK),
        "executable": os.access(watch_dir, os.X_OK),
    }

    print("📋 Directory permissions:")
    for perm, status in perms.items():
        status_emoji = "✅" if status else "❌"
        print(f"   {status_emoji} {perm}")

    # Count files
    try:
        files = list(watch_dir.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        dir_count = len([f for f in files if f.is_dir()])

        print(f"📁 Contents: {file_count} files, {dir_count} directories")

        # Show sample files
        sample_files = [f for f in files if f.is_file()][:5]
        if sample_files:
            print("📄 Sample files:")
            for file_path in sample_files:
                size = file_path.stat().st_size
                print(f"   • {file_path.name} ({size} bytes)")

    except Exception as e:
        print(f"❌ Error scanning directory: {e}")


if __name__ == "__main__":
    # CLI interface for debugging
    import argparse

    parser = argparse.ArgumentParser(description="Bit Buddy Debug Tools")
    subparsers = parser.add_subparsers(dest="command", help="Debug commands")

    # File system debug
    fs_parser = subparsers.add_parser("check-files", help="Check file system")
    fs_parser.add_argument("directory", help="Directory to check")

    # Health check
    subparsers.add_parser("health", help="System health check")

    # Performance monitor
    perf_parser = subparsers.add_parser(
        "monitor", help="Start performance monitoring"
    )
    perf_parser.add_argument(
        "--duration", type=int, default=60, help="Monitor duration in seconds"
    )

    args = parser.parse_args()

    if args.command == "check-files":
        debug_file_operations(Path(args.directory))

    elif args.command == "health":
        debugger = BitBuddyDebugger()
        health = debugger.run_health_check()
        print(json.dumps(health, indent=2, default=str))

    elif args.command == "monitor":
        debugger = BitBuddyDebugger()
        debugger.start_debug_session()

        print(f"📊 Monitoring for {args.duration} seconds...")
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            pass

        report = debugger.generate_debug_report()
        print(report)
        debugger.stop_debug_session()

    else:
        parser.print_help()
