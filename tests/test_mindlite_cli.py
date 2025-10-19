#!/usr/bin/env python3
"""
Simplified tests for mindlite CLI application.

Tests the standalone executable directly.
"""

import os
import sys
import tempfile
import unittest
import subprocess
import json
from datetime import datetime, timezone


class TestMindliteCLI(unittest.TestCase):
    """Test mindlite CLI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        # Initialize database
        result = subprocess.run(['python3', '-m', 'mindlite', 'init'], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
    
    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def run_command(self, args):
        """Run a mindlite command and return result."""
        cmd = ['python3', '-m', 'mindlite'] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    
    def test_init_command(self):
        """Test database initialization."""
        result = self.run_command(['init'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Database initialized', result.stdout)
    
    def test_add_command(self):
        """Test adding items."""
        result = self.run_command(['add', 'Test item', '--type', 'todo', '--priority', 'high'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Added item #1', result.stdout)
    
    def test_enhanced_date_parsing(self):
        """Test enhanced date parsing."""
        # Test tomorrow
        result = self.run_command(['add', 'Tomorrow task', '--due', 'tomorrow'])
        self.assertEqual(result.returncode, 0)
        
        # Test relative date
        result = self.run_command(['add', 'Next week task', '--due', '+7'])
        self.assertEqual(result.returncode, 0)
        
        # Test MM/DD/YY format
        result = self.run_command(['add', 'MM/DD task', '--due', '10/25/25'])
        self.assertEqual(result.returncode, 0)
    
    def test_list_command(self):
        """Test listing items."""
        # Add some test items
        self.run_command(['add', 'High priority task', '--priority', 'high', '--tags', 'urgent'])
        self.run_command(['add', 'Low priority task', '--priority', 'low', '--tags', 'research'])
        
        # Test basic list
        result = self.run_command(['list'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('High priority task', result.stdout)
        self.assertIn('Low priority task', result.stdout)
        
        # Test filtering by priority
        result = self.run_command(['list', '--priority', 'high'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('High priority task', result.stdout)
        self.assertNotIn('Low priority task', result.stdout)
        
        # Test filtering by tags
        result = self.run_command(['list', '--tags', 'urgent'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('High priority task', result.stdout)
    
    def test_bulk_operations(self):
        """Test bulk operations."""
        # Add test items
        self.run_command(['add', 'Task 1', '--type', 'todo'])
        self.run_command(['add', 'Task 2', '--type', 'todo'])
        self.run_command(['add', 'Task 3', '--type', 'todo'])
        
        # Test bulk done
        result = self.run_command(['bulk', 'done', '1,2,3'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Marked 3 items as done', result.stdout)
        
        # Test bulk tagging
        result = self.run_command(['bulk', 'tag', '1,2', '--tags', 'urgent,work'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Added tags to 2 items', result.stdout)
    
    def test_command_aliases(self):
        """Test command aliases."""
        # Test 'a' alias for add
        result = self.run_command(['a', 'Alias test', '--type', 'todo'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Added item', result.stdout)
        
        # Test 'l' alias for list
        result = self.run_command(['l'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Alias test', result.stdout)
        
        # Test 'h' alias for help
        result = self.run_command(['h'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout)
    
    def test_export_functionality(self):
        """Test export functionality."""
        # Add test item
        self.run_command(['add', 'Export test', '--type', 'todo', '--tags', 'test,export'])
        
        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            export_path = f.name
        
        try:
            result = self.run_command(['export', 'json', export_path])
            self.assertEqual(result.returncode, 0)
            
            # Verify export file
            self.assertTrue(os.path.exists(export_path))
            with open(export_path, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
                self.assertIn('Export test', data[0]['title'])
        
        finally:
            os.unlink(export_path)
        
        # Test Markdown export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            export_path = f.name
        
        try:
            result = self.run_command(['export', 'md', export_path])
            self.assertEqual(result.returncode, 0)
            
            # Verify export file
            self.assertTrue(os.path.exists(export_path))
            with open(export_path, 'r') as f:
                data = f.read()
                self.assertIn('# Mindlite Export', data)
                self.assertIn('Export test', data)
        
        finally:
            os.unlink(export_path)
    
    def test_status_changes(self):
        """Test status change commands."""
        # Add test item
        self.run_command(['add', 'Status test', '--type', 'todo'])
        
        # Test start command
        result = self.run_command(['start', '1'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('status changed to doing', result.stdout)
        
        # Test done command
        result = self.run_command(['done', '1'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('status changed to done', result.stdout)
    
    def test_id_reset_functionality(self):
        """Test ID reset when database is empty."""
        # Add and delete an item
        self.run_command(['add', 'Test item'])
        self.run_command(['delete', '1', '-y'])
        
        # Add another item - should get ID 1
        result = self.run_command(['add', 'New item'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Added item #1', result.stdout)
    
    def test_error_handling(self):
        """Test error handling."""
        # Test invalid command
        result = self.run_command(['invalid_command'])
        self.assertNotEqual(result.returncode, 0)
        
        # Test invalid date format
        result = self.run_command(['add', 'Test', '--due', 'invalid-date'])
        self.assertNotEqual(result.returncode, 0)
        
        # Test non-existent item
        result = self.run_command(['show', '999'])
        self.assertNotEqual(result.returncode, 0)


class TestDateParsing(unittest.TestCase):
    """Test date parsing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        # Initialize database
        subprocess.run(['python3', '-m', 'mindlite', 'init'], 
                      capture_output=True, text=True)
    
    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def run_command(self, args):
        """Run a mindlite command and return result."""
        cmd = ['python3', '-m', 'mindlite'] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    
    def test_date_formats(self):
        """Test various date formats."""
        test_cases = [
            ('2025-10-25', 'ISO format'),
            ('10/25/25', 'MM/DD/YY format'),
            ('10/25/2025', 'MM/DD/YYYY format'),
            ('tomorrow', 'Natural language'),
            ('+3', 'Relative date'),
        ]
        
        for date_str, description in test_cases:
            with self.subTest(date=date_str, description=description):
                result = self.run_command(['add', f'Test {description}', '--due', date_str])
                self.assertEqual(result.returncode, 0, 
                               f"Failed for {description}: {date_str}")
    
    def test_invalid_dates(self):
        """Test invalid date handling."""
        invalid_dates = [
            'invalid-date',
            '13/25/25',  # Invalid month
            '32/10/25',  # Invalid day
            'not-a-date',
        ]
        
        for invalid_date in invalid_dates:
            with self.subTest(date=invalid_date):
                result = self.run_command(['add', 'Test', '--due', invalid_date])
                self.assertNotEqual(result.returncode, 0,
                                  f"Should have failed for invalid date: {invalid_date}")


if __name__ == '__main__':
    unittest.main()
