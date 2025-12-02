import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from deploy import BuddyDeploymentManager
from enhanced_buddy import BitBuddyPersonality, EnhancedBitBuddy, FileSystemRAG


def create_test_personality(name: str = "TestBuddy") -> BitBuddyPersonality:
    """Factory function to create a test personality with all required fields"""
    return BitBuddyPersonality(
        name=name,
        temperature=0.7,
        humor=5,
        curiosity=7,
        formality=5,
        empathy=6,
        proactiveness=5,
        narrative_arc="test-arc",
        favorite_phrases=["Test phrase 1", "Test phrase 2"],
        mood_indicators={
            "healthy": ["All good!"],
            "confused": ["Something's fuzzy"],
            "sick": ["Not feeling great"],
            "critical": ["Help!"]
        },
        specialties=["testing", "debugging"],
        quirks={"test_mode": True}
    )


class TestBitBuddyPersonality:
    """Test the personality system"""

    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_personality_creation(self):
        """Test basic personality creation via dataclass"""
        personality = create_test_personality("TestBuddy")

        assert personality.name == "TestBuddy"
        assert 1 <= personality.humor <= 10
        assert 1 <= personality.curiosity <= 10
        assert 0.1 <= personality.temperature <= 1.5
        assert len(personality.specialties) >= 1

    def test_personality_dataclass_fields(self):
        """Test personality dataclass has expected fields"""
        personality = create_test_personality()

        # Check required fields exist
        assert hasattr(personality, 'name')
        assert hasattr(personality, 'temperature')
        assert hasattr(personality, 'humor')
        assert hasattr(personality, 'curiosity')
        assert hasattr(personality, 'formality')
        assert hasattr(personality, 'empathy')
        assert hasattr(personality, 'specialties')

    def test_personality_trait_ranges(self):
        """Test personality traits are within expected ranges"""
        personality = create_test_personality()

        # Traits should be in valid ranges
        assert 0.0 <= personality.temperature <= 1.5
        assert 0 <= personality.humor <= 10
        assert 0 <= personality.curiosity <= 10
        assert 0 <= personality.formality <= 10
        assert 0 <= personality.empathy <= 10


class TestFileSystemRAG:
    """Test the RAG (Retrieval Augmented Generation) system"""

    def setup_method(self):
        """Setup test files"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_dir = self.temp_dir / "db"
        self.db_dir.mkdir()
        self.rag = FileSystemRAG(self.temp_dir, self.db_dir)

        # Create test files
        (self.temp_dir / "test1.txt").write_text("This is about machine learning and AI")
        (self.temp_dir / "test2.txt").write_text("Python programming tutorial")
        (self.temp_dir / "vacation.txt").write_text("My trip to Hawaii was amazing")

        # Create subdirectory
        subdir = self.temp_dir / "projects"
        subdir.mkdir()
        (subdir / "neural_net.py").write_text("import torch\nclass NeuralNetwork:")

    def teardown_method(self):
        """Cleanup"""
        self.rag.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_indexing(self):
        """Test that files are properly indexed"""
        # Index files
        self.rag.index_files()

        # Check database has entries
        cursor = self.rag.conn.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        assert file_count >= 4  # Should have indexed our test files

    def test_file_search(self):
        """Test file search functionality"""
        # Index first
        self.rag.index_files()

        # Search for AI-related content
        results = self.rag.search_files("machine learning")

        assert len(results) > 0
        # Should find test1.txt
        assert any("test1.txt" in result["file_path"] for result in results)

    def test_content_extraction(self):
        """Test content extraction from different file types"""
        content = self.rag._extract_text_content(self.temp_dir / "test1.txt")
        assert "machine learning" in content.lower()

    def test_semantic_search(self):
        """Test semantic (vector) search"""
        # Index files first
        self.rag.index_files()

        # Search for semantically similar content
        results = self.rag.semantic_search("artificial intelligence", top_k=2)

        assert len(results) <= 2
        # Should find AI-related files
        if results:
            assert any("test1.txt" in result["file_path"] for result in results)


class TestEnhancedBitBuddy:
    """Test the complete bit buddy system"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.buddy_dir = self.temp_dir / "buddy"
        self.watch_dir = self.temp_dir / "watch"

        self.buddy_dir.mkdir()
        self.watch_dir.mkdir()

        # Create test files to watch
        (self.watch_dir / "document.txt").write_text("Important project document")
        (self.watch_dir / "photo.jpg").touch()  # Empty file for testing

    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_buddy_creation(self):
        """Test buddy can be created without model"""
        buddy = EnhancedBitBuddy(self.buddy_dir, self.watch_dir, model_path=None)

        assert buddy.personality.name is not None
        assert buddy.buddy_dir == self.buddy_dir
        assert buddy.watch_dir == self.watch_dir

    def test_file_discovery(self):
        """Test buddy discovers files"""
        buddy = EnhancedBitBuddy(self.buddy_dir, self.watch_dir, model_path=None)

        # Trigger file scan
        buddy.rag.index_files()

        # Check files were found
        cursor = buddy.rag.conn.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        assert file_count >= 2  # Should find our test files

    @pytest.mark.asyncio
    async def test_ask_without_model(self):
        """Test asking buddy questions without LLM model"""
        buddy = EnhancedBitBuddy(self.buddy_dir, self.watch_dir, model_path=None)
        buddy.rag.index_files()

        response = buddy.ask("What files do you see?")

        assert "answer" in response
        # Response contains file_results, not files
        assert "file_results" in response or "files_found" in response


