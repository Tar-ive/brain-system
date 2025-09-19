#!/usr/bin/env python3
"""
Performance Tests for Facebook.com Reliability Standards
Testing "when Mark first created it" reliability metrics

TARGET METRICS:
- Uptime: 99.99% (52.56 minutes downtime per year max)
- Recovery Time: <60 seconds from any failure
- Data Loss: Zero under normal operation
- Error Rate: <0.1% for all user operations
- Response Time: <100ms for core operations

CRITICAL RULE: Never modify these tests to make them pass.
Fix the system to meet performance specifications.
"""

import unittest
import tempfile
import shutil
import time
import threading
import sqlite3
import json
import os
import sys
import psutil
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/Users/tarive/brain-poc')
from simple_brain import SimpleBrain
from goal_keeper import GoalKeeper


class TestFacebookReliabilityStandards(unittest.TestCase):
    """Test Facebook.com level reliability standards"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.start_time = time.time()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_response_time_under_100ms(self):
        """Test: Core operations complete in <100ms (Facebook standard)"""
        brain = SimpleBrain(self.temp_dir)
        response_times = []

        try:
            # Test memory storage response time
            for i in range(20):
                start = time.time()
                brain.store(f"Performance test memory {i}", importance=0.5)
                end = time.time()
                response_times.append((end - start) * 1000)  # Convert to milliseconds

            # Test search response time
            search_times = []
            for i in range(20):
                start = time.time()
                brain.search("Performance test")
                end = time.time()
                search_times.append((end - start) * 1000)

            # Test working memory retrieval time
            working_memory_times = []
            for i in range(20):
                start = time.time()
                brain.get_working_memory()
                end = time.time()
                working_memory_times.append((end - start) * 1000)

            # Facebook.com standard: <100ms for core operations
            avg_store_time = statistics.mean(response_times)
            avg_search_time = statistics.mean(search_times)
            avg_working_memory_time = statistics.mean(working_memory_times)

            self.assertLess(avg_store_time, 100,
                           f"Average store time {avg_store_time:.2f}ms must be <100ms")
            self.assertLess(avg_search_time, 100,
                           f"Average search time {avg_search_time:.2f}ms must be <100ms")
            self.assertLess(avg_working_memory_time, 50,
                           f"Average working memory time {avg_working_memory_time:.2f}ms must be <50ms")

            # 95th percentile should also be reasonable
            p95_store = sorted(response_times)[int(0.95 * len(response_times))]
            self.assertLess(p95_store, 200,
                           f"95th percentile store time {p95_store:.2f}ms must be <200ms")

        finally:
            brain.conn.close()

    def test_concurrent_operation_performance(self):
        """Test: Performance under concurrent load (Facebook scale requirement)"""
        num_threads = 10
        operations_per_thread = 50
        error_count = 0
        completion_times = []

        def worker_function(thread_id):
            """Worker function for concurrent testing"""
            thread_brain = SimpleBrain(self.temp_dir)
            thread_errors = 0
            thread_times = []

            try:
                for i in range(operations_per_thread):
                    start = time.time()

                    # Mix of operations
                    if i % 3 == 0:
                        thread_brain.store(f"Thread {thread_id} memory {i}")
                    elif i % 3 == 1:
                        thread_brain.search(f"Thread {thread_id}")
                    else:
                        thread_brain.get_working_memory()

                    end = time.time()
                    thread_times.append((end - start) * 1000)

            except Exception as e:
                thread_errors += 1
                print(f"Thread {thread_id} error: {e}")
            finally:
                thread_brain.conn.close()

            return thread_errors, thread_times

        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_function, i) for i in range(num_threads)]

            for future in as_completed(futures):
                thread_errors, thread_times = future.result()
                error_count += thread_errors
                completion_times.extend(thread_times)

        # Facebook reliability standards
        total_operations = num_threads * operations_per_thread
        error_rate = error_count / total_operations

        self.assertLess(error_rate, 0.001,  # <0.1% error rate
                       f"Error rate {error_rate:.3%} must be <0.1%")

        if completion_times:
            avg_concurrent_time = statistics.mean(completion_times)
            self.assertLess(avg_concurrent_time, 200,
                           f"Average concurrent operation time {avg_concurrent_time:.2f}ms must be <200ms")

    def test_memory_usage_efficiency(self):
        """Test: Memory usage stays within reasonable bounds under load"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        brain = SimpleBrain(self.temp_dir)
        memory_measurements = []

        try:
            # Store many memories and measure memory growth
            for i in range(1000):
                brain.store(f"Memory efficiency test {i}" * 10,  # Larger content
                           importance=0.5, project=f"project_{i % 10}")

                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_measurements.append(current_memory)

            final_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory

            # Memory growth should be reasonable for 1000 memories
            self.assertLess(memory_growth, 100,  # <100MB growth for 1000 memories
                           f"Memory growth {memory_growth:.2f}MB should be <100MB for 1000 memories")

            # Memory usage should be relatively stable (no major leaks)
            if len(memory_measurements) > 2:
                memory_growth_rate = (memory_measurements[-1] - memory_measurements[0]) / len(memory_measurements)
                self.assertLess(memory_growth_rate, 10,  # <10MB per 100 operations
                               f"Memory growth rate {memory_growth_rate:.2f}MB per 100 ops should be <10MB")

        finally:
            brain.conn.close()

    def test_database_performance_under_load(self):
        """Test: SQLite database performance under Facebook-scale load"""
        brain = SimpleBrain(self.temp_dir)
        search_times = []

        try:
            # Create a substantial dataset
            for i in range(1000):
                brain.store(f"Database performance test item {i} with content about {i % 20} different topics",
                           importance=i / 1000, project=f"perf_project_{i % 5}")

            # Test search performance on loaded database
            search_queries = [
                "performance test",
                "item",
                "content",
                "topics",
                "database",
                "different",
                "500",  # Specific number
                "perf_project_1"  # Specific project
            ]

            for query in search_queries:
                for _ in range(10):  # Multiple searches per query
                    start = time.time()
                    results = brain.search(query)
                    end = time.time()

                    search_times.append((end - start) * 1000)

                    # Results should be reasonable
                    self.assertLessEqual(len(results), 20,
                                       "Search results should be limited to 20")

            # Search performance should remain good even with 1000 entries
            avg_search_time = statistics.mean(search_times)
            p95_search_time = sorted(search_times)[int(0.95 * len(search_times))]

            self.assertLess(avg_search_time, 50,
                           f"Average search time {avg_search_time:.2f}ms should be <50ms with 1000 entries")
            self.assertLess(p95_search_time, 100,
                           f"95th percentile search time {p95_search_time:.2f}ms should be <100ms")

        finally:
            brain.conn.close()

    def test_file_system_performance(self):
        """Test: File system operations meet performance requirements"""
        brain = SimpleBrain(self.temp_dir)
        file_operation_times = []

        try:
            # Test working memory file operations
            for i in range(100):
                start = time.time()

                # This triggers working memory file write
                brain.store(f"File system performance test {i}")

                # Force working memory read
                brain.get_working_memory()

                end = time.time()
                file_operation_times.append((end - start) * 1000)

            avg_file_time = statistics.mean(file_operation_times)
            max_file_time = max(file_operation_times)

            # File operations should be fast
            self.assertLess(avg_file_time, 20,
                           f"Average file operation time {avg_file_time:.2f}ms should be <20ms")
            self.assertLess(max_file_time, 100,
                           f"Maximum file operation time {max_file_time:.2f}ms should be <100ms")

        finally:
            brain.conn.close()

    def test_session_management_performance(self):
        """Test: Session management scales efficiently"""
        session_creation_times = []
        session_switch_times = []

        # Test session creation performance
        for i in range(50):
            start = time.time()
            brain = SimpleBrain(self.temp_dir)
            end = time.time()
            session_creation_times.append((end - start) * 1000)

            # Test session ID changes
            old_session = brain.session_id
            start = time.time()
            brain.session_id = f"test_session_{i}"
            end = time.time()
            session_switch_times.append((end - start) * 1000)

            brain.conn.close()

        avg_creation_time = statistics.mean(session_creation_times)
        avg_switch_time = statistics.mean(session_switch_times)

        self.assertLess(avg_creation_time, 50,
                       f"Average session creation time {avg_creation_time:.2f}ms should be <50ms")
        self.assertLess(avg_switch_time, 10,
                       f"Average session switch time {avg_switch_time:.2f}ms should be <10ms")

    def test_recovery_time_standard(self):
        """Test: System recovers in <60 seconds after simulated failure"""
        brain = SimpleBrain(self.temp_dir)

        # Store some data
        brain.store("Recovery test data before failure")
        original_session = brain.session_id

        # Simulate system restart by closing and recreating
        brain.conn.close()

        recovery_start = time.time()

        # Simulate recovery
        recovered_brain = SimpleBrain(self.temp_dir)

        # Verify data is still accessible
        search_results = recovered_brain.search("Recovery test data")
        self.assertGreater(len(search_results), 0,
                         "Data must be recoverable after restart")

        # Verify new operations work
        recovered_brain.store("Recovery test data after restart")
        new_search_results = recovered_brain.search("Recovery test")

        recovery_end = time.time()
        recovery_time = recovery_end - recovery_start

        # Facebook standard: <60 seconds recovery time
        self.assertLess(recovery_time, 60,
                       f"Recovery time {recovery_time:.2f}s must be <60 seconds")

        # Verify full functionality after recovery
        self.assertGreaterEqual(len(new_search_results), 2,
                               "Both pre and post-recovery data should be found")

        recovered_brain.conn.close()

    def test_zero_data_loss_guarantee(self):
        """Test: Zero data loss under normal operation (Facebook requirement)"""
        brain = SimpleBrain(self.temp_dir)
        stored_memories = []

        try:
            # Store many memories with unique identifiers
            for i in range(200):
                content = f"Data loss test memory {i} with unique identifier {i}_{time.time()}"
                brain.store(content, importance=i / 200)
                stored_memories.append(content)

            # Verify all memories are immediately searchable
            for i, memory in enumerate(stored_memories):
                search_results = brain.search(f"unique identifier {i}_", threshold=0.3)
                self.assertGreater(len(search_results), 0,
                                 f"Memory {i} must be immediately searchable after storage")

            # Simulate system stress and verify no data loss
            brain.conn.close()
            recovered_brain = SimpleBrain(self.temp_dir)

            # Verify all data is still present
            all_results = recovered_brain.search("Data loss test memory", threshold=0.3, limit=300)
            self.assertGreaterEqual(len(all_results), 200,
                                   "All 200 memories must be recoverable (zero data loss)")

            # Verify data integrity
            for i in range(0, 200, 10):  # Sample every 10th memory
                search_results = recovered_brain.search(f"unique identifier {i}_", threshold=0.3)
                self.assertGreater(len(search_results), 0,
                                 f"Memory {i} must be intact with unique identifier")

            recovered_brain.conn.close()

        finally:
            brain.conn.close()

    def test_error_rate_below_facebook_standard(self):
        """Test: Error rate <0.1% under normal operation"""
        total_operations = 1000
        errors = 0
        brain = SimpleBrain(self.temp_dir)

        try:
            for i in range(total_operations):
                try:
                    # Mix of normal operations
                    if i % 4 == 0:
                        brain.store(f"Error rate test {i}")
                    elif i % 4 == 1:
                        brain.search("error rate")
                    elif i % 4 == 2:
                        brain.get_working_memory()
                    else:
                        brain.get_context()

                except Exception as e:
                    errors += 1
                    print(f"Operation {i} failed: {e}")

            error_rate = errors / total_operations

            # Facebook standard: <0.1% error rate
            self.assertLess(error_rate, 0.001,
                           f"Error rate {error_rate:.3%} must be <0.1%")

        finally:
            brain.conn.close()


