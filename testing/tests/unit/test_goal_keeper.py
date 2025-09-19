#!/usr/bin/env python3
"""
Unit Tests for Goal Keeper Anti-Abandonment System
Following TDD principles: Red-Green-Refactor, 1:1 test-to-code ratio

CRITICAL RULE: Never modify these tests to make them pass.
Fix the system to meet test specifications.
"""

import unittest
import tempfile
import shutil
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '/Users/tarive/brain-poc')

from goal_keeper import GoalKeeper


class TestGoalKeeperInitialization(unittest.TestCase):
    """Test Goal Keeper initialization and file structure"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Mock the hardcoded brain directory path
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"
            self.keeper.goals = self.keeper._load_goals()
            self.keeper.wins = self.keeper._load_wins()
            self.keeper.commitment = self.keeper._load_commitment()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_goals_structure(self):
        """Test: Default goals are properly structured"""
        self.assertIn('brain_system', self.keeper.goals,
                     "Default brain_system goal must exist")

        brain_goal = self.keeper.goals['brain_system']
        required_fields = ['started', 'status', 'excitement_level', 'days_worked',
                          'last_win', 'commitment', 'next_actions', 'blockers']

        for field in required_fields:
            self.assertIn(field, brain_goal,
                         f"Goal must have {field} field")

        self.assertEqual(brain_goal['status'], 'active',
                        "Default goal status must be active")
        self.assertEqual(brain_goal['excitement_level'], 10,
                        "Default excitement level must be 10")

    def test_default_commitment_structure(self):
        """Test: Default commitment contract is properly structured"""
        self.assertIn('brain_project', self.keeper.commitment,
                     "Default brain project commitment must exist")

        commitment = self.keeper.commitment['brain_project']
        required_fields = ['promise', 'signed', 'minimum_days', 'fallback_plan']

        for field in required_fields:
            self.assertIn(field, commitment,
                         f"Commitment must have {field} field")

        self.assertEqual(commitment['minimum_days'], 30,
                        "Minimum commitment must be 30 days")

    def test_empty_wins_initialization(self):
        """Test: Wins log initializes as empty list"""
        self.assertIsInstance(self.keeper.wins, list,
                             "Wins must be a list")
        self.assertEqual(len(self.keeper.wins), 0,
                        "Initial wins list must be empty")


class TestGoalManagement(unittest.TestCase):
    """Test goal addition and management"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"
            self.keeper.goals = {}
            self.keeper.wins = []
            self.keeper.commitment = {}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_goal_creates_proper_structure(self):
        """Test: Adding goal creates properly structured entry"""
        project = "test_project"
        goal = "Build amazing feature"
        why_excited = "It will change everything"

        result = self.keeper.add_goal(project, goal, why_excited)

        self.assertIn(project, self.keeper.goals,
                     "Project must be added to goals")

        goal_data = self.keeper.goals[project]
        self.assertEqual(goal_data['goal'], goal,
                        "Goal text must match input")
        self.assertEqual(goal_data['why_excited'], why_excited,
                        "Excitement reason must match input")
        self.assertEqual(goal_data['status'], 'active',
                        "New goal status must be active")
        self.assertEqual(goal_data['excitement_level'], 10,
                        "New goal excitement must be 10")
        self.assertEqual(goal_data['days_worked'], 0,
                        "New goal days worked must be 0")

        self.assertIn("Goal added", result,
                     "Add goal must return success message")

    def test_add_goal_saves_to_file(self):
        """Test: Adding goal persists to file"""
        project = "test_project"
        goal = "Test goal"
        why_excited = "Testing"

        with patch.object(self.keeper, '_save_goals') as mock_save:
            self.keeper.add_goal(project, goal, why_excited)
            mock_save.assert_called_once()


