#!/usr/bin/env python3
"""
Comprehensive tests for mindlite CLI application.

Tests cover:
- Database operations
- Date parsing
- Bulk operations
- Filtering
- Command aliases
- Export functionality
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import sqlite3

# Add the mindlite package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mindlite import db, models, utils, export, cli


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        # Initialize test database
        with db.get_conn() as conn:
            db.init_db(conn)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def test_init_db(self):
        """Test database initialization."""
        with db.get_conn() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('items', tables)
            self.assertIn('tags', tables)
            self.assertIn('item_tags', tables)
    
    def test_insert_item(self):
        """Test item insertion."""
        item_data = {
            'type': 'todo',
            'title': 'Test item',
            'body': 'Test body',
            'status': 'todo',
            'priority': 'high',
            'due_date': '2025-10-25',
            'created_at': models.now_iso(),
            'updated_at': models.now_iso(),
            'tags': ['test', 'example']
        }
        
        with db.get_conn() as conn:
            item_id = db.insert_item(conn, item_data)
            self.assertEqual(item_id, 1)  # Should start from 1
            
            # Verify item was inserted
            item = db.get_item(conn, item_id)
            self.assertIsNotNone(item)
            self.assertEqual(item['title'], 'Test item')
            self.assertEqual(item['tags'], ['test', 'example'])
    
    def test_id_reset_on_empty_db(self):
        """Test that ID resets to 1 when database is empty."""
        # Add and delete an item
        item_data = {
            'type': 'todo',
            'title': 'Test item',
            'body': '',
            'status': 'todo',
            'priority': 'med',
            'due_date': None,
            'created_at': models.now_iso(),
            'updated_at': models.now_iso(),
            'tags': []
        }
        
        with db.get_conn() as conn:
            item_id = db.insert_item(conn, item_data)
            db.delete_item(conn, item_id)
            
            # Add another item - should get ID 1
            item_id2 = db.insert_item(conn, item_data)
            self.assertEqual(item_id2, 1)
    
    def test_update_item(self):
        """Test item updates."""
        item_data = {
            'type': 'todo',
            'title': 'Original title',
            'body': '',
            'status': 'todo',
            'priority': 'med',
            'due_date': None,
            'created_at': models.now_iso(),
            'updated_at': models.now_iso(),
            'tags': []
        }
        
        with db.get_conn() as conn:
            item_id = db.insert_item(conn, item_data)
            
            # Update the item
            db.update_item(conn, item_id, title='Updated title', status='doing')
            
            # Verify update
            item = db.get_item(conn, item_id)
            self.assertEqual(item['title'], 'Updated title')
            self.assertEqual(item['status'], 'doing')
    
    def test_list_items_with_filters(self):
        """Test item listing with various filters."""
        # Add test items
        items = [
            {'type': 'todo', 'title': 'High priority task', 'priority': 'high', 'status': 'todo', 'tags': ['urgent']},
            {'type': 'idea', 'title': 'Low priority idea', 'priority': 'low', 'status': 'done', 'tags': ['research']},
            {'type': 'todo', 'title': 'Medium task', 'priority': 'med', 'status': 'doing', 'tags': ['work']},
        ]
        
        with db.get_conn() as conn:
            for item_data in items:
                full_item = {
                    'type': item_data['type'],
                    'title': item_data['title'],
                    'body': '',
                    'status': item_data['status'],
                    'priority': item_data['priority'],
                    'due_date': None,
                    'created_at': models.now_iso(),
                    'updated_at': models.now_iso(),
                    'tags': item_data['tags']
                }
                db.insert_item(conn, full_item)
            
            # Test filters
            high_priority = db.list_items(conn, {'priority': ['high']})
            self.assertEqual(len(high_priority), 1)
            self.assertEqual(high_priority[0]['title'], 'High priority task')
            
            urgent_items = db.list_items(conn, {'tag': ['urgent']})
            self.assertEqual(len(urgent_items), 1)
            self.assertEqual(urgent_items[0]['title'], 'High priority task')
            
            open_items = db.list_items(conn, {'open_only': True})
            self.assertEqual(len(open_items), 2)  # todo and doing, not done


class TestDateParsing(unittest.TestCase):
    """Test enhanced date parsing functionality."""
    
    def test_iso_format(self):
        """Test ISO date format parsing."""
        result = models.parse_date('2025-10-25')
        self.assertEqual(result, '2025-10-25')
    
    def test_mm_dd_yy_format(self):
        """Test MM/DD/YY format parsing."""
        result = models.parse_date('10/25/25')
        self.assertEqual(result, '2025-10-25')
    
    def test_mm_dd_yyyy_format(self):
        """Test MM/DD/YYYY format parsing."""
        result = models.parse_date('10/25/2025')
        self.assertEqual(result, '2025-10-25')
    
    def test_relative_dates(self):
        """Test relative date parsing."""
        with patch('mindlite.models.datetime') as mock_datetime:
            mock_now = datetime(2025, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strptime = datetime.strptime
            
            # Test tomorrow
            result = models.parse_date('tomorrow')
            self.assertEqual(result, '2025-10-20')
            
            # Test +3 days
            result = models.parse_date('+3')
            self.assertEqual(result, '2025-10-22')
    
    def test_invalid_dates(self):
        """Test invalid date handling."""
        with self.assertRaises(ValueError):
            models.parse_date('invalid-date')
        
        with self.assertRaises(ValueError):
            models.parse_date('13/25/25')  # Invalid month
    
    def test_none_and_empty(self):
        """Test None and empty string handling."""
        self.assertIsNone(models.parse_date(None))
        self.assertIsNone(models.parse_date(''))


class TestBulkOperations(unittest.TestCase):
    """Test bulk operations functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        with db.get_conn() as conn:
            db.init_db(conn)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def test_bulk_done(self):
        """Test bulk done operation."""
        # Add test items
        with db.get_conn() as conn:
            for i in range(3):
                item_data = {
                    'type': 'todo',
                    'title': f'Task {i+1}',
                    'body': '',
                    'status': 'todo',
                    'priority': 'med',
                    'due_date': None,
                    'created_at': models.now_iso(),
                    'updated_at': models.now_iso(),
                    'tags': []
                }
                db.insert_item(conn, item_data)
        
        # Test bulk done
        with patch('sys.argv', ['mindlite', 'bulk', 'done', '1,2,3']):
            args = cli.create_parser().parse_args(['bulk', 'done', '1,2,3'])
            cli.cmd_bulk(args)
        
        # Verify all items are done
        with db.get_conn() as conn:
            items = db.list_items(conn, {'status': ['done']})
            self.assertEqual(len(items), 3)
    
    def test_bulk_tag(self):
        """Test bulk tagging operation."""
        # Add test items
        with db.get_conn() as conn:
            for i in range(2):
                item_data = {
                    'type': 'todo',
                    'title': f'Task {i+1}',
                    'body': '',
                    'status': 'todo',
                    'priority': 'med',
                    'due_date': None,
                    'created_at': models.now_iso(),
                    'updated_at': models.now_iso(),
                    'tags': []
                }
                db.insert_item(conn, item_data)
        
        # Test bulk tagging
        with patch('sys.argv', ['mindlite', 'bulk', 'tag', '1,2', '--tags', 'urgent,work']):
            args = cli.create_parser().parse_args(['bulk', 'tag', '1,2', '--tags', 'urgent,work'])
            cli.cmd_bulk(args)
        
        # Verify tags were added
        with db.get_conn() as conn:
            item1 = db.get_item(conn, 1)
            item2 = db.get_item(conn, 2)
            self.assertIn('urgent', item1['tags'])
            self.assertIn('work', item1['tags'])
            self.assertIn('urgent', item2['tags'])
            self.assertIn('work', item2['tags'])


