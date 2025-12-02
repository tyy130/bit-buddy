#!/usr/bin/env python3
"""
Bit Buddy Debug Tools
Provides debugging utilities for development and troubleshooting.
"""

import json
import logging
import time
import traceback
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class DebugEvent:
    """Represents a debug event"""

    timestamp: float
    event_type: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    level: str = "info"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "message": self.message,
            "details": self.details,
            "level": self.level,
        }


class BitBuddyDebugger:
    """Debug helper for Bit Buddy development"""

    def __init__(
        self,
        buddy: Any,
        max_events: int = 1000,
        log_file: Optional[Path] = None,
    ):
        """Initialize debugger

        Args:
            buddy: The EnhancedBitBuddy instance to debug
            max_events: Maximum number of events to keep in memory
            log_file: Optional file to write debug logs to
        """
        self.buddy = buddy
        self.max_events = max_events
        self.log_file = log_file

        # Event storage
        self.events: deque = deque(maxlen=max_events)
        self.error_count = 0
        self.warning_count = 0

        # Session info
        self.session_start: Optional[float] = None
        self.session_id: str = ""

        # Breakpoints and watches
        self.breakpoints: Dict[str, Callable] = {}
        self.watches: Dict[str, Any] = {}

        # Performance tracking
        self.operation_times: Dict[str, List[float]] = {}

        logging.info("🐛 BitBuddyDebugger initialized")

    def start_debug_session(self, session_id: str = None):
        """Start a debug session

        Args:
            session_id: Optional session identifier
        """
        self.session_start = time.time()
        self.session_id = session_id or f"debug-{int(time.time())}"
        self.events.clear()
        self.error_count = 0
        self.warning_count = 0

        self._log_event("session_start", f"Debug session started: {self.session_id}")
        logging.info(f"🐛 Debug session started: {self.session_id}")

    def stop_debug_session(self) -> Dict[str, Any]:
        """Stop the debug session

        Returns:
            Session summary
        """
        if not self.session_start:
            return {"error": "No active session"}

        duration = time.time() - self.session_start

        summary = {
            "session_id": self.session_id,
            "duration_seconds": round(duration, 2),
            "total_events": len(self.events),
            "errors": self.error_count,
            "warnings": self.warning_count,
        }

        self._log_event("session_end", f"Debug session ended: {summary}")

        # Write to file if configured
        if self.log_file:
            self._write_session_log()

        self.session_start = None
        logging.info(f"🐛 Debug session ended: {summary}")
        return summary

    def _log_event(
        self,
        event_type: str,
        message: str,
        details: Dict[str, Any] = None,
        level: str = "info",
    ):
        """Log a debug event

        Args:
            event_type: Type of event
            message: Event message
            details: Additional details
            level: Log level (info, warning, error)
        """
        event = DebugEvent(
            timestamp=time.time(),
            event_type=event_type,
            message=message,
            details=details or {},
            level=level,
        )

        self.events.append(event)

        if level == "error":
            self.error_count += 1
        elif level == "warning":
            self.warning_count += 1

    def log_buddy_action(self, action: str, details: Dict[str, Any] = None):
        """Log a buddy action

        Args:
            action: Action name
            details: Action details
        """
        self._log_event("buddy_action", action, details)

    def log_error(self, error: Exception, context: str = None):
        """Log an error

        Args:
            error: The exception
            context: Where the error occurred
        """
        self._log_event(
            "error",
            str(error),
            {
                "context": context,
                "type": type(error).__name__,
                "traceback": traceback.format_exc(),
            },
            level="error",
        )

    def log_warning(self, message: str, details: Dict[str, Any] = None):
        """Log a warning

        Args:
            message: Warning message
            details: Additional details
        """
        self._log_event("warning", message, details, level="warning")

    def time_operation(self, operation_name: str):
        """Context manager for timing operations

        Args:
            operation_name: Name of the operation

        Usage:
            with debugger.time_operation("search"):
                results = rag.search(query)
        """
        return OperationTimer(self, operation_name)

    def _record_operation_time(self, operation_name: str, duration: float):
        """Record operation timing

        Args:
            operation_name: Name of operation
            duration: Duration in seconds
        """
        if operation_name not in self.operation_times:
            self.operation_times[operation_name] = []

        self.operation_times[operation_name].append(duration)

        # Keep only last 100 measurements
        if len(self.operation_times[operation_name]) > 100:
            self.operation_times[operation_name] = self.operation_times[
                operation_name
            ][-100:]

    def add_breakpoint(self, name: str, condition: Callable[[], bool]):
        """Add a conditional breakpoint

        Args:
            name: Breakpoint name
            condition: Function that returns True when breakpoint should trigger
        """
        self.breakpoints[name] = condition
        self._log_event("breakpoint_added", f"Breakpoint: {name}")

    def check_breakpoints(self) -> List[str]:
        """Check all breakpoints

        Returns:
            List of triggered breakpoint names
        """
        triggered = []
        for name, condition in self.breakpoints.items():
            try:
                if condition():
                    triggered.append(name)
                    self._log_event("breakpoint_triggered", f"Breakpoint: {name}")
            except Exception as e:
                self.log_error(e, f"Breakpoint check: {name}")

        return triggered

    def add_watch(self, name: str, getter: Callable[[], Any]):
        """Add a watch expression

        Args:
            name: Watch name
            getter: Function to get current value
        """
        self.watches[name] = getter

    def get_watch_values(self) -> Dict[str, Any]:
        """Get current values of all watches

        Returns:
            Dictionary of watch_name -> current_value
        """
        values = {}
        for name, getter in self.watches.items():
            try:
                values[name] = getter()
            except Exception as e:
                values[name] = f"<error: {e}>"

        return values

    def run_health_check(self) -> Dict[str, Any]:
        """Run a comprehensive health check

        Returns:
            Health check results
        """
        results = {
            "timestamp": time.time(),
            "session_active": self.session_start is not None,
            "buddy_status": "unknown",
            "rag_status": "unknown",
            "brain_status": "unknown",
            "issues": [],
            "performance": {},
        }

        # Check buddy
        try:
            if hasattr(self.buddy, "health_status"):
                results["buddy_status"] = self.buddy.health_status
            if hasattr(self.buddy, "personality"):
                results["personality_name"] = self.buddy.personality.name
        except Exception as e:
            results["issues"].append(f"Buddy check failed: {e}")

        # Check RAG
        try:
            if hasattr(self.buddy, "rag"):
                if hasattr(self.buddy.rag, "conn"):
                    results["rag_status"] = "connected"
                if hasattr(self.buddy.rag, "vector_enabled"):
                    results["vector_search"] = self.buddy.rag.vector_enabled
        except Exception as e:
            results["issues"].append(f"RAG check failed: {e}")

        # Check brain
        try:
            if hasattr(self.buddy, "brain"):
                results["brain_status"] = (
                    "available" if self.buddy.brain.available else "fallback"
                )
        except Exception as e:
            results["issues"].append(f"Brain check failed: {e}")

        # Performance summary
        for op_name, times in self.operation_times.items():
            if times:
                results["performance"][op_name] = {
                    "avg_ms": round(sum(times) / len(times) * 1000, 2),
                    "min_ms": round(min(times) * 1000, 2),
                    "max_ms": round(max(times) * 1000, 2),
                    "count": len(times),
                }

        return results

    def get_recent_events(
        self, count: int = 50, event_type: str = None
    ) -> List[Dict[str, Any]]:
        """Get recent debug events

        Args:
            count: Number of events to return
            event_type: Filter by event type

        Returns:
            List of events as dictionaries
        """
        events = list(self.events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [e.to_dict() for e in events[-count:]]

    def _write_session_log(self):
        """Write session log to file"""
        if not self.log_file:
            return

        try:
            log_data = {
                "session_id": self.session_id,
                "session_start": self.session_start,
                "events": [e.to_dict() for e in self.events],
            }

            with open(self.log_file, "w") as f:
                json.dump(log_data, f, indent=2)

            logging.info(f"📝 Session log written to {self.log_file}")
        except Exception as e:
            logging.error(f"Failed to write session log: {e}")

    def export_events(self, filepath: Path, format: str = "json") -> bool:
        """Export events to file

        Args:
            filepath: Output file path
            format: Export format (json or csv)

        Returns:
            True if export successful
        """
        try:
            events_data = [e.to_dict() for e in self.events]

            if format == "json":
                with open(filepath, "w") as f:
                    json.dump(events_data, f, indent=2)
            elif format == "csv":
                import csv

                with open(filepath, "w", newline="") as f:
                    if events_data:
                        writer = csv.DictWriter(f, fieldnames=events_data[0].keys())
                        writer.writeheader()
                        for event in events_data:
                            # Flatten details for CSV
                            event["details"] = json.dumps(event["details"])
                            writer.writerow(event)

            logging.info(f"📤 Exported {len(events_data)} events to {filepath}")
            return True
        except Exception as e:
            logging.error(f"Export failed: {e}")
            return False


class OperationTimer:
    """Context manager for timing operations"""

    def __init__(self, debugger: BitBuddyDebugger, operation_name: str):
        self.debugger = debugger
        self.operation_name = operation_name
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.debugger._record_operation_time(self.operation_name, duration)

        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Demo usage
    print("🐛 Bit Buddy Debug Tools Demo\n")

    # Create a mock buddy for testing
    class MockBuddy:
        health_status = "healthy"

        class personality:
            name = "TestBuddy"

        class rag:
            conn = True
            vector_enabled = True

        class brain:
            available = True

    mock_buddy = MockBuddy()
    debugger = BitBuddyDebugger(mock_buddy)

    # Start session
    debugger.start_debug_session("demo-session")

    # Log some events
    debugger.log_buddy_action("file_scan", {"files_found": 42})
    debugger.log_buddy_action("query", {"query": "find photos"})
    debugger.log_warning("Low disk space", {"free_gb": 1.5})

    # Time an operation
    with debugger.time_operation("search"):
        time.sleep(0.05)  # Simulate work

    # Health check
    print("Health Check Results:")
    health = debugger.run_health_check()
    for key, value in health.items():
        print(f"  {key}: {value}")

    # Get recent events
    print("\nRecent Events:")
    for event in debugger.get_recent_events(5):
        print(f"  [{event['level']}] {event['event_type']}: {event['message']}")

    # End session
    print("\nSession Summary:")
    summary = debugger.stop_debug_session()
    for key, value in summary.items():
        print(f"  {key}: {value}")
