#!/usr/bin/env python3
"""
Parallel Execution Performance Tests
Testing system performance under concurrent load with parallel operations
"""

import pytest
import time
import threading
import concurrent.futures
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, '/Users/tarive/brain-system-organized/core')

from simple_brain import SimpleBrain
from goal_keeper import GoalKeeper


class TestParallelExecution:
    """Test parallel execution performance and reliability"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain_dirs = []
        for i in range(10):
            brain_dir = Path(self.temp_dir) / f"brain_{i}"
            brain_dir.mkdir()
            self.brain_dirs.append(brain_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.performance
    @pytest.mark.concurrent
    def test_parallel_memory_storage_performance(self):
        """Test: Parallel memory storage meets performance requirements"""
        self.setUp()

        def store_memories_worker(brain_dir, worker_id, num_operations=50):
            """Worker function to store memories in parallel"""
            brain = SimpleBrain(str(brain_dir))
            times = []
            errors = []

            try:
                for i in range(num_operations):
                    start_time = time.time()
                    result = brain.store(
                        f"Worker {worker_id} memory {i}: Important information for testing parallel storage",
                        importance=5,
                        project=f"parallel_test_{worker_id}"
                    )
                    end_time = time.time()

                    if "success" in result.lower():
                        times.append(end_time - start_time)
                    else:
                        errors.append(f"Storage failed: {result}")

                    # Small delay to simulate real usage
                    time.sleep(0.01)

            except Exception as e:
                errors.append(str(e))
            finally:
                if hasattr(brain, 'conn') and brain.conn:
                    brain.conn.close()

            return {
                'worker_id': worker_id,
                'times': times,
                'errors': errors,
                'avg_time': sum(times) / len(times) if times else float('inf'),
                'success_rate': len(times) / num_operations * 100
            }

        # Run parallel workers
        num_workers = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            start_time = time.time()

            for i in range(num_workers):
                future = executor.submit(
                    store_memories_worker,
                    self.brain_dirs[i],
                    i,
                    25  # 25 operations per worker = 200 total
                )
                futures.append(future)

            results = []
            for future in concurrent.futures.as_completed(futures, timeout=60):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Worker failed with exception: {e}")

        total_time = time.time() - start_time

        # Analyze results
        total_operations = sum(len(r['times']) for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        avg_operation_time = sum(r['avg_time'] for r in results) / len(results)
        overall_success_rate = (total_operations / (num_workers * 25)) * 100

        # Performance assertions
        assert total_operations >= 180, f"Expected at least 180 successful operations, got {total_operations}"
        assert total_errors <= 20, f"Too many errors: {total_errors} (max 20 allowed)"
        assert avg_operation_time < 0.5, f"Average operation time too slow: {avg_operation_time}s (max 0.5s)"
        assert overall_success_rate >= 90, f"Success rate too low: {overall_success_rate}% (min 90%)"
        assert total_time < 45, f"Total execution time too slow: {total_time}s (max 45s)"

        # Print performance summary
        print(f"\nParallel Storage Performance Summary:")
        print(f"Total operations: {total_operations}")
        print(f"Total errors: {total_errors}")
        print(f"Average operation time: {avg_operation_time:.3f}s")
        print(f"Success rate: {overall_success_rate:.1f}%")
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Throughput: {total_operations/total_time:.1f} ops/sec")

        self.tearDown()

    @pytest.mark.performance
    @pytest.mark.concurrent
    def test_parallel_search_performance(self):
        """Test: Parallel search operations maintain performance"""
        self.setUp()

        # First, populate one brain with test data
        setup_brain = SimpleBrain(str(self.brain_dirs[0]))
        test_queries = []

        # Create test data with known search terms
        for i in range(100):
            content = f"Test content {i}: machine learning artificial intelligence data science {i % 10}"
            setup_brain.store(content, importance=i % 10, project=f"test_project_{i % 5}")
            if i % 10 == 0:
                test_queries.append(f"machine learning {i}")

        setup_brain.conn.close()

        def search_worker(brain_dir, worker_id, queries, num_searches=20):
            """Worker function to perform search operations"""
            brain = SimpleBrain(str(brain_dir))
            times = []
            errors = []

            try:
                for i in range(num_searches):
                    query = queries[i % len(queries)]
                    start_time = time.time()

                    try:
                        results = brain.search(query)
                        end_time = time.time()

                        times.append(end_time - start_time)

                        # Verify search returned results
                        if not results or len(results) == 0:
                            errors.append(f"No results for query: {query}")

                    except Exception as e:
                        errors.append(f"Search error: {str(e)}")

                    time.sleep(0.005)  # Small delay

            except Exception as e:
                errors.append(f"Worker error: {str(e)}")
            finally:
                if hasattr(brain, 'conn') and brain.conn:
                    brain.conn.close()

            return {
                'worker_id': worker_id,
                'times': times,
                'errors': errors,
                'avg_time': sum(times) / len(times) if times else float('inf'),
                'success_rate': len(times) / num_searches * 100
            }

        # Run parallel search workers
        num_workers = 6
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            start_time = time.time()

            for i in range(num_workers):
                future = executor.submit(
                    search_worker,
                    self.brain_dirs[0],  # All workers search the same populated brain
                    i,
                    test_queries,
                    15  # 15 searches per worker = 90 total
                )
                futures.append(future)

            results = []
            for future in concurrent.futures.as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Search worker failed: {e}")

        total_time = time.time() - start_time

        # Analyze search performance
        total_searches = sum(len(r['times']) for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        avg_search_time = sum(r['avg_time'] for r in results) / len(results)
        overall_success_rate = (total_searches / (num_workers * 15)) * 100

        # Performance assertions for search
        assert total_searches >= 80, f"Expected at least 80 successful searches, got {total_searches}"
        assert total_errors <= 10, f"Too many search errors: {total_errors} (max 10 allowed)"
        assert avg_search_time < 0.2, f"Average search time too slow: {avg_search_time}s (max 0.2s)"
        assert overall_success_rate >= 85, f"Search success rate too low: {overall_success_rate}% (min 85%)"
        assert total_time < 20, f"Total search time too slow: {total_time}s (max 20s)"

        print(f"\nParallel Search Performance Summary:")
        print(f"Total searches: {total_searches}")
        print(f"Total errors: {total_errors}")
        print(f"Average search time: {avg_search_time:.3f}s")
        print(f"Success rate: {overall_success_rate:.1f}%")
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Search throughput: {total_searches/total_time:.1f} searches/sec")

        self.tearDown()

    @pytest.mark.performance
    @pytest.mark.concurrent
    def test_mixed_operations_parallel_performance(self):
        """Test: Mixed read/write operations maintain performance under parallel load"""
        self.setUp()

        def mixed_operations_worker(brain_dir, worker_id, num_operations=30):
            """Worker performing mixed read/write operations"""
            brain = SimpleBrain(str(brain_dir))
            operation_times = {'store': [], 'search': [], 'context': []}
            errors = []

            try:
                for i in range(num_operations):
                    operation_type = ['store', 'search', 'context'][i % 3]
                    start_time = time.time()

                    try:
                        if operation_type == 'store':
                            result = brain.store(
                                f"Worker {worker_id} operation {i}: Mixed operation test data",
                                importance=i % 10,
                                project=f"mixed_test_{worker_id}"
                            )
                            if "success" not in result.lower():
                                errors.append(f"Store failed: {result}")

                        elif operation_type == 'search':
                            results = brain.search(f"Worker {worker_id}")
                            if not isinstance(results, list):
                                errors.append(f"Search returned invalid format: {type(results)}")

                        elif operation_type == 'context':
                            context = brain.get_context()
                            if not isinstance(context, dict):
                                errors.append(f"Context returned invalid format: {type(context)}")

                        end_time = time.time()
                        operation_times[operation_type].append(end_time - start_time)

                    except Exception as e:
                        errors.append(f"{operation_type} error: {str(e)}")

                    time.sleep(0.01)  # Simulate realistic usage

            except Exception as e:
                errors.append(f"Worker {worker_id} critical error: {str(e)}")
            finally:
                if hasattr(brain, 'conn') and brain.conn:
                    brain.conn.close()

            return {
                'worker_id': worker_id,
                'operation_times': operation_times,
                'errors': errors,
                'total_operations': sum(len(times) for times in operation_times.values())
            }

        # Run mixed operations with multiple workers
        num_workers = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            start_time = time.time()

            for i in range(num_workers):
                future = executor.submit(
                    mixed_operations_worker,
                    self.brain_dirs[i],
                    i,
                    24  # 24 operations per worker = 120 total
                )
                futures.append(future)

            results = []
            for future in concurrent.futures.as_completed(futures, timeout=45):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Mixed operations worker failed: {e}")

        total_time = time.time() - start_time

        # Aggregate performance data
        all_store_times = []
        all_search_times = []
        all_context_times = []
        total_errors = []
        total_operations = 0

        for result in results:
            all_store_times.extend(result['operation_times']['store'])
            all_search_times.extend(result['operation_times']['search'])
            all_context_times.extend(result['operation_times']['context'])
            total_errors.extend(result['errors'])
            total_operations += result['total_operations']

        # Calculate averages
        avg_store_time = sum(all_store_times) / len(all_store_times) if all_store_times else 0
        avg_search_time = sum(all_search_times) / len(all_search_times) if all_search_times else 0
        avg_context_time = sum(all_context_times) / len(all_context_times) if all_context_times else 0

        # Performance assertions
        assert total_operations >= 100, f"Expected at least 100 operations, got {total_operations}"
        assert len(total_errors) <= 20, f"Too many errors: {len(total_errors)} (max 20 allowed)"
        assert avg_store_time < 0.3, f"Store operations too slow: {avg_store_time:.3f}s (max 0.3s)"
        assert avg_search_time < 0.15, f"Search operations too slow: {avg_search_time:.3f}s (max 0.15s)"
        assert avg_context_time < 0.1, f"Context operations too slow: {avg_context_time:.3f}s (max 0.1s)"
        assert total_time < 35, f"Total execution too slow: {total_time:.2f}s (max 35s)"

        # Success rate calculation
        expected_operations = num_workers * 24
        success_rate = (total_operations / expected_operations) * 100
        assert success_rate >= 85, f"Success rate too low: {success_rate:.1f}% (min 85%)"

        print(f"\nMixed Operations Performance Summary:")
        print(f"Total operations: {total_operations}")
        print(f"Store operations: {len(all_store_times)} (avg: {avg_store_time:.3f}s)")
        print(f"Search operations: {len(all_search_times)} (avg: {avg_search_time:.3f}s)")
        print(f"Context operations: {len(all_context_times)} (avg: {avg_context_time:.3f}s)")
        print(f"Total errors: {len(total_errors)}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Overall throughput: {total_operations/total_time:.1f} ops/sec")

        self.tearDown()


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])