class TestFiltering(unittest.TestCase):
    """Test enhanced filtering functionality."""
    
    def setUp(self):
        """Set up test database with sample data."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        with db.get_conn() as conn:
            db.init_db(conn)
            
            # Add test data
            test_items = [
                {'type': 'todo', 'title': 'High priority urgent task', 'priority': 'high', 'status': 'todo', 'tags': ['urgent', 'work']},
                {'type': 'idea', 'title': 'Low priority research idea', 'priority': 'low', 'status': 'done', 'tags': ['research']},
                {'type': 'todo', 'title': 'Medium priority task', 'priority': 'med', 'status': 'doing', 'tags': ['work']},
                {'type': 'issue', 'title': 'Bug fix needed', 'priority': 'high', 'status': 'blocked', 'tags': ['bug']},
            ]
            
            for item_data in test_items:
                full_item = {
                    'type': item_data['type'],
                    'title': item_data['title'],
                    'body': '',
                    'status': item_data['status'],
                    'priority': item_data['priority'],
                    'due_date': None,
                    'created_at': models.now_iso(),
                    'updated_at': models.now_iso(),
                    'tags': item_data['tags']
                }
                db.insert_item(conn, full_item)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def test_multiple_priorities_filter(self):
        """Test filtering by multiple priorities."""
        with db.get_conn() as conn:
            items = db.list_items(conn, {'priority': ['high', 'med']})
            self.assertEqual(len(items), 3)  # 2 high + 1 med
    
    def test_multiple_statuses_filter(self):
        """Test filtering by multiple statuses."""
        with db.get_conn() as conn:
            items = db.list_items(conn, {'status': ['todo', 'doing']})
            self.assertEqual(len(items), 2)  # 1 todo + 1 doing
    
    def test_multiple_tags_filter(self):
        """Test filtering by multiple tags."""
        with db.get_conn() as conn:
            items = db.list_items(conn, {'tag': ['urgent', 'work']})
            self.assertEqual(len(items), 2)  # Items with urgent OR work tags
    
    def test_search_filter(self):
        """Test search functionality."""
        with db.get_conn() as conn:
            items = db.list_items(conn, {'search': 'priority'})
            self.assertEqual(len(items), 2)  # Items containing 'priority' in title
    
    def test_open_only_filter(self):
        """Test open only filter."""
        with db.get_conn() as conn:
            items = db.list_items(conn, {'open_only': True})
            self.assertEqual(len(items), 3)  # All except 'done'


class TestCommandAliases(unittest.TestCase):
    """Test command aliases functionality."""
    
    def test_alias_resolution(self):
        """Test that command aliases are resolved correctly."""
        # Test that aliases are properly mapped
        aliases = {
            'a': 'add',
            'l': 'list',
            's': 'show',
            'e': 'edit',
            'st': 'start',
            'b': 'block',
            'del': 'delete',
            'ag': 'agenda',
            'exp': 'export',
            'h': 'help'
        }
        
        for alias, command in aliases.items():
            with patch('sys.argv', ['mindlite', alias]):
                # This should not raise an error
                parser = cli.create_parser()
                args = parser.parse_args([alias])
                self.assertEqual(args.command, command)


class TestExportFunctionality(unittest.TestCase):
    """Test export functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.original_db_path = os.environ.get('MINDLITE_DB')
        os.environ['MINDLITE_DB'] = self.test_db.name
        
        with db.get_conn() as conn:
            db.init_db(conn)
            
            # Add test item
            item_data = {
                'type': 'todo',
                'title': 'Test export item',
                'body': 'This is a test item for export',
                'status': 'todo',
                'priority': 'high',
                'due_date': '2025-10-25',
                'created_at': models.now_iso(),
                'updated_at': models.now_iso(),
                'tags': ['test', 'export']
            }
            db.insert_item(conn, item_data)
    
    def tearDown(self):
        """Clean up test database."""
        os.unlink(self.test_db.name)
        if self.original_db_path:
            os.environ['MINDLITE_DB'] = self.original_db_path
        else:
            os.environ.pop('MINDLITE_DB', None)
    
    def test_json_export(self):
        """Test JSON export functionality."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            export_path = f.name
        
        try:
            with db.get_conn() as conn:
                export.export_json(conn, export_path)
            
            # Verify export file was created and contains data
            self.assertTrue(os.path.exists(export_path))
            
            with open(export_path, 'r') as f:
                data = f.read()
                self.assertIn('Test export item', data)
                self.assertIn('test', data)
                self.assertIn('export', data)
        
        finally:
            os.unlink(export_path)
    
    def test_markdown_export(self):
        """Test Markdown export functionality."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            export_path = f.name
        
        try:
            with db.get_conn() as conn:
                export.export_md(conn, export_path)
            
            # Verify export file was created and contains data
            self.assertTrue(os.path.exists(export_path))
            
            with open(export_path, 'r') as f:
                data = f.read()
                self.assertIn('# Mindlite Export', data)
                self.assertIn('Test export item', data)
                self.assertIn('test, export', data)
        
        finally:
            os.unlink(export_path)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_comma_split(self):
        """Test comma splitting functionality."""
        self.assertEqual(utils.comma_split('a,b,c'), ['a', 'b', 'c'])
        self.assertEqual(utils.comma_split('a, b, c'), ['a', 'b', 'c'])
        self.assertEqual(utils.comma_split(''), [])
        self.assertEqual(utils.comma_split(None), [])
    
    def test_validation_functions(self):
        """Test validation functions."""
        # Test valid inputs
        self.assertEqual(models.validate_type('todo'), 'todo')
        self.assertEqual(models.validate_status('doing'), 'doing')
        self.assertEqual(models.validate_priority('high'), 'high')
        
        # Test invalid inputs
        with self.assertRaises(ValueError):
            models.validate_type('invalid')
        
        with self.assertRaises(ValueError):
            models.validate_status('invalid')
        
        with self.assertRaises(ValueError):
            models.validate_priority('invalid')


if __name__ == '__main__':
    unittest.main()
