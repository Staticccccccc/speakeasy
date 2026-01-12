# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Unit tests for the RegistryManager component.
Tests registry key creation, value storage, and retrieval without binary execution.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy.windows.regman import (
    RegistryManager, RegKey, RegValue,
    HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER,
    HKEY_CLASSES_ROOT, HKEY_USERS
)
import speakeasy.winenv.defs.registry.reg as regdefs


class TestRegValue(unittest.TestCase):
    """Test RegValue class functionality."""

    def test_string_value(self):
        """Test REG_SZ value creation."""
        val = RegValue("TestName", regdefs.REG_SZ, "TestData")
        self.assertEqual(val.get_name(), "TestName")
        self.assertEqual(val.get_type(), regdefs.REG_SZ)
        self.assertEqual(val.get_data(), "TestData")

    def test_dword_value_from_string(self):
        """Test REG_DWORD value creation from hex string."""
        val = RegValue("DwordVal", regdefs.REG_DWORD, "0x12345678")
        self.assertEqual(val.get_name(), "DwordVal")
        self.assertEqual(val.get_type(), regdefs.REG_DWORD)
        self.assertEqual(val.get_data(), 0x12345678)

    def test_dword_value_from_int(self):
        """Test REG_DWORD value creation from integer."""
        val = RegValue("DwordVal", regdefs.REG_DWORD, 42)
        self.assertEqual(val.get_data(), 42)

    def test_qword_value(self):
        """Test REG_QWORD value creation."""
        val = RegValue("QwordVal", regdefs.REG_QWORD, "0xDEADBEEFCAFE")
        self.assertEqual(val.get_data(), 0xDEADBEEFCAFE)

    def test_expand_sz_value(self):
        """Test REG_EXPAND_SZ value."""
        val = RegValue("ExpandVal", regdefs.REG_EXPAND_SZ, "%SystemRoot%\\test.exe")
        self.assertEqual(val.get_data(), "%SystemRoot%\\test.exe")

    def test_multi_sz_value(self):
        """Test REG_MULTI_SZ value."""
        val = RegValue("MultiVal", regdefs.REG_MULTI_SZ, "value1\0value2\0")
        self.assertEqual(val.get_data(), "value1\0value2\0")


class TestRegKey(unittest.TestCase):
    """Test RegKey class functionality."""

    def test_key_creation(self):
        """Test basic key creation."""
        key = RegKey("HKEY_LOCAL_MACHINE\\SOFTWARE\\Test")
        self.assertEqual(key.get_path(), "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test")

    def test_handle_allocation(self):
        """Test that handles are unique."""
        key1 = RegKey("HKEY_LOCAL_MACHINE\\Test1")
        key2 = RegKey("HKEY_LOCAL_MACHINE\\Test2")
        h1 = key1.get_handle()
        h2 = key2.get_handle()
        self.assertNotEqual(h1, h2)

    def test_create_and_get_value(self):
        """Test creating and retrieving a value."""
        key = RegKey("HKEY_LOCAL_MACHINE\\Test")
        key.create_value("TestVal", regdefs.REG_SZ, "TestData")
        
        val = key.get_value("TestVal")
        self.assertIsNotNone(val)
        self.assertEqual(val.get_data(), "TestData")

    def test_get_nonexistent_value(self):
        """Test getting a value that doesn't exist."""
        key = RegKey("HKEY_LOCAL_MACHINE\\Test")
        val = key.get_value("NonExistent")
        self.assertIsNone(val)

    def test_case_insensitive_value_lookup(self):
        """Test that value lookup is case-insensitive."""
        key = RegKey("HKEY_LOCAL_MACHINE\\Test")
        key.create_value("TestVal", regdefs.REG_SZ, "data")
        
        val = key.get_value("testval")
        self.assertIsNotNone(val)
        self.assertEqual(val.get_data(), "data")

    def test_default_value(self):
        """Test retrieving default value with None name."""
        key = RegKey("HKEY_LOCAL_MACHINE\\Test")
        key.create_value("default", regdefs.REG_SZ, "DefaultData")
        
        val = key.get_value(None)
        self.assertIsNotNone(val)
        self.assertEqual(val.get_data(), "DefaultData")

    def test_get_values(self):
        """Test getting all values from a key."""
        key = RegKey("HKEY_LOCAL_MACHINE\\Test")
        key.create_value("Val1", regdefs.REG_SZ, "data1")
        key.create_value("Val2", regdefs.REG_DWORD, 123)
        
        values = key.get_values()
        self.assertEqual(len(values), 2)