class TestWinLogging(unittest.TestCase):
    """Test win logging and excitement tracking"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"
            self.keeper.goals = {
                'test_project': {
                    'started': datetime.now().isoformat(),
                    'status': 'active',
                    'excitement_level': 5,
                    'days_worked': 0,
                    'last_win': None
                }
            }
            self.keeper.wins = []
            self.keeper.commitment = {}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_win_increases_excitement(self):
        """Test: Logging win increases excitement level"""
        initial_excitement = self.keeper.goals['test_project']['excitement_level']

        with patch.object(self.keeper, '_save_wins'), \
             patch.object(self.keeper, '_save_goals'):
            result = self.keeper.log_win('test_project', 'Fixed bug')

        final_excitement = self.keeper.goals['test_project']['excitement_level']

        self.assertGreater(final_excitement, initial_excitement,
                          "Win must increase excitement level")
        self.assertIn("WIN LOGGED", result,
                     "Win logging must return success message")

    def test_log_win_caps_excitement_at_10(self):
        """Test: Excitement level cannot exceed 10"""
        self.keeper.goals['test_project']['excitement_level'] = 9

        with patch.object(self.keeper, '_save_wins'), \
             patch.object(self.keeper, '_save_goals'):
            self.keeper.log_win('test_project', 'Major breakthrough', excitement_boost=5)

        final_excitement = self.keeper.goals['test_project']['excitement_level']

        self.assertLessEqual(final_excitement, 10,
                           "Excitement level must not exceed 10")

    def test_log_win_increments_days_worked(self):
        """Test: Logging win increments days worked counter"""
        initial_days = self.keeper.goals['test_project']['days_worked']

        with patch.object(self.keeper, '_save_wins'), \
             patch.object(self.keeper, '_save_goals'):
            self.keeper.log_win('test_project', 'Progress made')

        final_days = self.keeper.goals['test_project']['days_worked']

        self.assertEqual(final_days, initial_days + 1,
                        "Days worked must increment by 1")

    def test_log_win_updates_last_win_timestamp(self):
        """Test: Logging win updates last win timestamp"""
        self.assertIsNone(self.keeper.goals['test_project']['last_win'],
                         "Initial last win should be None")

        with patch.object(self.keeper, '_save_wins'), \
             patch.object(self.keeper, '_save_goals'):
            self.keeper.log_win('test_project', 'Achievement unlocked')

        last_win = self.keeper.goals['test_project']['last_win']

        self.assertIsNotNone(last_win, "Last win timestamp must be set")
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(last_win)

    def test_log_win_creates_win_entry(self):
        """Test: Logging win creates proper win entry"""
        win_description = "Solved complex problem"

        with patch.object(self.keeper, '_save_wins'), \
             patch.object(self.keeper, '_save_goals'):
            self.keeper.log_win('test_project', win_description)

        self.assertEqual(len(self.keeper.wins), 1,
                        "Win entry must be added to wins list")

        win_entry = self.keeper.wins[0]
        required_fields = ['project', 'win', 'timestamp', 'excitement_before', 'excitement_after']

        for field in required_fields:
            self.assertIn(field, win_entry,
                         f"Win entry must have {field} field")

        self.assertEqual(win_entry['project'], 'test_project',
                        "Win entry project must match")
        self.assertEqual(win_entry['win'], win_description,
                        "Win entry description must match")

    def test_log_win_nonexistent_project(self):
        """Test: Logging win for nonexistent project returns error"""
        result = self.keeper.log_win('nonexistent', 'Some win')

        self.assertIn("not found", result,
                     "Must return error for nonexistent project")


class TestBlockerManagement(unittest.TestCase):
    """Test blocker logging and resolution"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"
            self.keeper.goals = {
                'test_project': {
                    'started': datetime.now().isoformat(),
                    'status': 'active',
                    'excitement_level': 8,
                    'days_worked': 5,
                    'last_win': datetime.now().isoformat(),
                    'blockers': []
                }
            }
            self.keeper.wins = []
            self.keeper.commitment = {
                'test_project': {
                    'promise': 'Never give up on this project'
                }
            }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_blocker_decreases_excitement(self):
        """Test: Logging blocker decreases excitement level"""
        initial_excitement = self.keeper.goals['test_project']['excitement_level']

        with patch.object(self.keeper, '_save_goals'):
            self.keeper.log_blocker('test_project', 'API broke', severity=5)

        final_excitement = self.keeper.goals['test_project']['excitement_level']

        self.assertLess(final_excitement, initial_excitement,
                       "Blocker must decrease excitement level")

    def test_log_blocker_never_drops_below_threshold(self):
        """Test: Excitement never drops below commitment threshold (3)"""
        self.keeper.goals['test_project']['excitement_level'] = 4

        with patch.object(self.keeper, '_save_goals'):
            self.keeper.log_blocker('test_project', 'Major disaster', severity=10)

        final_excitement = self.keeper.goals['test_project']['excitement_level']

        self.assertGreaterEqual(final_excitement, 3,
                               "Excitement must not drop below commitment threshold")

    def test_log_blocker_creates_blocker_entry(self):
        """Test: Logging blocker creates proper blocker entry"""
        blocker_description = "Tests are failing"
        severity = 7

        with patch.object(self.keeper, '_save_goals'):
            result = self.keeper.log_blocker('test_project', blocker_description, severity)

        blockers = self.keeper.goals['test_project']['blockers']
        self.assertEqual(len(blockers), 1,
                        "Blocker entry must be added")

        blocker = blockers[0]
        required_fields = ['issue', 'severity', 'logged', 'resolved']

        for field in required_fields:
            self.assertIn(field, blocker,
                         f"Blocker entry must have {field} field")

        self.assertEqual(blocker['issue'], blocker_description,
                        "Blocker description must match")
        self.assertEqual(blocker['severity'], severity,
                        "Blocker severity must match")
        self.assertFalse(blocker['resolved'],
                        "New blocker must not be resolved")

        self.assertIn("BLOCKER LOGGED", result,
                     "Must return blocker logged message")

    def test_log_blocker_includes_anti_abandonment_message(self):
        """Test: Blocker logging includes anti-abandonment messaging"""
        with patch.object(self.keeper, '_save_goals'):
            result = self.keeper.log_blocker('test_project', 'Something broke')

        anti_abandonment_phrases = [
            "don't quit", "commitment", "invested", "Quick fixes"
        ]

        for phrase in anti_abandonment_phrases:
            self.assertIn(phrase.lower(), result.lower(),
                         f"Result must contain anti-abandonment phrase: {phrase}")

    def test_resolve_blocker_increases_excitement(self):
        """Test: Resolving blocker increases excitement level"""
        # Add a blocker first
        self.keeper.goals['test_project']['blockers'] = [{
            'issue': 'Test blocker',
            'severity': 5,
            'logged': datetime.now().isoformat(),
            'resolved': False
        }]

        initial_excitement = self.keeper.goals['test_project']['excitement_level']

        with patch.object(self.keeper, '_save_goals'):
            result = self.keeper.resolve_blocker('test_project')

        final_excitement = self.keeper.goals['test_project']['excitement_level']

        self.assertGreater(final_excitement, initial_excitement,
                          "Resolving blocker must increase excitement")
        self.assertIn("BLOCKER RESOLVED", result,
                     "Must return resolution success message")

    def test_resolve_blocker_marks_as_resolved(self):
        """Test: Resolving blocker properly marks it as resolved"""
        blocker = {
            'issue': 'Test blocker',
            'severity': 5,
            'logged': datetime.now().isoformat(),
            'resolved': False
        }
        self.keeper.goals['test_project']['blockers'] = [blocker]

        with patch.object(self.keeper, '_save_goals'):
            self.keeper.resolve_blocker('test_project')

        resolved_blocker = self.keeper.goals['test_project']['blockers'][0]

        self.assertTrue(resolved_blocker['resolved'],
                       "Blocker must be marked as resolved")
        self.assertIn('resolved_at', resolved_blocker,
                     "Blocker must have resolution timestamp")

    def test_resolve_blocker_no_blockers(self):
        """Test: Resolving blocker when none exist returns appropriate message"""
        self.keeper.goals['test_project']['blockers'] = []

        result = self.keeper.resolve_blocker('test_project')

        self.assertIn("No blockers", result,
                     "Must indicate no blockers to resolve")


