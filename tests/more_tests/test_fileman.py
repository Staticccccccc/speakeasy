# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Unit tests for the FileManager component.
Tests file system emulation including files, pipes, and memory maps.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy.windows.fileman import File, Pipe, FileMap


class TestFile(unittest.TestCase):
    """Test File class functionality."""

    def test_file_creation(self):
        """Test basic file creation."""
        f = File(path="C:\\test\\file.txt")
        self.assertEqual(f.get_path(), "C:\\test\\file.txt")

    def test_file_handle_allocation(self):
        """Test file handle allocation."""
        f1 = File(path="C:\\test\\file1.txt")
        f2 = File(path="C:\\test\\file2.txt")
        h1 = f1.get_handle()
        h2 = f2.get_handle()
        self.assertNotEqual(h1, h2)

    def test_file_with_data(self):
        """Test file creation with initial data."""
        data = b"Hello, World!"
        f = File(path="C:\\test\\file.txt", data=data)
        
        read_data = f.get_data()
        self.assertEqual(read_data, data)

    def test_add_data(self):
        """Test adding data to a file."""
        f = File(path="C:\\test\\file.txt")
        f.add_data(b"First ")
        f.add_data(b"Second")
        
        data = f.get_data(reset_pointer=True)
        self.assertEqual(data, b"First Second")

    def test_file_size(self):
        """Test file size calculation."""
        data = b"Test data content"
        f = File(path="C:\\test\\file.txt", data=data)
        self.assertEqual(f.get_size(), len(data))

    def test_file_seek_tell(self):
        """Test file seek and tell operations."""
        data = b"0123456789"
        f = File(path="C:\\test\\file.txt", data=data)
        
        # Seek from start
        f.seek(5, 0)  # SEEK_SET
        self.assertEqual(f.tell(), 5)
        
        # Read from current position
        read_data = f.get_data(size=3)
        self.assertEqual(read_data, b"567")

    def test_file_seek_from_current(self):
        """Test seeking from current position."""
        data = b"0123456789"
        f = File(path="C:\\test\\file.txt", data=data)
        
        f.seek(5, 0)  # Go to position 5
        f.seek(2, 1)  # SEEK_CUR - move 2 more
        self.assertEqual(f.tell(), 7)

    def test_file_seek_from_end(self):
        """Test seeking from end of file."""
        data = b"0123456789"
        f = File(path="C:\\test\\file.txt", data=data)
        
        f.seek(-3, 2)  # SEEK_END - 3 bytes from end
        self.assertEqual(f.tell(), 7)

    def test_is_directory(self):
        """Test directory detection (file is not directory)."""
        f = File(path="C:\\test\\file.txt")
        self.assertFalse(f.is_directory())

    def test_remove_data(self):
        """Test removing file data."""
        f = File(path="C:\\test\\file.txt", data=b"data")
        f.remove_data()
        # After removal, data should be empty BytesIO
        self.assertEqual(f.get_size(), 0)


class TestPipe(unittest.TestCase):
    """Test Pipe class functionality."""

    def test_pipe_creation(self):
        """Test pipe creation."""
        pipe = Pipe(
            name="\\\\.\\pipe\\TestPipe",
            mode=0,
            num_instances=1,
            out_size=4096,
            in_size=4096
        )
        self.assertIsNotNone(pipe)
        self.assertEqual(pipe.name, "\\\\.\\pipe\\TestPipe")

    def test_pipe_handle_allocation(self):
        """Test pipe handle allocation."""
        p1 = Pipe(name="\\\\.\\pipe\\Pipe1", mode=0, num_instances=1, out_size=1024, in_size=1024)
        p2 = Pipe(name="\\\\.\\pipe\\Pipe2", mode=0, num_instances=1, out_size=1024, in_size=1024)
        
        h1 = p1.get_handle()
        h2 = p2.get_handle()
        self.assertNotEqual(h1, h2)


class TestFileMap(unittest.TestCase):
    """Test FileMap class functionality."""

    def test_filemap_creation(self):
        """Test memory mapped file creation."""
        fm = FileMap(name="TestMap", size=4096, prot=0x04)  # PAGE_READWRITE
        self.assertEqual(fm.get_name(), "TestMap")
        self.assertEqual(fm.get_prot(), 0x04)

    def test_filemap_handle(self):
        """Test file map handle allocation."""
        fm1 = FileMap(name="Map1", size=4096, prot=0x04)
        fm2 = FileMap(name="Map2", size=4096, prot=0x04)
        
        h1 = fm1.get_handle()
        h2 = fm2.get_handle()
        self.assertNotEqual(h1, h2)

    def test_filemap_with_backed_file(self):
        """Test file map with backing file."""
        backing_file = File(path="C:\\test\\backing.dat", data=b"backed data")
        fm = FileMap(name="BackedMap", size=4096, prot=0x04, backed_file=backing_file)
        
        self.assertEqual(fm.get_backed_file(), backing_file)

    def test_filemap_add_view(self):
        """Test adding a view to file map."""
        fm = FileMap(name="TestMap", size=4096, prot=0x04)
        fm.add_view(base=0x10000, offset=0, size=4096, protect=0x04)
        
        self.assertIn(0x10000, fm.views)


class TestFileDuplicate(unittest.TestCase):
    """Test File duplication."""

    def test_file_duplicate(self):
        """Test file duplication."""
        f = File(path="C:\\test\\file.txt", data=b"test data")
        f.seek(2, 0)
        
        dup = f.duplicate()
        self.assertEqual(dup.get_path(), f.get_path())
        # Duplicate should have a different handle
        self.assertNotEqual(dup.get_handle(), f.get_handle())


class TestFileHash(unittest.TestCase):
    """Test file hash calculation."""

    def test_file_hash(self):
        """Test file hash calculation."""
        data = b"test data"
        f = File(path="C:\\test\\file.txt", data=data)
        
        file_hash = f.get_hash()
        self.assertIsNotNone(file_hash)
        # Should be SHA256 hash (64 chars)
        self.assertEqual(len(file_hash), 64)


if __name__ == '__main__':
    unittest.main()
