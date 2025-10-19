#!/usr/bin/env python3
"""
Test runner for mindlite CLI application.

Usage:
    python3 run_tests.py
    python3 run_tests.py --verbose
    python3 run_tests.py --coverage
"""

import sys
import os
import unittest
import argparse

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tests(verbose=False, coverage=False):
    """Run all tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    suite = loader.discover(start_dir, pattern='test_mindlite_cli.py')
    
    # Configure test runner
    verbosity = 2 if verbose else 1
    
    if coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
            
            runner = unittest.TextTestRunner(verbosity=verbosity)
            result = runner.run(suite)
            
            cov.stop()
            cov.save()
            
            print("\n" + "="*50)
            print("COVERAGE REPORT")
            print("="*50)
            cov.report()
            
            return result.wasSuccessful()
        except ImportError:
            print("Warning: coverage module not available. Install with: pip install coverage")
            runner = unittest.TextTestRunner(verbosity=verbosity)
            result = runner.run(suite)
            return result.wasSuccessful()
    else:
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return result.wasSuccessful()

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run mindlite tests')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Generate coverage report')
    
    args = parser.parse_args()
    
    print("Running mindlite tests...")
    print("="*50)
    
    success = run_tests(verbose=args.verbose, coverage=args.coverage)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