class TestDailyAccountability(unittest.TestCase):
    """Test daily accountability and progress tracking"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"

            yesterday = datetime.now() - timedelta(days=1)
            self.keeper.goals = {
                'active_project': {
                    'started': yesterday.isoformat(),
                    'status': 'active',
                    'excitement_level': 6,
                    'days_worked': 1,
                    'last_win': yesterday.isoformat(),
                    'blockers': []
                },
                'inactive_project': {
                    'started': yesterday.isoformat(),
                    'status': 'paused',
                    'excitement_level': 4,
                    'days_worked': 0,
                    'last_win': None,
                    'blockers': []
                }
            }
            self.keeper.wins = []
            self.keeper.commitment = {}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_daily_check_only_processes_active_projects(self):
        """Test: Daily check only processes projects with active status"""
        with patch.object(self.keeper, '_save_goals'):
            report = self.keeper.daily_check()

        # Should mention active project but not inactive
        self.assertIn('ACTIVE_PROJECT', report,
                     "Daily check should include active project")
        self.assertNotIn('INACTIVE_PROJECT', report,
                        "Daily check should not include inactive project")

    def test_daily_check_decreases_excitement_for_stale_projects(self):
        """Test: Daily check decreases excitement for projects without recent wins"""
        # Set last win to 5 days ago (stale)
        five_days_ago = datetime.now() - timedelta(days=5)
        self.keeper.goals['active_project']['last_win'] = five_days_ago.isoformat()
        initial_excitement = self.keeper.goals['active_project']['excitement_level']

        with patch.object(self.keeper, '_save_goals'):
            self.keeper.daily_check()

        final_excitement = self.keeper.goals['active_project']['excitement_level']

        self.assertLess(final_excitement, initial_excitement,
                       "Excitement should decrease for stale projects")

    def test_daily_check_excitement_floor(self):
        """Test: Daily check never reduces excitement below 1"""
        # Set very low excitement and old last win
        self.keeper.goals['active_project']['excitement_level'] = 2
        old_date = datetime.now() - timedelta(days=10)
        self.keeper.goals['active_project']['last_win'] = old_date.isoformat()

        with patch.object(self.keeper, '_save_goals'):
            self.keeper.daily_check()

        final_excitement = self.keeper.goals['active_project']['excitement_level']

        self.assertGreaterEqual(final_excitement, 1,
                               "Excitement must not drop below 1")

    def test_daily_check_includes_motivation_messages(self):
        """Test: Daily check includes motivational messaging"""
        # Set last win to 4 days ago to trigger "Need a win" message
        four_days_ago = datetime.now() - timedelta(days=4)
        self.keeper.goals['active_project']['last_win'] = four_days_ago.isoformat()

        with patch.object(self.keeper, '_save_goals'):
            report = self.keeper.daily_check()

        motivational_phrases = [
            "Commitment > Excitement",
            "Need a win",
            "Days committed"
        ]

        for phrase in motivational_phrases:
            self.assertIn(phrase, report,
                         f"Daily check should include motivational phrase: {phrase}")

    def test_daily_check_shows_unresolved_blockers(self):
        """Test: Daily check highlights unresolved blockers"""
        self.keeper.goals['active_project']['blockers'] = [
            {
                'issue': 'Unresolved issue',
                'severity': 5,
                'logged': datetime.now().isoformat(),
                'resolved': False
            },
            {
                'issue': 'Resolved issue',
                'severity': 3,
                'logged': datetime.now().isoformat(),
                'resolved': True
            }
        ]

        with patch.object(self.keeper, '_save_goals'):
            report = self.keeper.daily_check()

        self.assertIn("1 unresolved blockers", report,
                     "Daily check should show count of unresolved blockers")


class TestNextActionGuidance(unittest.TestCase):
    """Test next action recommendation system"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch.object(GoalKeeper, '__init__') as mock_init:
            mock_init.return_value = None
            self.keeper = GoalKeeper()
            self.keeper.brain_dir = Path(self.temp_dir)
            self.keeper.goals_file = self.keeper.brain_dir / "active_goals.json"
            self.keeper.wins_file = self.keeper.brain_dir / "wins_log.json"
            self.keeper.commitment_file = self.keeper.brain_dir / "commitment.json"
            self.keeper.goals = {
                'test_project': {
                    'started': datetime.now().isoformat(),
                    'status': 'active',
                    'excitement_level': 6,
                    'days_worked': 1,
                    'last_win': datetime.now().isoformat(),
                    'blockers': [],
                    'next_actions': []
                }
            }
            self.keeper.wins = []
            self.keeper.commitment = {}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_next_action_prioritizes_blockers(self):
        """Test: Next action prioritizes fixing unresolved blockers"""
        blocker_issue = "Critical bug blocking progress"
        self.keeper.goals['test_project']['blockers'] = [{
            'issue': blocker_issue,
            'severity': 8,
            'logged': datetime.now().isoformat(),
            'resolved': False
        }]

        next_action = self.keeper.get_next_action('test_project')

        self.assertIn("FIX BLOCKER", next_action,
                     "Next action should prioritize fixing blockers")
        self.assertIn(blocker_issue, next_action,
                     "Next action should mention specific blocker")
        self.assertIn("Don't abandon", next_action,
                     "Next action should include anti-abandonment message")

    def test_get_next_action_suggests_quick_win_when_stale(self):
        """Test: Next action suggests quick win when no recent wins"""
        # Set last win to 3 days ago
        old_date = datetime.now() - timedelta(days=3)
        self.keeper.goals['test_project']['last_win'] = old_date.isoformat()

        next_action = self.keeper.get_next_action('test_project')

        self.assertIn("GET A QUICK WIN", next_action,
                     "Next action should suggest quick win for stale projects")
        self.assertIn("small", next_action,
                     "Should suggest small achievable tasks")

    def test_get_next_action_returns_planned_actions(self):
        """Test: Next action returns planned actions when available"""
        planned_action = "Implement user authentication"
        self.keeper.goals['test_project']['next_actions'] = [planned_action]

        next_action = self.keeper.get_next_action('test_project')

        self.assertIn("NEXT", next_action,
                     "Should indicate this is the next planned action")
        self.assertIn(planned_action, next_action,
                     "Should include the planned action text")

    def test_get_next_action_nonexistent_project(self):
        """Test: Next action for nonexistent project returns error"""
        next_action = self.keeper.get_next_action('nonexistent')

        self.assertIn("not found", next_action,
                     "Should return error for nonexistent project")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)