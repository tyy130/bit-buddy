#!/usr/bin/env python3
"""
Bit Buddy Installer - Drive analyzer and model selector
"""

import shutil
from pathlib import Path
from typing import Dict, Tuple

import psutil


class DriveAnalyzer:
    """Analyzes drive space and recommends appropriate model"""

    # Model requirements (in GB)
    MODELS = {
        "tinyllama-1.1b": {
            "size_gb": 0.7,
            "ram_gb": 2,
            "description": "Ultra-lightweight (fastest)",
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf",
        },
        "qwen2.5-1.5b": {
            "size_gb": 0.9,
            "ram_gb": 3,
            "description": "Recommended (best balance)",
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        },
        "phi3.5-mini": {
            "size_gb": 2.3,
            "ram_gb": 4,
            "description": "Most capable (slower)",
            "url": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-q4.gguf",
        },
    }

    @staticmethod
    def get_drive_info(drive_path: str = None) -> Dict:
        """Get drive space information"""
        if drive_path is None:
            drive_path = Path.home().drive or "/"

        usage = psutil.disk_usage(drive_path)

        return {
            "total_gb": usage.total / (1024**3),
            "used_gb": usage.used / (1024**3),
            "free_gb": usage.free / (1024**3),
            "percent_used": usage.percent,
        }

    @staticmethod
    def get_ram_info() -> Dict:
        """Get system RAM information"""
        mem = psutil.virtual_memory()

        return {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent_used": mem.percent,
        }

    @classmethod
    def recommend_model(cls, drive_path: str = None) -> Tuple[str, Dict]:
        """Recommend best model based on available resources"""
        drive_info = cls.get_drive_info(drive_path)
        ram_info = cls.get_ram_info()

        free_space_gb = drive_info["free_gb"]
        available_ram_gb = ram_info["available_gb"]

        # Need at least 2GB free for app + model + operating space
        min_required = 2.0

        # Select model based on constraints
        for model_id in ["phi3.5-mini", "qwen2.5-1.5b", "tinyllama-1.1b"]:
            model = cls.MODELS[model_id]
            total_required = model["size_gb"] + 1.0  # +1GB for app & data

            if free_space_gb >= total_required and available_ram_gb >= model["ram_gb"]:
                return model_id, {
                    "model": model,
                    "drive_info": drive_info,
                    "ram_info": ram_info,
                    "can_install": True,
                    "reason": f"Sufficient space ({free_space_gb:.1f}GB free) and RAM ({available_ram_gb:.1f}GB available)",
                }

        # If no model fits, return smallest with warning
        return "tinyllama-1.1b", {
            "model": cls.MODELS["tinyllama-1.1b"],
            "drive_info": drive_info,
            "ram_info": ram_info,
            "can_install": free_space_gb >= 2.0,
            "reason": (
                "Limited resources - using smallest model"
                if free_space_gb >= 2.0
                else "Insufficient space!"
            ),
        }

    @staticmethod
    def estimate_index_size(folder_path: Path) -> float:
        """Estimate index size for a folder (in GB)"""
        try:
            total_size = 0
            # Count text-like files
            for ext in ["*.txt", "*.md", "*.pdf", "*.docx"]:
                for f in folder_path.rglob(ext):
                    try:
                        total_size += f.stat().st_size
                    except BaseException:
                        pass

            # Index is roughly 10-15% of source size (embeddings)
            index_size_gb = (total_size * 0.15) / (1024**3)
            return max(0.1, index_size_gb)  # Minimum 100MB
        except Exception:
            return 0.5  # Default estimate


class InstallationPlanner:
    """Plan and execute Bit Buddy installation"""

    def __init__(self, install_drive: str = None):
        self.install_drive = install_drive or str(Path.home().drive)
        self.install_dir = Path(self.install_drive) / "BitBuddy"
        self.analyzer = DriveAnalyzer()

    def plan_installation(self, watch_folder: Path = None) -> Dict:
        """Create installation plan"""
        if watch_folder is None:
            watch_folder = Path.home() / "Documents"

        # Get model recommendation (returns tuple)
        model_id, model_info = self.analyzer.recommend_model(self.install_drive)

        # Estimate space needed
        index_size = self.analyzer.estimate_index_size(watch_folder)
        total_needed = (
            model_info["model"]["size_gb"]  # Model
            + 0.5  # Application files
            + index_size  # Index
            + 0.5  # Operating space
        )

        plan = {
            "install_dir": str(self.install_dir),
            "watch_folder": str(watch_folder),
            "model": {
                "id": model_id,
                "name": model_info["model"]["description"],
                "size_gb": model_info["model"]["size_gb"],
                "url": model_info["model"]["url"],
            },
            "space": {
                "total_needed_gb": total_needed,
                "available_gb": model_info["drive_info"]["free_gb"],
                "can_install": model_info["can_install"],
            },
            "estimated_index_size_gb": index_size,
        }

        return plan

    def check_prerequisites(self) -> Dict:
        """Check system prerequisites"""
        checks = {
            "python": shutil.which("python") is not None or shutil.which("python3") is not None,
            "space": self.analyzer.get_drive_info(self.install_drive)["free_gb"] >= 2.0,
            "ram": self.analyzer.get_ram_info()["available_gb"] >= 2.0,
        }

        checks["all_pass"] = all(checks.values())
        return checks


def main():
    """CLI test of drive analyzer"""
    print("🔍 Bit Buddy Installation Analyzer\n")

    # Analyze system
    analyzer = DriveAnalyzer()

    print("📊 System Information:")
    drive = analyzer.get_drive_info()
    print(f"  Drive Space: {drive['free_gb']:.1f}GB free of {drive['total_gb']:.1f}GB")
    print(f"  Usage: {drive['percent_used']:.1f}%")

    ram = analyzer.get_ram_info()
    print(f"\n  RAM: {ram['available_gb']:.1f}GB available of {ram['total_gb']:.1f}GB")
    print(f"  Usage: {ram['percent_used']:.1f}%")

    # Get recommendation
    model_id, rec = analyzer.recommend_model()
    print(f"\n🤖 Recommended Model: {model_id}")
    print(f"  {rec['model']['description']}")
    print(f"  Size: {rec['model']['size_gb']:.1f}GB")
    print(f"  RAM needed: {rec['model']['ram_gb']}GB")
    print(f"  Reason: {rec['reason']}")

    # Installation plan (use current directory as install location)
    planner = InstallationPlanner(install_drive=Path.cwd())
    plan = planner.plan_installation()

    print(f"\n📦 Installation Plan:")
    print(f"  Install to: {plan['install_dir']}")
    print(f"  Watch folder: {plan['watch_folder']}")
    print(f"  Total space needed: {plan['space']['total_needed_gb']:.1f}GB")
    print(f"  Available: {plan['space']['available_gb']:.1f}GB")
    print(f"  Can install: {'✓ YES' if plan['space']['can_install'] else '✗ NO'}")

    # Prerequisites
    prereqs = planner.check_prerequisites()
    print(f"\n✅ Prerequisites:")
    print(f"  Python: {'✓' if prereqs['python'] else '✗'}")
    print(f"  Disk Space: {'✓' if prereqs['space'] else '✗'}")
    print(f"  RAM: {'✓' if prereqs['ram'] else '✗'}")
    print(f"\n  Ready to install: {'YES!' if prereqs['all_pass'] else 'NO - check requirements'}")


if __name__ == "__main__":
    main()
