#!/usr/bin/env python3
"""
Bit Buddy Deployment Manager - Easy setup and management tools
"""

import asyncio
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List

import requests


class BuddyDeploymentManager:
    """Manages bit buddy installation, models, and deployment"""

    def __init__(self, install_dir: Path = None):
        self.install_dir = install_dir or Path.home() / ".bit_buddies"
        self.models_dir = self.install_dir / "models"
        self.buddies_dir = self.install_dir / "buddies"
        self.config_file = self.install_dir / "config.json"

        # Create directories
        for dir_path in [self.install_dir, self.models_dir, self.buddies_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)

        # Load configuration
        self.config = self._load_config()

        # Model registry
        self.model_registry = {
            "qwen2.5-1.5b": {
                "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
                "size_mb": 934,
                "description": "Qwen2.5 1.5B - Great balance of capability and speed",
                "ram_requirement": "2GB",
                "recommended": True,
            },
            "tinyllama-1.1b": {
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf",
                "size_mb": 669,
                "description": "TinyLlama 1.1B - Ultra-fast, minimal resources",
                "ram_requirement": "1.5GB",
                "recommended": False,
            },
            "phi3.5-mini": {
                "url": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-q4.gguf",
                "size_mb": 2300,
                "description": "Phi-3.5 Mini - Microsoft's efficient model",
                "ram_requirement": "3GB",
                "recommended": True,
            },
        }

    def _load_config(self) -> Dict:
        """Load deployment configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                # Ignore config read errors and fall back to defaults
                pass

        # Default config
        return {
            "version": "1.0.0",
            "default_model": "qwen2.5-1.5b",
            "auto_start": False,
            "mesh_enabled": True,
            "mesh_port_range": [8000, 8100],
            "buddies": {},
        }

    def _save_config(self):
        """Save deployment configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def list_available_models(self) -> Dict:
        """List all available models for download"""
        return self.model_registry

    def list_installed_models(self) -> List[Dict]:
        """List currently installed models"""
        installed = []

        for model_id, model_info in self.model_registry.items():
            model_path = self.models_dir / f"{model_id}.gguf"
            if model_path.exists():
                installed.append(
                    {
                        "id": model_id,
                        "path": str(model_path),
                        "size_mb": model_path.stat().st_size / (1024 * 1024),
                        "description": model_info["description"],
                    }
                )

        return installed

    async def download_model(
        self, model_id: str, progress_callback=None
    ) -> Path:
        """Download and install a model"""
        if model_id not in self.model_registry:
            raise ValueError(f"Unknown model: {model_id}")

        model_info = self.model_registry[model_id]
        model_path = self.models_dir / f"{model_id}.gguf"

        if model_path.exists():
            print(f"✅ Model {model_id} already installed")
            return model_path

        print(f"📥 Downloading {model_id} ({model_info['size_mb']}MB)...")

        # Download with progress
        response = requests.get(model_info["url"], stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded, total_size)
                    elif total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(
                            f"\r  Progress: {progress:.1f}%",
                            end="",
                            flush=True,
                        )

        print(f"\n✅ Downloaded {model_id} to {model_path}")
        return model_path

    def create_buddy(
        self,
        name: str,
        watch_dir: Path,
        model_id: str = None,
        mesh_enabled: bool = True,
        debug_mode: bool = False,
    ) -> Dict:
        """Create a new bit buddy"""
        if not model_id:
            model_id = self.config["default_model"]

        # Validate model
        model_path = self.models_dir / f"{model_id}.gguf"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model {model_id} not installed. Run: deploy.py download-model {model_id}"
            )

        # Create buddy directory
        buddy_dir = self.buddies_dir / name.lower().replace(" ", "_")
        buddy_dir.mkdir(exist_ok=True)

        # Create buddy config
        buddy_config = {
            "name": name,
            "watch_dir": str(watch_dir),
            "model_path": str(model_path),
            "buddy_dir": str(buddy_dir),
            "mesh_enabled": mesh_enabled,
            "debug_mode": debug_mode,
            "created_at": __import__("time").time(),
            "personality": self._generate_initial_personality(name),
        }

        # Save buddy config
        config_path = buddy_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(buddy_config, f, indent=2)

        # Update main config
        self.config["buddies"][name] = buddy_config
        self._save_config()

        print(f"✅ Created bit buddy '{name}' watching {watch_dir}")
        return buddy_config

    def _generate_initial_personality(self, name: str) -> Dict:
        """Generate initial personality for new buddy"""
        import random

        # Name-based personality seeds
        name_lower = name.lower()

        # Base traits
        traits = {
            "temperature": random.uniform(0.3, 0.9),
            "humor": random.randint(1, 10),
            "curiosity": random.randint(3, 10),
            "formality": random.randint(1, 8),
            "empathy": random.randint(4, 10),
        }

        # Name-influenced traits
        if any(
            word in name_lower for word in ["tech", "code", "dev", "pixel"]
        ):
            traits["specialties"] = ["programming", "technical_docs"]
            traits["curiosity"] += 2
        elif any(word in name_lower for word in ["art", "creative", "design"]):
            traits["specialties"] = ["visual_content", "creative_projects"]
            traits["humor"] += 2
        elif any(word in name_lower for word in ["doc", "write", "text"]):
            traits["specialties"] = ["documents", "text_files"]
            traits["formality"] += 1
        else:
            traits["specialties"] = ["general_files", "organization"]

        # Clamp values
        for key in ["humor", "curiosity", "formality", "empathy"]:
            traits[key] = max(1, min(10, traits[key]))

        return traits

    def list_buddies(self) -> List[Dict]:
        """List all created buddies"""
        buddies = []

        for name, config in self.config["buddies"].items():
            buddy_dir = Path(config["buddy_dir"])
            status = (
                "active"
                if (buddy_dir / "personality.json").exists()
                else "inactive"
            )

            buddies.append(
                {
                    "name": name,
                    "watch_dir": config["watch_dir"],
                    "model": Path(config["model_path"]).stem,
                    "status": status,
                    "created_at": config.get("created_at", 0),
                }
            )

        return buddies

    def start_buddy(self, name: str, port: int = None) -> subprocess.Popen:
        """Start a bit buddy as background process"""
        if name not in self.config["buddies"]:
            raise ValueError(f"Buddy '{name}' not found")

        buddy_config = self.config["buddies"][name]

        # Create startup script
        startup_code = f"""
import asyncio
import sys
sys.path.insert(0, "{Path(__file__).parent}")

from enhanced_buddy import EnhancedBitBuddy
from mesh_network import BuddyMeshNetwork
from pathlib import Path

async def main():
    buddy = EnhancedBitBuddy(
        buddy_dir=Path("{buddy_config['buddy_dir']}"),
        watch_dir=Path("{buddy_config['watch_dir']}"),
        model_path=Path("{buddy_config['model_path']}") if "{buddy_config['model_path']}" else None
    )

    if {buddy_config.get('mesh_enabled', True)}:
        mesh = BuddyMeshNetwork(buddy, {port or 0})
        buddy.mesh = mesh
        await mesh.start_server()

    print(f"🤖 {{buddy.personality.name}} is now watching {{buddy.watch_dir}}")
    print(f"🌐 Mesh network: {{'enabled' if {buddy_config.get('mesh_enabled', True)} else 'disabled'}}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        if hasattr(buddy, 'mesh'):
            await buddy.mesh.shutdown()
        print(f"\\n👋 {{buddy.personality.name}} shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
"""

        # Write startup script
        script_path = Path(buddy_config["buddy_dir"]) / "start.py"
        with open(script_path, "w") as f:
            f.write(startup_code)

        # Start process
        process = subprocess.Popen(
            [sys.executable, str(script_path)], cwd=buddy_config["buddy_dir"]
        )

        print(f"🚀 Started buddy '{name}' (PID: {process.pid})")
        return process

    def stop_buddy(self, name: str):
        """Stop a running buddy"""
        # TODO: Implement proper process management
        print(
            f"⏹️  Stopping buddy '{name}' (use Ctrl+C in the buddy's terminal)"
        )

    def setup_auto_start(self):
        """Setup buddies to auto-start on system boot"""
        # TODO: Platform-specific auto-start implementation
        print("🔧 Auto-start setup not yet implemented")

    def health_check(self) -> Dict:
        """Check system health and requirements"""
        health = {"system": "healthy", "issues": [], "recommendations": []}

        # Check Python version
        if sys.version_info < (3, 8):
            health["issues"].append("Python 3.8+ required")
            health["system"] = "unhealthy"

        # Check dependencies
        required_packages = [
            "requests",
            "chromadb",
            "sentence-transformers",
            "watchdog",
            "fastapi",
            "uvicorn",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            health["issues"].append(
                f"Missing packages: {', '.join(missing_packages)}"
            )
            health["recommendations"].append(
                "Run: pip install -r requirements.txt"
            )

        # Check available RAM
        try:
            import psutil

            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            if available_ram_gb < 2:
                health["issues"].append(
                    f"Low RAM: {available_ram_gb:.1f}GB available"
                )
                health["recommendations"].append(
                    "Consider using TinyLlama model for low-RAM systems"
                )
        except ImportError:
            health["recommendations"].append(
                "Install psutil for system monitoring"
            )

        # Check disk space
        available_space_gb = shutil.disk_usage(self.install_dir).free / (
            1024**3
        )
        if available_space_gb < 5:
            health["issues"].append(
                f"Low disk space: {available_space_gb:.1f}GB available"
            )
            health["recommendations"].append(
                "Free up disk space or change install directory"
            )

        if health["issues"]:
            health["system"] = (
                "warning" if len(health["issues"]) == 1 else "unhealthy"
            )

        return health

    def cleanup_old_models(self):
        """Remove unused model files"""
        # Find models not referenced by any buddy
        used_models = set()
        for buddy_config in self.config["buddies"].values():
            model_path = Path(buddy_config["model_path"])
            used_models.add(model_path.name)

        # Remove unused models
        removed_count = 0
        for model_file in self.models_dir.glob("*.gguf"):
            if model_file.name not in used_models:
                print(f"🗑️  Removing unused model: {model_file.name}")
                model_file.unlink()
                removed_count += 1

        print(f"✅ Cleaned up {removed_count} unused models")

    def export_buddy(self, name: str, export_path: Path):
        """Export a buddy configuration for sharing"""
        if name not in self.config["buddies"]:
            raise ValueError(f"Buddy '{name}' not found")

        buddy_config = self.config["buddies"][name]
        buddy_dir = Path(buddy_config["buddy_dir"])

        # Create export package
        with zipfile.ZipFile(export_path, "w") as zf:
            # Add buddy config (without absolute paths)
            export_config = buddy_config.copy()
            export_config["model_path"] = Path(
                export_config["model_path"]
            ).name
            export_config["buddy_dir"] = "."

            zf.writestr("config.json", json.dumps(export_config, indent=2))

            # Add personality and experience files
            for file_name in ["personality.json", "experience.json"]:
                file_path = buddy_dir / file_name
                if file_path.exists():
                    zf.write(file_path, file_name)

        print(f"📦 Exported buddy '{name}' to {export_path}")

    def import_buddy(
        self, import_path: Path, new_name: str = None, watch_dir: Path = None
    ):
        """Import a buddy from export package"""
        with zipfile.ZipFile(import_path, "r") as zf:
            # Read config
            config_data = zf.read("config.json")
            imported_config = json.loads(config_data.decode())

            # Set new name and directories
            buddy_name = new_name or imported_config["name"]
            buddy_dir = self.buddies_dir / buddy_name.lower().replace(" ", "_")
            buddy_dir.mkdir(exist_ok=True)

            # Update config
            imported_config["name"] = buddy_name
            imported_config["buddy_dir"] = str(buddy_dir)
            if watch_dir:
                imported_config["watch_dir"] = str(watch_dir)

            # Extract files
            zf.extractall(buddy_dir)

            # Update main config
            self.config["buddies"][buddy_name] = imported_config
            self._save_config()

        print(f"📥 Imported buddy '{buddy_name}' from {import_path}")


def main():
    """CLI interface for deployment manager"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bit Buddy Deployment Manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Health check
    subparsers.add_parser("health", help="Check system health")

    # List models
    subparsers.add_parser("list-models", help="List available models")
    subparsers.add_parser("installed-models", help="List installed models")

    # Download model
    download_parser = subparsers.add_parser(
        "download-model", help="Download a model"
    )
    download_parser.add_argument("model_id", help="Model ID to download")

    # Create buddy
    create_parser = subparsers.add_parser(
        "create-buddy", help="Create new buddy"
    )
    create_parser.add_argument("name", help="Buddy name")
    create_parser.add_argument("watch_dir", help="Directory to watch")
    create_parser.add_argument("--model", help="Model ID to use")
    create_parser.add_argument(
        "--no-mesh", action="store_true", help="Disable mesh networking"
    )
    create_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )

    # List buddies
    subparsers.add_parser("list-buddies", help="List all buddies")

    # Start buddy
    start_parser = subparsers.add_parser("start-buddy", help="Start a buddy")
    start_parser.add_argument("name", help="Buddy name")
    start_parser.add_argument("--port", type=int, help="Mesh port")

    # Cleanup
    subparsers.add_parser("cleanup", help="Remove unused models")

    # Testing and debugging
    test_parser = subparsers.add_parser("test", help="Run test suite")
    test_parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "all"],
        default="unit",
        help="Type of tests to run",
    )
    test_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    debug_parser = subparsers.add_parser("debug", help="Debug a buddy")
    debug_parser.add_argument("name", help="Buddy name to debug")
    debug_parser.add_argument("--operation", help="Specific operation to test")

    # Export/Import
    export_parser = subparsers.add_parser(
        "export-buddy", help="Export buddy configuration"
    )
    export_parser.add_argument("name", help="Buddy name")
    export_parser.add_argument("export_path", help="Export file path")

    import_parser = subparsers.add_parser(
        "import-buddy", help="Import buddy configuration"
    )
    import_parser.add_argument("import_path", help="Import file path")
    import_parser.add_argument("--name", help="New buddy name")
    import_parser.add_argument("--watch-dir", help="Directory to watch")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create deployment manager
    manager = BuddyDeploymentManager()

    try:
        if args.command == "health":
            health = manager.health_check()
            print(f"🏥 System Health: {health['system'].upper()}")

            if health["issues"]:
                print("\n⚠️  Issues:")
                for issue in health["issues"]:
                    print(f"  • {issue}")

            if health["recommendations"]:
                print("\n💡 Recommendations:")
                for rec in health["recommendations"]:
                    print(f"  • {rec}")

        elif args.command == "list-models":
            models = manager.list_available_models()
            print("📋 Available Models:")
            for model_id, info in models.items():
                status = "✅" if info.get("recommended") else "⚪"
                print(f"  {status} {model_id}")
                print(f"      {info['description']}")
                print(
                    f"      Size: {info['size_mb']}MB, RAM: {info['ram_requirement']}"
                )
                print()

        elif args.command == "installed-models":
            models = manager.list_installed_models()
            if models:
                print("📦 Installed Models:")
                for model in models:
                    print(f"  ✅ {model['id']} ({model['size_mb']:.1f}MB)")
                    print(f"      {model['description']}")
            else:
                print("📦 No models installed")

        elif args.command == "download-model":
            asyncio.run(manager.download_model(args.model_id))

        elif args.command == "create-buddy":
            manager.create_buddy(
                name=args.name,
                watch_dir=Path(args.watch_dir),
                model_id=args.model,
                mesh_enabled=not args.no_mesh,
                debug_mode=args.debug,
            )

        elif args.command == "list-buddies":
            buddies = manager.list_buddies()
            if buddies:
                print("🤖 Your Bit Buddies:")
                for buddy in buddies:
                    status_emoji = (
                        "🟢" if buddy["status"] == "active" else "⚪"
                    )
                    print(
                        f"  {status_emoji} {buddy['name']} ({buddy['model']})"
                    )
                    print(f"      Watching: {buddy['watch_dir']}")
            else:
                print("🤖 No buddies created yet")

        elif args.command == "start-buddy":
            process = manager.start_buddy(args.name, args.port)
            print("🎯 Buddy started! Press Ctrl+C to stop.")
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
                print("\n👋 Buddy stopped")

        elif args.command == "cleanup":
            manager.cleanup_old_models()

        elif args.command == "export-buddy":
            manager.export_buddy(args.name, Path(args.export_path))

        elif args.command == "import-buddy":
            manager.import_buddy(
                Path(args.import_path),
                args.name,
                Path(args.watch_dir) if args.watch_dir else None,
            )

        elif args.command == "test":
            # Run tests
            try:
                from test_runner import TestRunner

                runner = TestRunner()

                if args.type == "unit":
                    runner.run_unit_tests(args.verbose)
                elif args.type == "integration":
                    runner.run_integration_tests(args.verbose)
                elif args.type == "performance":
                    runner.run_performance_tests(args.verbose)
                elif args.type == "all":
                    runner.run_all_tests(verbose=args.verbose)

            except ImportError:
                print(
                    "❌ Test runner not available. Install with: pip install pytest pytest-asyncio"
                )

        elif args.command == "debug":
            # Debug a specific buddy
            if args.name not in manager.config["buddies"]:
                print(f"❌ Buddy '{args.name}' not found")
                return 1

            try:
                from debug_tools import quick_debug_buddy
                from enhanced_buddy import EnhancedBitBuddy

                buddy_config = manager.config["buddies"][args.name]
                buddy = EnhancedBitBuddy(
                    buddy_dir=Path(buddy_config["buddy_dir"]),
                    watch_dir=Path(buddy_config["watch_dir"]),
                    model_path=(
                        Path(buddy_config["model_path"])
                        if buddy_config["model_path"]
                        else None
                    ),
                    debug_mode=True,
                )

                _report = quick_debug_buddy(buddy, args.operation)
                print("\n📋 Debug report generated")

            except ImportError:
                print("❌ Debug tools not available")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
