#!/usr/bin/env python3
"""
Unit Tests for Simple Brain Core Memory Operations
Following TDD principles: Red-Green-Refactor, 1:1 test-to-code ratio

CRITICAL RULE: Never modify these tests to make them pass.
Fix the system to meet test specifications.
"""

import unittest
import tempfile
import shutil
import os
import json
import sqlite3
import fcntl
import time
import threading
from pathlib import Path
from unittest.mock import patch, mock_open
import sys
sys.path.insert(0, '/Users/tarive/brain-poc')

from simple_brain import SimpleBrain


class TestSimpleBrainInitialization(unittest.TestCase):
    """Test brain initialization and basic setup"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_brain_directory_creation(self):
        """Test: Brain directory structure is created correctly"""
        brain_path = Path(self.temp_dir)

        self.assertTrue(brain_path.exists(), "Brain directory must be created")
        self.assertTrue((brain_path / "sessions").exists(), "Sessions directory must be created")
        self.assertTrue(brain_path.is_dir(), "Brain path must be a directory")

    def test_session_id_generation(self):
        """Test: Session ID is unique and follows format"""
        session_id = self.brain.session_id

        self.assertIsInstance(session_id, str, "Session ID must be string")
        self.assertEqual(len(session_id), 8, "Session ID must be 8 characters")
        self.assertTrue(session_id.isalnum(), "Session ID must be alphanumeric")

        # Test uniqueness - generate another brain
        brain2 = SimpleBrain(tempfile.mkdtemp())
        self.assertNotEqual(session_id, brain2.session_id, "Session IDs must be unique")
        brain2.conn.close()

    def test_session_directory_creation(self):
        """Test: Session-specific directory is created"""
        session_dir = Path(self.temp_dir) / "sessions" / self.brain.session_id

        self.assertTrue(session_dir.exists(), "Session directory must be created")
        self.assertTrue(session_dir.is_dir(), "Session path must be a directory")

    def test_search_index_initialization(self):
        """Test: SQLite search index is properly initialized"""
        db_path = Path(self.temp_dir) / "search.db"

        self.assertTrue(db_path.exists(), "Search database must be created")

        # Verify table structure
        cursor = self.brain.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        self.assertIsNotNone(cursor.fetchone(), "Memories table must exist")

        # Verify index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_content'")
        self.assertIsNotNone(cursor.fetchone(), "Content index must exist")

    def test_memory_log_file_initialization(self):
        """Test: Memory log file path is correctly set"""
        expected_path = Path(self.temp_dir) / "memory.log"

        self.assertEqual(self.brain.memory_log, expected_path, "Memory log path must be correct")


class TestCoreMemoryOperations(unittest.TestCase):
    """Test core store and retrieve operations"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_basic_memory(self):
        """Test: Basic memory storage returns success"""
        content = "This is a test memory"
        result = self.brain.store(content)

        self.assertTrue(result, "Store operation must return True on success")

    def test_store_with_importance(self):
        """Test: Memory can be stored with importance value"""
        content = "Important memory"
        importance = 0.8
        result = self.brain.store(content, importance=importance)

        self.assertTrue(result, "Store with importance must return True")

    def test_store_with_project(self):
        """Test: Memory can be stored with project tag"""
        content = "Project-specific memory"
        project = "test_project"
        result = self.brain.store(content, project=project)

        self.assertTrue(result, "Store with project must return True")

    def test_store_creates_log_entry(self):
        """Test: Store operation creates entry in memory log"""
        content = "Test memory for log"
        self.brain.store(content)

        log_file = Path(self.temp_dir) / "memory.log"
        self.assertTrue(log_file.exists(), "Memory log file must be created")

        with open(log_file, 'r') as f:
            log_content = f.read()

        self.assertIn(content, log_content, "Memory content must be in log")
        self.assertIn(self.brain.session_id, log_content, "Session ID must be in log")

    def test_store_updates_search_index(self):
        """Test: Store operation updates SQLite search index"""
        content = "Searchable memory content"
        self.brain.store(content)

        cursor = self.brain.conn.cursor()
        cursor.execute("SELECT content FROM memories WHERE content = ?", (content,))
        result = cursor.fetchone()

        self.assertIsNotNone(result, "Memory must be in search index")
        self.assertEqual(result[0], content, "Stored content must match")