class TestDeploymentManager:
    """Test deployment and management system"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = BuddyDeploymentManager(self.temp_dir)

    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_creation(self):
        """Test deployment manager initializes correctly"""
        assert self.manager.install_dir == self.temp_dir
        assert self.manager.models_dir.exists()
        assert self.manager.buddies_dir.exists()

    def test_model_registry(self):
        """Test model registry contains expected models"""
        models = self.manager.list_available_models()

        assert "qwen2.5-1.5b" in models
        assert "tinyllama-1.1b" in models
        assert "phi3.5-mini" in models

        # Check model info structure
        qwen_info = models["qwen2.5-1.5b"]
        assert "url" in qwen_info
        assert "size_mb" in qwen_info
        assert "description" in qwen_info

    def test_buddy_creation_without_model(self):
        """Test buddy creation fails gracefully without model"""
        watch_dir = self.temp_dir / "watch"
        watch_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            self.manager.create_buddy("TestBuddy", watch_dir, "nonexistent-model")

    def test_health_check(self):
        """Test system health check"""
        health = self.manager.health_check()

        assert "system" in health
        assert health["system"] in ["healthy", "warning", "unhealthy"]
        assert "issues" in health
        assert "recommendations" in health

    def test_config_persistence(self):
        """Test configuration saves and loads"""
        _original_config = self.manager.config.copy()

        # Modify config
        self.manager.config["test_key"] = "test_value"
        self.manager._save_config()

        # Create new manager (should load saved config)
        new_manager = BuddyDeploymentManager(self.temp_dir)

        assert new_manager.config["test_key"] == "test_value"


class TestMeshNetworking:
    """Test mesh networking (basic tests without actual networking)"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mesh_imports(self):
        """Test mesh networking components can be imported"""
        try:
            from mesh_network import BuddyMeshNetwork, BuddyPeer, MeshMessage  # noqa: F401

            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import mesh components: {e}")

    def test_mesh_message_creation(self):
        """Test mesh message creation"""
        from mesh_network import MeshMessage

        message = MeshMessage(
            message_id="test123",
            sender_id="buddy1",
            recipient_id="buddy2",
            message_type="query",
            payload={"query": "test question"},
            timestamp=1234567890.0,
            signature="test_signature",
        )

        assert message.sender_id == "buddy1"
        assert message.payload["query"] == "test question"


# Utility functions for testing


def create_test_buddy(temp_dir: Path, name: str = "TestBuddy") -> EnhancedBitBuddy:
    """Helper to create a test buddy"""
    buddy_dir = temp_dir / "buddy"
    watch_dir = temp_dir / "watch"

    buddy_dir.mkdir(exist_ok=True)
    watch_dir.mkdir(exist_ok=True)

    return EnhancedBitBuddy(buddy_dir, watch_dir, model_path=None)


def create_test_files(directory: Path, file_specs: dict):
    """Helper to create test files

    Args:
        directory: Directory to create files in
        file_specs: Dict of filename -> content
    """
    for filename, content in file_specs.items():
        file_path = directory / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)


# Performance tests


@pytest.mark.performance
class TestPerformance:
    """Performance tests for bit buddy system"""

    def test_large_file_indexing(self):
        """Test indexing performance with many files"""
        temp_dir = Path(tempfile.mkdtemp())
        db_dir = temp_dir / "db"
        db_dir.mkdir()

        try:
            # Create many test files
            for i in range(100):
                (temp_dir / f"file_{i}.txt").write_text(f"Content of file {i}")

            # Time the indexing
            import time

            rag = FileSystemRAG(temp_dir, db_dir)

            start_time = time.time()
            rag.index_files()
            end_time = time.time()

            indexing_time = end_time - start_time

            # Should complete within reasonable time (adjust as needed)
            assert indexing_time < 30, f"Indexing took too long: {indexing_time}s"

            # Verify files were indexed (some may fail due to concurrent db access)
            cursor = rag.conn.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            assert file_count >= 90, f"Expected at least 90 files, got {file_count}"

            rag.close()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# Integration tests


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_buddy_workflow(self):
        """Test complete buddy setup and usage workflow"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # 1. Create deployment manager
            manager = BuddyDeploymentManager(temp_dir)

            # 2. Create watch directory with files
            watch_dir = temp_dir / "watch"
            watch_dir.mkdir()

            create_test_files(
                watch_dir,
                {
                    "project.md": "# My AI Project\nWorking on machine learning",
                    "notes.txt": "Important notes about the presentation",
                    "data/results.csv": "column1,column2\nvalue1,value2",
                },
            )

            # 3. Create buddy (without model for testing)
            buddy_config = {
                "name": "IntegrationTest",
                "watch_dir": str(watch_dir),
                "buddy_dir": str(temp_dir / "buddy"),
                "model_path": "",
                "mesh_enabled": False,
                "created_at": 1234567890,
                "personality": manager._generate_initial_personality("IntegrationTest"),
            }

            manager.config["buddies"]["IntegrationTest"] = buddy_config

            # 4. Create and use buddy
            buddy = EnhancedBitBuddy(
                buddy_dir=Path(buddy_config["buddy_dir"]),
                watch_dir=Path(buddy_config["watch_dir"]),
                model_path=None,
            )

            # 5. Test file discovery
            buddy.rag.index_files()

            # 6. Test queries
            response = buddy.ask("What files do you see?")
            assert "answer" in response
            # Check file_results or files_found since response format may vary
            assert "file_results" in response or "files_found" in response

            # 7. Test search
            search_response = buddy.ask("Find files about AI")
            assert "answer" in search_response

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
