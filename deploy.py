#!/usr/bin/env python3
"""
Bit Buddy Deployment Manager
Handles buddy deployment, model management, and system configuration.
"""

import json
import logging
import random
import time
from pathlib import Path
from typing import Any, Dict

from installer import DriveAnalyzer


class BuddyDeploymentManager:
    """Manages buddy deployment and system configuration"""

    # Model registry with download URLs and metadata
    MODEL_REGISTRY = {
        "tinyllama-1.1b": {
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf",
            "size_mb": 700,
            "ram_required_mb": 2048,
            "description": "Ultra-lightweight model, fastest responses",
        },
        "qwen2.5-1.5b": {
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "size_mb": 900,
            "ram_required_mb": 3072,
            "description": "Recommended balance of speed and capability",
        },
        "phi3.5-mini": {
            "url": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-q4.gguf",
            "size_mb": 2300,
            "ram_required_mb": 4096,
            "description": "Most capable model, slower but smarter",
        },
    }

    def __init__(self, install_dir: Path):
        """Initialize deployment manager

        Args:
            install_dir: Base directory for installation
        """
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.models_dir = self.install_dir / "models"
        self.buddies_dir = self.install_dir / "buddies"
        self.config_file = self.install_dir / "config.json"

        self.models_dir.mkdir(exist_ok=True)
        self.buddies_dir.mkdir(exist_ok=True)

        # Load or initialize config
        self.config = self._load_config()
        self.analyzer = DriveAnalyzer()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from disk"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")

        # Default configuration
        return {
            "version": "1.0.0",
            "buddies": {},
            "default_model": "qwen2.5-1.5b",
            "created_at": time.time(),
        }

    def _save_config(self):
        """Save configuration to disk"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def list_available_models(self) -> Dict[str, Dict]:
        """List available models for download

        Returns:
            Dictionary of model_id -> model_info
        """
        return self.MODEL_REGISTRY.copy()

    def create_buddy(self, name: str, watch_dir: Path, model_id: str) -> Dict[str, Any]:
        """Create a new buddy instance

        Args:
            name: Buddy name
            watch_dir: Directory for buddy to watch
            model_id: Model identifier

        Returns:
            Buddy configuration

        Raises:
            FileNotFoundError: If model file doesn't exist
        """
        # Check model exists
        model_path = self.models_dir / f"{model_id}.gguf"
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_id} not found at {model_path}")

        # Create buddy directory
        buddy_dir = self.buddies_dir / name
        buddy_dir.mkdir(exist_ok=True)

        # Create configuration
        buddy_config = {
            "name": name,
            "watch_dir": str(watch_dir),
            "buddy_dir": str(buddy_dir),
            "model_path": str(model_path),
            "model_id": model_id,
            "mesh_enabled": False,
            "created_at": time.time(),
            "personality": self._generate_initial_personality(name),
        }

        # Save to main config
        self.config["buddies"][name] = buddy_config
        self._save_config()

        return buddy_config

    def _generate_initial_personality(self, name: str) -> Dict[str, Any]:
        """Generate initial personality traits for a new buddy

        Args:
            name: Buddy name

        Returns:
            Personality configuration
        """
        arcs = [
            "amnesiac-detective",
            "grumpy-janitor",
            "lost-librarian",
            "ship-AI-in-recovery",
            "digital-archaeologist",
            "chaos-organizer",
        ]

        specialties = [
            "photo organization",
            "document management",
            "project coordination",
            "download cleanup",
            "duplicate detection",
            "creative file naming",
        ]

        return {
            "name": name,
            "humor": random.randint(3, 9),
            "curiosity": random.randint(4, 10),
            "formality": random.randint(2, 8),
            "empathy": random.randint(3, 9),
            "proactiveness": random.randint(2, 8),
            "narrative_arc": random.choice(arcs),
            "specialties": random.sample(specialties, random.randint(1, 3)),
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform system health check

        Returns:
            Health status with issues and recommendations
        """
        issues = []
        recommendations = []

        # Check disk space
        try:
            drive_info = self.analyzer.get_drive_info(str(self.install_dir))
            if drive_info["free_gb"] < 1.0:
                issues.append("Low disk space (< 1GB free)")
                recommendations.append("Free up disk space or move to larger drive")
            elif drive_info["free_gb"] < 2.0:
                recommendations.append("Consider freeing up disk space")
        except Exception as e:
            issues.append(f"Unable to check disk space: {e}")

        # Check RAM
        try:
            ram_info = self.analyzer.get_ram_info()
            if ram_info["available_gb"] < 2.0:
                issues.append("Low available RAM (< 2GB)")
                recommendations.append("Close other applications to free memory")
        except Exception as e:
            issues.append(f"Unable to check RAM: {e}")

        # Check models directory
        if not self.models_dir.exists():
            issues.append("Models directory missing")
            recommendations.append("Reinstall application")

        # Determine overall status
        if len(issues) >= 2:
            status = "unhealthy"
        elif len(issues) == 1:
            status = "warning"
        else:
            status = "healthy"

        return {
            "system": status,
            "issues": issues,
            "recommendations": recommendations,
            "disk_free_gb": drive_info.get("free_gb") if "drive_info" in dir() else None,
            "ram_available_gb": (ram_info.get("available_gb") if "ram_info" in dir() else None),
        }

    def get_buddy(self, name: str) -> Dict[str, Any]:
        """Get buddy configuration by name

        Args:
            name: Buddy name

        Returns:
            Buddy configuration or None
        """
        return self.config.get("buddies", {}).get(name)

    def list_buddies(self) -> Dict[str, Dict]:
        """List all configured buddies

        Returns:
            Dictionary of buddy_name -> buddy_config
        """
        return self.config.get("buddies", {}).copy()


if __name__ == "__main__":
    # Demo usage
    import tempfile

    print("🚀 Bit Buddy Deployment Manager Demo\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        manager = BuddyDeploymentManager(Path(temp_dir))

        print("📦 Available Models:")
        for model_id, info in manager.list_available_models().items():
            print(f"  - {model_id}: {info['description']} ({info['size_mb']}MB)")

        print("\n🏥 System Health Check:")
        health = manager.health_check()
        print(f"  Status: {health['system']}")
        if health["issues"]:
            print(f"  Issues: {', '.join(health['issues'])}")
        if health["recommendations"]:
            print(f"  Recommendations: {', '.join(health['recommendations'])}")
