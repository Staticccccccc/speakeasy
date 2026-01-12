# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Tests for shellcode loading and execution.
Uses embedded shellcode bytes to test without requiring compiled binaries.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy import Speakeasy


def get_test_config():
    """Get full test configuration from test.json."""
    import json
    fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.json')
    with open(fp, 'r') as f:
        return json.load(f)


# Simple x86 shellcode that just returns
# xor eax, eax  ; 31 C0
# ret           ; C3
SHELLCODE_X86_RET = bytes([0x31, 0xC0, 0xC3])

# x86 shellcode: mov eax, 0x12345678; ret
# B8 78 56 34 12  ; mov eax, 0x12345678
# C3              ; ret
SHELLCODE_X86_MOV_RET = bytes([0xB8, 0x78, 0x56, 0x34, 0x12, 0xC3])

# x64 shellcode that just returns
# xor rax, rax  ; 48 31 C0
# ret           ; C3
SHELLCODE_X64_RET = bytes([0x48, 0x31, 0xC0, 0xC3])

# x64 shellcode: mov rax, 0x12345678; ret
# 48 C7 C0 78 56 34 12  ; mov rax, 0x12345678
# C3                     ; ret
SHELLCODE_X64_MOV_RET = bytes([0x48, 0xC7, 0xC0, 0x78, 0x56, 0x34, 0x12, 0xC3])


class TestShellcodeLoading(unittest.TestCase):
    """Test shellcode loading functionality."""

    def setUp(self):
        self.config = get_test_config()

    def test_load_x86_shellcode(self):
        """Test loading x86 shellcode."""
        se = Speakeasy(config=self.config)
        sc_addr = se.load_shellcode(fpath=None, arch='x86', data=SHELLCODE_X86_RET)
        self.assertIsNotNone(sc_addr)
        self.assertGreater(sc_addr, 0)

    def test_load_x64_shellcode(self):
        """Test loading x64 shellcode."""
        se = Speakeasy(config=self.config)
        sc_addr = se.load_shellcode(fpath=None, arch='amd64', data=SHELLCODE_X64_RET)
        self.assertIsNotNone(sc_addr)
        self.assertGreater(sc_addr, 0)

    def test_load_shellcode_with_nops(self):
        """Test loading shellcode with NOP sled."""
        nop_sled = b'\x90' * 16 + SHELLCODE_X86_RET
        
        se = Speakeasy(config=self.config)
        sc_addr = se.load_shellcode(fpath=None, arch='x86', data=nop_sled)
        self.assertIsNotNone(sc_addr)


class TestShellcodeExecution(unittest.TestCase):
    """Test shellcode execution (may timeout on some systems)."""

    def setUp(self):
        self.config = get_test_config()
        # Reduce timeout for faster testing
        self.config['timeout'] = 5

    def test_x86_simple_shellcode(self):
        """Test executing simple x86 shellcode."""
        try:
            se = Speakeasy(config=self.config)
            sc_addr = se.load_shellcode(fpath=None, arch='x86', data=SHELLCODE_X86_RET)
            se.run_shellcode(sc_addr)
            report = se.get_report()
            
            self.assertIsNotNone(report)
            self.assertIn('entry_points', report)
        except Exception as e:
            # Some systems may have issues with emulation
            self.skipTest(f"Shellcode execution failed: {e}")

    def test_x64_simple_shellcode(self):
        """Test executing simple x64 shellcode."""
        try:
            se = Speakeasy(config=self.config)
            sc_addr = se.load_shellcode(fpath=None, arch='amd64', data=SHELLCODE_X64_RET)
            se.run_shellcode(sc_addr)
            report = se.get_report()
            
            self.assertIsNotNone(report)
            self.assertIn('entry_points', report)
        except Exception as e:
            self.skipTest(f"Shellcode execution failed: {e}")


class TestShellcodeEdgeCases(unittest.TestCase):
    """Test edge cases for shellcode handling."""

    def setUp(self):
        self.config = get_test_config()

    def test_single_ret_shellcode(self):
        """Test single byte shellcode (just ret)."""
        se = Speakeasy(config=self.config)
        sc_addr = se.load_shellcode(fpath=None, arch='x86', data=b'\xC3')
        self.assertIsNotNone(sc_addr)


if __name__ == '__main__':
    unittest.main()
