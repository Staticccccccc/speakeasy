# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Unit tests for the ObjectManager component.
Tests Console and SEH classes which don't require full emulator.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy.windows.objman import Console, SEH


class TestConsole(unittest.TestCase):
    """Test Console class functionality."""

    def test_console_creation(self):
        """Test basic console creation."""
        console = Console()
        self.assertIsNotNone(console.handle)

    def test_console_handle_unique(self):
        """Test that console handles are unique."""
        c1 = Console()
        c2 = Console()
        self.assertNotEqual(c1.handle, c2.handle)

    def test_console_window(self):
        """Test console window setter/getter."""
        console = Console()
        console.set_window(0x12345)
        self.assertEqual(console.get_window(), 0x12345)


class TestSEH(unittest.TestCase):
    """Test SEH (Structured Exception Handling) class."""

    def test_seh_creation(self):
        """Test basic SEH creation."""
        seh = SEH()
        self.assertIsNone(seh.context)
        self.assertEqual(seh.context_address, 0)

    def test_seh_context(self):
        """Test setting and getting SEH context."""
        seh = SEH()
        mock_context = object()
        seh.set_context(mock_context, address=0x1000)
        
        self.assertEqual(seh.get_context(), mock_context)
        self.assertEqual(seh.context_address, 0x1000)

    def test_seh_record(self):
        """Test setting SEH record."""
        seh = SEH()
        mock_record = object()
        seh.set_record(mock_record, address=0x2000)
        
        self.assertEqual(seh.record, mock_record)
        # Note: set_record doesn't store address in SEH class

    def test_seh_frames(self):
        """Test SEH frame management."""
        seh = SEH()
        
        # Initially no frames
        self.assertEqual(len(seh.get_frames()), 0)
        
        # Add a frame
        seh.add_frame(
            entry=0x1000,
            scope_table=0x2000,
            records=[{'filter': 0x3000, 'handler': 0x4000}]
        )
        
        # Should have one frame
        self.assertEqual(len(seh.get_frames()), 1)

    def test_seh_clear_frames(self):
        """Test clearing SEH frames."""
        seh = SEH()
        seh.add_frame(entry=0x1000, scope_table=0x2000, records=[])
        seh.add_frame(entry=0x5000, scope_table=0x6000, records=[])
        
        self.assertEqual(len(seh.get_frames()), 2)
        
        seh.clear_frames()
        self.assertEqual(len(seh.get_frames()), 0)

    def test_seh_set_current_frame(self):
        """Test setting current frame."""
        seh = SEH()
        mock_frame = object()
        seh.set_current_frame(mock_frame)
        
        # Note: set_current_frame stores to self.frame, not self.curr_frame
        self.assertEqual(seh.frame, mock_frame)

    def test_seh_last_func(self):
        """Test setting last function."""
        seh = SEH()
        seh.set_last_func(0xDEADBEEF)
        
        self.assertEqual(seh.last_func, 0xDEADBEEF)


class TestSEHFrame(unittest.TestCase):
    """Test SEH.Frame inner class."""

    def test_frame_creation(self):
        """Test frame creation."""
        frame = SEH.Frame(
            entry=0x1000,
            scope_table=0x2000,
            scope_records=[{'filter': 0x3000, 'handler': 0x4000}]
        )
        
        self.assertEqual(frame.entry, 0x1000)
        self.assertEqual(frame.scope_table, 0x2000)
        self.assertFalse(frame.searched)


class TestSEHScopeRecord(unittest.TestCase):
    """Test SEH.ScopeRecord inner class."""

    def test_scope_record_creation(self):
        """Test scope record creation."""
        record = SEH.ScopeRecord({'filter': 0x1000, 'handler': 0x2000})
        
        self.assertFalse(record.filter_called)
        self.assertFalse(record.handler_called)


if __name__ == '__main__':
    unittest.main()