class TestRegistryManager(unittest.TestCase):
    """Test RegistryManager class functionality."""

    def setUp(self):
        """Set up test configuration."""
        self.config = {
            "keys": [
                {
                    "path": "HKEY_LOCAL_MACHINE\\SOFTWARE\\ConfigTest",
                    "values": [
                        {
                            "name": "ConfigVal",
                            "type": "REG_SZ",
                            "data": "ConfigData"
                        }
                    ]
                }
            ]
        }
        self.regman = RegistryManager(config=self.config)

    def test_predefined_keys_exist(self):
        """Test that predefined root keys are initialized."""
        hklm = self.regman.get_key_from_handle(HKEY_LOCAL_MACHINE)
        self.assertIsNotNone(hklm)
        
        hkcu = self.regman.get_key_from_handle(HKEY_CURRENT_USER)
        self.assertIsNotNone(hkcu)
        
        hkcr = self.regman.get_key_from_handle(HKEY_CLASSES_ROOT)
        self.assertIsNotNone(hkcr)
        
        hku = self.regman.get_key_from_handle(HKEY_USERS)
        self.assertIsNotNone(hku)

    def test_create_key(self):
        """Test creating a new registry key."""
        key = self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\NewKey")
        self.assertIsNotNone(key)
        self.assertEqual(key.get_path(), "HKEY_LOCAL_MACHINE\\SOFTWARE\\NewKey")

    def test_create_key_idempotent(self):
        """Test that creating the same key twice returns the same key."""
        key1 = self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\SameKey")
        key2 = self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\SameKey")
        self.assertEqual(key1.get_path(), key2.get_path())

    def test_open_key(self):
        """Test opening a registry key."""
        self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\OpenTest")
        handle = self.regman.open_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\OpenTest")
        self.assertIsNotNone(handle)
        
        key = self.regman.get_key_from_handle(handle)
        self.assertIsNotNone(key)

    def test_open_nonexistent_key(self):
        """Test opening a key that doesn't exist."""
        handle = self.regman.open_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\DoesNotExist")
        self.assertIsNone(handle)

    def test_open_key_with_create(self):
        """Test opening with create flag creates the key."""
        handle = self.regman.open_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\CreateOnOpen", create=True)
        self.assertIsNotNone(handle)

    def test_get_key_from_config(self):
        """Test that keys from config are accessible via open_key."""
        # Note: get_key_from_path doesn't auto-check config, use open_key
        handle = self.regman.open_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\ConfigTest")
        self.assertIsNotNone(handle)
        
        key = self.regman.get_key_from_handle(handle)
        self.assertIsNotNone(key)
        
        val = key.get_value("ConfigVal")
        self.assertIsNotNone(val)
        self.assertEqual(val.get_data(), "ConfigData")

    def test_normalize_registry_path(self):
        """Test registry path normalization."""
        # Test \\registry\\machine\\ prefix
        path1 = self.regman.normalize_reg_path("\\registry\\machine\\SOFTWARE\\Test")
        self.assertEqual(path1, "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test")
        
        # Test HKLM\\ prefix
        path2 = self.regman.normalize_reg_path("HKLM\\SOFTWARE\\Test")
        self.assertEqual(path2, "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test")

    def test_get_subkeys(self):
        """Test enumerating subkeys."""
        self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\Parent\\Child1")
        self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\Parent\\Child2")
        self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\Parent\\Child3")
        
        parent = self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\Parent")
        subkeys = self.regman.get_subkeys(parent)
        
        self.assertIn("Child1", subkeys)
        self.assertIn("Child2", subkeys)
        self.assertIn("Child3", subkeys)

    def test_is_key_parent_key(self):
        """Test checking if a key is a parent of other keys."""
        self.regman.create_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\ParentTest\\SubKey")
        
        is_parent = self.regman.is_key_a_parent_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\ParentTest")
        self.assertTrue(is_parent)
        
        not_parent = self.regman.is_key_a_parent_key("HKEY_LOCAL_MACHINE\\SOFTWARE\\NotAParent")
        self.assertFalse(not_parent)


class TestRegistryManagerNoConfig(unittest.TestCase):
    """Test RegistryManager without configuration."""

    def setUp(self):
        """Set up registry manager without config."""
        self.regman = RegistryManager(config={"keys": []})

    def test_basic_operations(self):
        """Test basic operations work without config."""
        key = self.regman.create_key("HKEY_CURRENT_USER\\Software\\TestApp")
        self.assertIsNotNone(key)
        
        key.create_value("Setting", regdefs.REG_SZ, "Value")
        val = key.get_value("Setting")
        self.assertEqual(val.get_data(), "Value")


if __name__ == '__main__':
    unittest.main()
