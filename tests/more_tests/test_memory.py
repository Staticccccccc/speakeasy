# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Unit tests for the MemoryManager component.
Tests MemMap class functionality.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy.memmgr import MemMap
import speakeasy.common as common


class TestMemMap(unittest.TestCase):
    """Test MemMap class functionality."""

    def test_memmap_creation(self):
        """Test basic MemMap creation."""
        mm = MemMap(
            base=0x10000,
            size=0x1000,
            tag="test_alloc",
            prot=common.PERM_MEM_RWX,
            flags=0,
            block_base=0x10000,
            block_size=0x1000
        )
        
        self.assertEqual(mm.get_base(), 0x10000)
        self.assertEqual(mm.get_size(), 0x1000)
        # get_tag() returns format "tag.base", so check if tag is contained
        self.assertIn("test_alloc", mm.get_tag())
        self.assertEqual(mm.get_prot(), common.PERM_MEM_RWX)

    def test_memmap_tag_update(self):
        """Test updating memory map tag."""
        mm = MemMap(
            base=0x10000, size=0x1000, tag="original",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        
        mm.update_tag("updated")
        self.assertEqual(mm.get_tag(), "updated")

    def test_memmap_alloc_free_state(self):
        """Test allocation state tracking."""
        mm = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        
        # Initially allocated
        self.assertFalse(mm.is_free())
        
        # Mark as free
        mm.set_free()
        self.assertTrue(mm.is_free())
        
        # Mark as allocated again
        mm.set_alloc()
        self.assertFalse(mm.is_free())

    def test_memmap_process_association(self):
        """Test process association."""
        mm = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        
        mock_process = object()
        mm.set_process(mock_process)
        self.assertEqual(mm.get_process(), mock_process)

    def test_memmap_equality(self):
        """Test MemMap equality comparison."""
        mm1 = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        mm2 = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        mm3 = MemMap(
            base=0x20000, size=0x1000, tag="other",
            prot=0, flags=0, block_base=0x20000, block_size=0x1000
        )
        
        self.assertEqual(mm1, mm2)
        self.assertNotEqual(mm1, mm3)

    def test_memmap_hash(self):
        """Test MemMap hashing for use in sets/dicts."""
        mm1 = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x10000, block_size=0x1000
        )
        mm2 = MemMap(
            base=0x20000, size=0x1000, tag="test",
            prot=0, flags=0, block_base=0x20000, block_size=0x1000
        )
        
        # Should be able to use in a set
        mm_set = {mm1, mm2}
        self.assertEqual(len(mm_set), 2)

    def test_shared_memory_flag(self):
        """Test shared memory mapping."""
        mm = MemMap(
            base=0x10000, size=0x1000, tag="shared_test",
            prot=common.PERM_MEM_RWX, flags=0,
            block_base=0x10000, block_size=0x1000,
            shared=True
        )
        
        self.assertTrue(mm.shared)

    def test_non_shared_memory(self):
        """Test non-shared memory mapping."""
        mm = MemMap(
            base=0x10000, size=0x1000, tag="private_test",
            prot=common.PERM_MEM_RWX, flags=0,
            block_base=0x10000, block_size=0x1000,
            shared=False
        )
        
        self.assertFalse(mm.shared)

    def test_memmap_flags(self):
        """Test that flags are stored correctly."""
        test_flags = 0x42
        mm = MemMap(
            base=0x10000, size=0x1000, tag="test",
            prot=0, flags=test_flags,
            block_base=0x10000, block_size=0x1000
        )
        
        self.assertEqual(mm.get_flags(), test_flags)

    def test_permission_constants(self):
        """Test that permission constants are defined."""
        self.assertIsNotNone(common.PERM_MEM_RWX)
        self.assertIsNotNone(common.PERM_MEM_READ)
        self.assertIsNotNone(common.PERM_MEM_WRITE)
        self.assertIsNotNone(common.PERM_MEM_EXEC)


if __name__ == '__main__':
    unittest.main()
