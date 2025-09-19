#!/usr/bin/env python3
"""
Global pytest configuration and fixtures for Brain System testing
Provides shared test utilities and setup for all test categories
"""

import pytest
import tempfile
import shutil
import os
import sys
import time
import threading
from pathlib import Path
from typing import Generator, Any
from unittest.mock import patch, MagicMock

# Add core module to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

# Test configuration constants
TEST_TIMEOUT = 300  # 5 minutes default timeout
PERFORMANCE_TEST_TIMEOUT = 1800  # 30 minutes for performance tests
CONCURRENT_TEST_WORKERS = 4  # Number of concurrent test workers


@pytest.fixture(scope="session")
def test_session_config():
    """Session-wide test configuration"""
    return {
        "test_timeout": TEST_TIMEOUT,
        "performance_timeout": PERFORMANCE_TEST_TIMEOUT,
        "concurrent_workers": CONCURRENT_TEST_WORKERS,
        "test_start_time": time.time(),
    }


@pytest.fixture(scope="function")
def temp_dir():
    """Create and cleanup temporary directory for each test"""
    temp_path = tempfile.mkdtemp(prefix="brain_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def isolated_brain_dir():
    """Create isolated brain directory for testing"""
    temp_path = tempfile.mkdtemp(prefix="brain_isolated_")
    brain_dir = Path(temp_path) / "test_brain"
    brain_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable for isolation
    old_brain_dir = os.environ.get("BRAIN_DIR")
    os.environ["BRAIN_DIR"] = str(brain_dir)

    yield brain_dir

    # Cleanup
    if old_brain_dir:
        os.environ["BRAIN_DIR"] = old_brain_dir
    else:
        os.environ.pop("BRAIN_DIR", None)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_session_id():
    """Provide consistent session ID for testing"""
    test_session_id = "test_session_12345678"
    with patch.dict(os.environ, {"CLAUDE_SESSION_ID": test_session_id}):
        yield test_session_id


@pytest.fixture(scope="function")
def simple_brain(isolated_brain_dir, mock_session_id):
    """Create SimpleBrain instance for testing"""
    try:
        from simple_brain import SimpleBrain
        brain = SimpleBrain(str(isolated_brain_dir))
        yield brain
        # Cleanup database connection
        if hasattr(brain, 'conn') and brain.conn:
            brain.conn.close()
    except ImportError:
        pytest.skip("SimpleBrain not available for testing")


@pytest.fixture(scope="function")
def goal_keeper(isolated_brain_dir):
    """Create GoalKeeper instance for testing"""
    try:
        from goal_keeper import GoalKeeper
        keeper = GoalKeeper(str(isolated_brain_dir))
        yield keeper
    except ImportError:
        pytest.skip("GoalKeeper not available for testing")


@pytest.fixture(scope="function")
def concurrent_test_environment():
    """Setup environment for concurrent testing"""
    def run_concurrent_operation(func, *args, **kwargs):
        """Helper to run operations concurrently"""
        results = []
        errors = []
        threads = []

        def worker():
            try:
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        for _ in range(CONCURRENT_TEST_WORKERS):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)

        return results, errors

    yield run_concurrent_operation


@pytest.fixture(scope="function")
def mock_mcp_environment():
    """Mock MCP server environment for testing"""
    mcp_mocks = {
        "basic_memory_available": True,
        "gmail_mcp_available": True,
        "apple_reminders_available": True,
    }

    def mock_subprocess_run(*args, **kwargs):
        command = args[0] if args else kwargs.get('args', [])
        if isinstance(command, list) and len(command) > 0:
            if command[0] == 'which' and command[1] == 'basic-memory':
                return MagicMock(returncode=0 if mcp_mocks["basic_memory_available"] else 1)
            elif 'basic-memory' in command:
                return MagicMock(returncode=0, stdout="OK", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch('subprocess.run', side_effect=mock_subprocess_run):
        yield mcp_mocks


@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor performance metrics during tests"""
    import psutil

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = time.time()
            self.start_memory = psutil.virtual_memory().used
            self.peak_memory = self.start_memory

        def checkpoint(self, name: str):
            current_time = time.time()
            current_memory = psutil.virtual_memory().used
            self.peak_memory = max(self.peak_memory, current_memory)

            return {
                "checkpoint": name,
                "elapsed_time": current_time - self.start_time,
                "memory_used": current_memory - self.start_memory,
                "peak_memory": self.peak_memory - self.start_memory,
                "cpu_percent": psutil.cpu_percent(interval=None),
            }

        def get_final_stats(self):
            return self.checkpoint("final")

    monitor = PerformanceMonitor()
    yield monitor


@pytest.fixture(scope="function")
def database_cleanup():
    """Ensure database cleanup after tests"""
    db_connections = []

    def register_connection(conn):
        db_connections.append(conn)
        return conn

    yield register_connection

    # Cleanup all registered connections
    for conn in db_connections:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "facebook_reliability: Tests that validate Facebook-scale reliability standards"
    )
    config.addinivalue_line(
        "markers", "concurrent: Tests involving concurrent operations"
    )
    config.addinivalue_line(
        "markers", "mcp: Tests involving MCP server coordination"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers"""
    for item in items:
        # Add slow marker to tests that take longer
        if "performance" in item.nodeid or "facebook_reliability" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Add concurrent marker to threading tests
        if "concurrent" in item.nodeid or "thread" in item.nodeid:
            item.add_marker(pytest.mark.concurrent)

        # Add mcp marker to MCP-related tests
        if "mcp" in item.nodeid or "coordination" in item.nodeid:
            item.add_marker(pytest.mark.mcp)


def pytest_runtest_setup(item):
    """Setup before each test"""
    # Skip tests that require specific markers in certain environments
    if item.get_closest_marker("facebook_reliability"):
        if not item.config.getoption("--run-facebook-tests", default=False):
            pytest.skip("Facebook reliability tests skipped (use --run-facebook-tests to enable)")


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-facebook-tests",
        action="store_true",
        default=False,
        help="Run Facebook-scale reliability tests"
    )
    parser.addoption(
        "--concurrent-workers",
        action="store",
        default=CONCURRENT_TEST_WORKERS,
        type=int,
        help="Number of concurrent test workers"
    )


@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation and cleanup"""
    # Store original environment
    original_env = dict(os.environ)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def pytest_sessionfinish(session, exitstatus):
    """Clean up after test session"""
    # Cleanup any remaining test artifacts
    test_dirs = Path("/tmp").glob("brain_test_*")
    for test_dir in test_dirs:
        try:
            if test_dir.is_dir():
                shutil.rmtree(test_dir, ignore_errors=True)
        except Exception:
            pass