class TestGoalKeeperPerformance(unittest.TestCase):
    """Test GoalKeeper performance under Facebook reliability standards"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_goal_keeper_response_time(self):
        """Test: GoalKeeper operations complete quickly"""
        keeper = GoalKeeper()
        operation_times = []

        # Test win logging performance
        for i in range(50):
            start = time.time()
            keeper.log_win("brain_system", f"Performance test win {i}")
            end = time.time()
            operation_times.append((end - start) * 1000)

        # Test blocker logging performance
        for i in range(20):
            start = time.time()
            keeper.log_blocker("brain_system", f"Performance test blocker {i}")
            end = time.time()
            operation_times.append((end - start) * 1000)

        # Test daily check performance
        for i in range(10):
            start = time.time()
            keeper.daily_check()
            end = time.time()
            operation_times.append((end - start) * 1000)

        avg_time = statistics.mean(operation_times)
        max_time = max(operation_times)

        self.assertLess(avg_time, 100,
                       f"Average GoalKeeper operation time {avg_time:.2f}ms should be <100ms")
        self.assertLess(max_time, 500,
                       f"Maximum GoalKeeper operation time {max_time:.2f}ms should be <500ms")

    def test_goal_keeper_concurrent_access(self):
        """Test: GoalKeeper handles concurrent access safely"""
        num_threads = 5
        operations_per_thread = 20

        def worker_goal_operations(thread_id):
            keeper = GoalKeeper()
            for i in range(operations_per_thread):
                if i % 2 == 0:
                    keeper.log_win("brain_system", f"Thread {thread_id} win {i}")
                else:
                    keeper.log_blocker("brain_system", f"Thread {thread_id} blocker {i}")

        # Execute concurrent goal operations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_goal_operations, i) for i in range(num_threads)]

            # All should complete without errors
            for future in as_completed(futures):
                future.result()  # This will raise if there were exceptions

        # Verify data integrity after concurrent operations
        final_keeper = GoalKeeper()
        daily_report = final_keeper.daily_check()

        # Should contain information from all threads
        self.assertIn("BRAIN_SYSTEM", daily_report.upper())


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)