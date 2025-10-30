#!/usr/bin/env python3
"""
Pre-Build Test Suite
Tests all components before building the production executable
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class PreBuildTester:
    """Run comprehensive pre-build tests"""

    def __init__(self):
        self.results = []
        self.errors = []
        self.root = PROJECT_ROOT

    def test(self, name, func):
        """Run a test and record result"""
        print(f"\n🧪 Testing: {name}")
        try:
            result = func()
            if result:
                print(f"✅ PASS: {name}")
                self.results.append({"test": name, "status": "pass"})
                return True
            else:
                print(f"❌ FAIL: {name}")
                self.results.append({"test": name, "status": "fail"})
                return False
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   {str(e)}")
            self.errors.append({"test": name, "error": str(e)})
            self.results.append({"test": name, "status": "error"})
            return False

    def test_imports(self):
        """Test that all critical modules can be imported"""
        imports = [
            "fastapi",
            "uvicorn",
            "fastembed",
            "numpy",
            "yaml",
            "pypdf",
            "docx2txt",
            "tkinter",
            "PIL",
            "psutil",
        ]

        failed = []
        for module in imports:
            try:
                __import__(module)
            except ImportError as e:
                failed.append(f"{module}: {e}")

        if failed:
            print(f"   Missing: {', '.join(failed)}")
            return False
        return True

    def test_config_files(self):
        """Test that all config files exist and are valid"""
        config_files = [
            self.root / "app/config.yaml",
            self.root / "custodian/manifest.yaml",
            self.root / "custodian/policy.yaml",
            self.root / "custodian/peers.json",
        ]

        missing = [str(f.relative_to(self.root)) for f in config_files if not f.exists()]
        if missing:
            print(f"   Missing: {', '.join(missing)}")
            return False

        return True

    def test_icon_files(self):
        """Test that icon files were generated"""
        icon_files = [
            self.root / "assets/buddy_icon.png",
            self.root / "assets/buddy_icon.ico",
        ]

        missing = [str(f.relative_to(self.root)) for f in icon_files if not f.exists()]
        if missing:
            print(f"   Missing: {', '.join(missing)}")
            return False
        return True

    def test_pyinstaller_spec(self):
        """Test that PyInstaller spec file exists"""
        spec_file = self.root / "build/config/buddy.spec"
        if not spec_file.exists():
            print(f"   Missing: {spec_file.relative_to(self.root)}")
            return False
        return True

    def test_gui_import(self):
        """Test that GUI module imports successfully"""
        try:
            import buddy_gui

            # Check that main class exists
            if not hasattr(buddy_gui, "BuddyGUI"):
                print("   BuddyGUI class not found")
                return False
            return True
        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_installer_import(self):
        """Test that installer module imports successfully"""
        try:
            import installer

            # Check that main classes exist
            if not hasattr(installer, "DriveAnalyzer"):
                print("   DriveAnalyzer class not found")
                return False
            if not hasattr(installer, "InstallationPlanner"):
                print("   InstallationPlanner class not found")
                return False
            return True
        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_server_health(self):
        """Test that server module can be imported and has endpoints"""
        try:
            from app import server

            # Check that FastAPI app exists
            if not hasattr(server, "app"):
                print("   FastAPI app not found")
                return False

            # Check that required endpoints exist
            routes = [route.path for route in server.app.routes]
            required = ["/", "/health", "/chat", "/reindex"]

            missing = [r for r in required if r not in routes]
            if missing:
                print(f"   Missing routes: {', '.join(missing)}")
                return False

            return True
        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_rag_module(self):
        """Test that RAG module imports and has required functions"""
        try:
            from app import rag

            # Check that RAG class exists
            if not hasattr(rag, "RAG"):
                print("   RAG class not found")
                return False

            # Check that config loader exists
            if not hasattr(rag, "load_config"):
                print("   load_config function not found")
                return False

            return True
        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_persona_module(self):
        """Test that persona module imports and works"""
        try:
            from app import persona  # noqa: F401

            # Just verify it imports - it uses functions not classes
            return True
        except Exception as e:
            print(f"   Error: {e}")
            return False

    def test_requirements(self):
        """Test that requirements.txt exists and is valid"""
        req_file = self.root / "requirements.txt"
        if not req_file.exists():
            print(f"   Missing: {req_file.relative_to(self.root)}")
            return False

        with open(req_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 5:
                print("   requirements.txt seems incomplete")
                return False

        return True

    def test_documentation(self):
        """Test that key documentation files exist"""
        docs = [
            self.root / "README.md",
            self.root / "PROJECT_STRUCTURE.md",
            self.root / "docs/user/END_USER_GUIDE.md",
            self.root / "docs/build/BUILD_INSTRUCTIONS.md",
        ]

        missing = [str(d.relative_to(self.root)) for d in docs if not d.exists()]
        if missing:
            print(f"   Missing: {', '.join(missing)}")
            return False
        return True

    def test_directory_structure(self):
        """Test that required directories exist"""
        dirs = [
            self.root / "app",
            self.root / "custodian",
            self.root / "assets",
            self.root / "scripts",
            self.root / "docs",
            self.root / "build",
            self.root / "tools",
        ]

        missing = [str(d.relative_to(self.root)) for d in dirs if not d.is_dir()]
        if missing:
            print(f"   Missing: {', '.join(missing)}")
            return False
        return True

    def run_all_tests(self):
        """Run all pre-build tests"""
        print("=" * 60)
        print("🚀 PRE-BUILD TEST SUITE")
        print("=" * 60)

        # Run all tests
        self.test("Directory Structure", self.test_directory_structure)
        self.test("Configuration Files", self.test_config_files)
        self.test("Icon Files", self.test_icon_files)
        self.test("PyInstaller Spec", self.test_pyinstaller_spec)
        self.test("Requirements File", self.test_requirements)
        self.test("Documentation", self.test_documentation)
        self.test("Critical Imports", self.test_imports)
        self.test("GUI Module", self.test_gui_import)
        self.test("Installer Module", self.test_installer_import)
        self.test("Server Module", self.test_server_health)
        self.test("RAG Module", self.test_rag_module)
        self.test("Persona Module", self.test_persona_module)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        errors = sum(1 for r in self.results if r["status"] == "error")
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")

        if errors > 0:
            print("\n🔥 ERRORS:")
            for error in self.errors:
                print(f"   - {error['test']}: {error['error']}")

        print("\n" + "=" * 60)

        if passed == total:
            print("🎉 ALL TESTS PASSED - READY TO BUILD!")
            print("\n📦 Next steps:")
            print("   1. Build executable: pyinstaller buddy.spec")
            print(
                "   2. Test executable: dist/BitBuddy or dist/BitBuddy.exe"
            )  # noqa: E501
            print(
                "   3. Create installer (Windows): iscc BitBuddyInstaller.iss"
            )  # noqa: E501
            return True
        else:
            print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE BUILDING")
            print("\n🔧 Fix the issues above and run again:")
            print("   python pre_build_test.py")
            return False


def main():
    """Main entry point"""
    tester = PreBuildTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