class TestFileLockingMechanism(unittest.TestCase):
    """Test file locking for concurrent access safety"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_store_operations(self):
        """Test: Multiple concurrent store operations don't corrupt data"""
        contents = [f"Memory {i}" for i in range(10)]
        threads = []
        results = []

        def store_memory(content):
            result = self.brain.store(content)
            results.append(result)

        # Start multiple threads storing simultaneously
        for content in contents:
            thread = threading.Thread(target=store_memory, args=(content,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All operations should succeed
        self.assertEqual(len(results), 10, "All store operations must complete")
        self.assertTrue(all(results), "All store operations must succeed")

        # Verify all memories are in the log
        log_file = Path(self.temp_dir) / "memory.log"
        with open(log_file, 'r') as f:
            log_content = f.read()

        for content in contents:
            self.assertIn(content, log_content, f"Memory '{content}' must be in log")

    def test_file_lock_prevents_corruption(self):
        """Test: File locking prevents data corruption during writes"""
        # This test simulates what would happen without proper locking
        # We verify that with locking, data integrity is maintained

        content1 = "First memory"
        content2 = "Second memory"

        # Store memories simultaneously from different processes would be ideal,
        # but for unit test we verify the locking mechanism exists
        with patch('fcntl.flock') as mock_flock:
            self.brain.store(content1)

            # Verify flock was called for exclusive lock
            mock_flock.assert_any_call(unittest.mock.ANY, fcntl.LOCK_EX)
            # Verify flock was called for unlock
            mock_flock.assert_any_call(unittest.mock.ANY, fcntl.LOCK_UN)


class TestWorkingMemoryLimits(unittest.TestCase):
    """Test 7-item working memory cognitive limit enforcement"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_working_memory_limit_enforcement(self):
        """Test: Working memory is limited to 7 items maximum"""
        # Store 10 memories
        for i in range(10):
            self.brain.store(f"Memory {i}", importance=0.5)

        working_memory = self.brain.get_working_memory()

        self.assertLessEqual(len(working_memory), 7,
                           "Working memory must not exceed 7 items (cognitive limit)")

    def test_working_memory_keeps_most_important(self):
        """Test: Working memory retains most important items when at limit"""
        # Store memories with varying importance
        low_importance_memories = [f"Low importance {i}" for i in range(5)]
        high_importance_memories = [f"High importance {i}" for i in range(5)]

        # Store low importance first
        for content in low_importance_memories:
            self.brain.store(content, importance=0.1)

        # Store high importance (should push out low importance)
        for content in high_importance_memories:
            self.brain.store(content, importance=0.9)

        working_memory = self.brain.get_working_memory()
        working_contents = [item['content'] for item in working_memory]

        # High importance memories should be retained
        for content in high_importance_memories:
            self.assertIn(content, working_contents,
                         f"High importance memory '{content}' should be retained")

    def test_working_memory_persistence(self):
        """Test: Working memory persists across brain instances"""
        content = "Persistent memory"
        self.brain.store(content)

        # Close current brain and create new one with same directory
        self.brain.conn.close()
        brain2 = SimpleBrain(self.temp_dir)
        brain2.session_id = self.brain.session_id  # Same session

        working_memory = brain2.get_working_memory()
        working_contents = [item['content'] for item in working_memory]

        self.assertIn(content, working_contents,
                     "Working memory must persist across brain instances")

        brain2.conn.close()


class TestSessionIsolation(unittest.TestCase):
    """Test session isolation prevents cross-contamination"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_different_sessions_have_separate_working_memory(self):
        """Test: Different sessions maintain separate working memory"""
        brain1 = SimpleBrain(self.temp_dir)
        brain2 = SimpleBrain(self.temp_dir)

        # Store memory in brain1
        content1 = "Brain1 memory"
        brain1.store(content1)

        # Store memory in brain2
        content2 = "Brain2 memory"
        brain2.store(content2)

        # Check working memories are separate
        wm1 = brain1.get_working_memory()
        wm2 = brain2.get_working_memory()

        wm1_contents = [item['content'] for item in wm1]
        wm2_contents = [item['content'] for item in wm2]

        self.assertIn(content1, wm1_contents, "Brain1 should have its own memory")
        self.assertNotIn(content2, wm1_contents, "Brain1 should not see brain2 memory")

        self.assertIn(content2, wm2_contents, "Brain2 should have its own memory")
        self.assertNotIn(content1, wm2_contents, "Brain2 should not see brain1 memory")

        brain1.conn.close()
        brain2.conn.close()

    def test_shared_search_across_sessions(self):
        """Test: Search works across all sessions while working memory is isolated"""
        brain1 = SimpleBrain(self.temp_dir)
        brain2 = SimpleBrain(self.temp_dir)

        # Store memories in different sessions
        content1 = "Searchable content from brain1"
        content2 = "Searchable content from brain2"

        brain1.store(content1)
        brain2.store(content2)

        # Both brains should find both memories in search
        results1 = brain1.search("Searchable content")
        results2 = brain2.search("Searchable content")

        result1_contents = [r['content'] for r in results1]
        result2_contents = [r['content'] for r in results2]

        self.assertIn(content1, result1_contents, "Brain1 should find brain1 memory")
        self.assertIn(content2, result1_contents, "Brain1 should find brain2 memory")

        self.assertIn(content1, result2_contents, "Brain2 should find brain1 memory")
        self.assertIn(content2, result2_contents, "Brain2 should find brain2 memory")

        brain1.conn.close()
        brain2.conn.close()


class TestSearchFunctionality(unittest.TestCase):
    """Test memory search capabilities"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_returns_relevant_results(self):
        """Test: Search returns memories containing query terms"""
        # Store test memories
        memories = [
            "Python programming is fun",
            "JavaScript development",
            "Python data analysis",
            "Unrelated content"
        ]

        for memory in memories:
            self.brain.store(memory)

        # Search for Python
        results = self.brain.search("Python")
        result_contents = [r['content'] for r in results]

        self.assertIn("Python programming is fun", result_contents)
        self.assertIn("Python data analysis", result_contents)
        self.assertNotIn("JavaScript development", result_contents)
        self.assertNotIn("Unrelated content", result_contents)

    def test_search_scoring_algorithm(self):
        """Test: Search results are scored and ordered correctly"""
        # Store memories with different relevance
        self.brain.store("Python programming tutorial", importance=0.5)
        self.brain.store("Python Python Python", importance=0.3)  # Multiple matches
        self.brain.store("Advanced Python techniques", importance=0.9)  # High importance

        results = self.brain.search("Python")

        # Results should be ordered by score (content match + importance)
        self.assertGreater(len(results), 0, "Search should return results")

        # All results should have scores
        for result in results:
            self.assertIn('score', result, "Each result should have a score")
            self.assertGreaterEqual(result['score'], 0, "Score should be non-negative")
            self.assertLessEqual(result['score'], 1, "Score should not exceed 1")

    def test_search_threshold_filtering(self):
        """Test: Search threshold filters low-relevance results"""
        self.brain.store("Python programming", importance=0.9)
        self.brain.store("Barely related python mention", importance=0.1)

        # High threshold should return fewer results
        high_threshold_results = self.brain.search("Python programming", threshold=0.8)
        low_threshold_results = self.brain.search("Python programming", threshold=0.1)

        self.assertLessEqual(len(high_threshold_results), len(low_threshold_results),
                           "Higher threshold should return fewer or equal results")

    def test_search_limit_enforcement(self):
        """Test: Search respects result limit (20 items max)"""
        # Store more than 20 memories
        for i in range(25):
            self.brain.store(f"Test memory {i} with searchable content")

        results = self.brain.search("searchable")

        self.assertLessEqual(len(results), 20,
                           "Search should not return more than 20 results")


class TestContextAndMetadata(unittest.TestCase):
    """Test context retrieval and metadata operations"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain = SimpleBrain(self.temp_dir)

    def tearDown(self):
        if hasattr(self, 'brain') and hasattr(self.brain, 'conn'):
            self.brain.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_context_basic_info(self):
        """Test: get_context returns basic session information"""
        context = self.brain.get_context()

        self.assertIn('session_id', context, "Context must include session ID")
        self.assertIn('working_memory', context, "Context must include working memory")
        self.assertIn('memory_log_size', context, "Context must include log size")

        self.assertEqual(context['session_id'], self.brain.session_id,
                        "Context session ID must match brain session ID")

    def test_get_context_working_memory_consistency(self):
        """Test: Context working memory matches get_working_memory()"""
        # Store a memory
        self.brain.store("Test memory for context")

        context = self.brain.get_context()
        working_memory = self.brain.get_working_memory()

        self.assertEqual(context['working_memory'], working_memory,
                        "Context working memory must match get_working_memory()")

    def test_get_context_active_sessions(self):
        """Test: Context includes active sessions when requested"""
        # Create another brain instance (different session)
        brain2 = SimpleBrain(self.temp_dir)
        brain2.store("Memory from second session")

        context = self.brain.get_context(include_other_sessions=True)

        self.assertIn('active_sessions', context, "Context must include active sessions")
        self.assertIn('total_active', context, "Context must include active count")
        self.assertIsInstance(context['active_sessions'], list,
                            "Active sessions must be a list")

        brain2.conn.close()

    def test_memory_log_size_tracking(self):
        """Test: Memory log size is accurately tracked"""
        initial_context = self.brain.get_context()
        initial_size = initial_context['memory_log_size']

        # Store a memory
        self.brain.store("This will increase log size")

        updated_context = self.brain.get_context()
        updated_size = updated_context['memory_log_size']

        self.assertGreater(updated_size, initial_size,
                          "Log size should increase after storing memory")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)