# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Tests for API hook functionality.
Tests hook registration - hooks are stored in a list before module load.
"""

import unittest
import sys
import os

# Add speakeasy and parent test directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy import Speakeasy


def get_test_config():
    """Get test configuration."""
    import json
    fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.json')
    with open(fp, 'r') as f:
        return json.load(f)


class TestAPIHookRegistration(unittest.TestCase):
    """Test API hook registration functionality."""

    def setUp(self):
        self.config = get_test_config()

    def test_hook_registration_before_load(self):
        """Test that hooks can be registered before loading a module."""
        se = Speakeasy(config=self.config)
        
        def dummy_callback(emu, api_name, func, params):
            return None
        
        initial_count = len(se.api_hooks)
        se.add_api_hook(
            cb=dummy_callback,
            module='kernel32',
            api_name='GetTickCount'
        )
        
        # Hook should be added to the pending hooks list
        self.assertEqual(len(se.api_hooks), initial_count + 1)

    def test_hook_without_module(self):
        """Test registering a hook without specific module."""
        se = Speakeasy(config=self.config)
        
        def dummy_callback(emu, api_name, func, params):
            return None
        
        initial_count = len(se.api_hooks)
        se.add_api_hook(
            cb=dummy_callback,
            module='',  # Match any module
            api_name='MessageBox*'  # Wildcard
        )
        
        self.assertEqual(len(se.api_hooks), initial_count + 1)

    def test_wildcard_hook(self):
        """Test registering a hook with wildcard pattern."""
        se = Speakeasy(config=self.config)
        
        def dummy_callback(emu, api_name, func, params):
            return None
        
        initial_count = len(se.api_hooks)
        # Hook all functions starting with "Create"
        se.add_api_hook(
            cb=dummy_callback,
            module='kernel32',
            api_name='Create*'
        )
        
        self.assertEqual(len(se.api_hooks), initial_count + 1)


class TestMultipleHooks(unittest.TestCase):
    """Test registering multiple hooks."""

    def setUp(self):
        self.config = get_test_config()

    def test_multiple_hooks_different_apis(self):
        """Test registering multiple hooks for different APIs."""
        se = Speakeasy(config=self.config)
        
        def callback1(emu, api_name, func, params):
            return None
        
        def callback2(emu, api_name, func, params):
            return None
        
        initial_count = len(se.api_hooks)
        se.add_api_hook(cb=callback1, module='kernel32', api_name='Sleep')
        se.add_api_hook(cb=callback2, module='kernel32', api_name='GetTickCount')
        
        self.assertEqual(len(se.api_hooks), initial_count + 2)

    def test_hooks_on_different_modules(self):
        """Test hooks on different modules."""
        se = Speakeasy(config=self.config)
        
        initial_count = len(se.api_hooks)
        
        se.add_api_hook(
            cb=lambda e, a, f, p: None,
            module='kernel32',
            api_name='CreateFileA'
        )
        
        se.add_api_hook(
            cb=lambda e, a, f, p: None,
            module='ntdll',
            api_name='NtCreateFile'
        )
        
        se.add_api_hook(
            cb=lambda e, a, f, p: None,
            module='user32',
            api_name='MessageBoxA'
        )
        
        self.assertEqual(len(se.api_hooks), initial_count + 3)


class TestHookCatchAll(unittest.TestCase):
    """Test catch-all hooks."""

    def setUp(self):
        self.config = get_test_config()

    def test_global_wildcard_hook(self):
        """Test that global wildcard can be registered."""
        se = Speakeasy(config=self.config)
        
        initial_count = len(se.api_hooks)
        se.add_api_hook(
            cb=lambda e, a, f, p: None,
            module='',  # Any module
            api_name='*'  # Any API
        )
        
        self.assertEqual(len(se.api_hooks), initial_count + 1)

    def test_module_wildcard_hook(self):
        """Test module-level wildcard hook."""
        se = Speakeasy(config=self.config)
        
        initial_count = len(se.api_hooks)
        se.add_api_hook(
            cb=lambda e, a, f, p: None,
            module='kernel32',  # Specific module
            api_name='*'  # All APIs in that module
        )
        
        self.assertEqual(len(se.api_hooks), initial_count + 1)


if __name__ == '__main__':
    unittest.main()
