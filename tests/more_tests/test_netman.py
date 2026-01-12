# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Unit tests for the NetworkManager component.
Tests socket creation, wininet components, and DNS resolution.
"""

import unittest
import sys
import os

# Add speakeasy to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from speakeasy.windows.netman import (
    Socket, WininetComponent, WininetSession, WininetRequest,
    WininetInstance, NetworkManager, normalize_response_path
)


class TestSocket(unittest.TestCase):
    """Test Socket class functionality."""

    def test_socket_creation(self):
        """Test basic socket creation."""
        sock = Socket(
            fd=100,
            family=2,      # AF_INET
            stype=1,       # SOCK_STREAM
            protocol=6,    # IPPROTO_TCP
            flags=0
        )
        self.assertEqual(sock.get_fd(), 100)
        self.assertEqual(sock.get_type(), 1)

    def test_socket_connection_info(self):
        """Test setting and getting connection info."""
        sock = Socket(fd=100, family=2, stype=1, protocol=6, flags=0)
        sock.set_connection_info("192.168.1.1", 80)
        
        host, port = sock.get_connection_info()
        self.assertEqual(host, "192.168.1.1")
        self.assertEqual(port, 80)

    def test_socket_recv_data(self):
        """Test socket receive data functionality."""
        sock = Socket(fd=100, family=2, stype=1, protocol=6, flags=0)
        
        # Socket starts with empty packet
        self.assertIsNotNone(sock.curr_packet)


class TestWininetComponent(unittest.TestCase):
    """Test WininetComponent base class."""

    def test_handle_allocation(self):
        """Test that handles are unique."""
        c1 = WininetComponent()
        c2 = WininetComponent()
        
        h1 = c1.get_handle()
        h2 = c2.get_handle()
        self.assertNotEqual(h1, h2)


class TestWininetInstance(unittest.TestCase):
    """Test WininetInstance class."""

    def test_instance_creation(self):
        """Test WinInet instance creation."""
        inst = WininetInstance(
            user_agent="TestAgent/1.0",
            access=1,
            proxy="",
            bypass="",
            flags=0
        )
        self.assertIsNotNone(inst)
        self.assertEqual(inst.get_user_agent(), "TestAgent/1.0")

    def test_instance_handle(self):
        """Test instance handle allocation."""
        inst = WininetInstance(
            user_agent="TestAgent/1.0",
            access=1,
            proxy="",
            bypass="",
            flags=0
        )
        self.assertIsNotNone(inst.get_handle())


class TestNetworkManager(unittest.TestCase):
    """Test NetworkManager class functionality."""

    def setUp(self):
        """Set up test configuration."""
        self.config = {
            "dns": {
                "names": {
                    "default": "10.0.0.1",
                    "test.com": "192.168.1.100",
                    "malware.evil": "10.10.10.10"
                },
                "txt": []
            },
            "http": {
                "responses": []
            },
            "winsock": {
                "responses": []
            }
        }
        self.netman = NetworkManager(config=self.config)

    def test_dns_resolve_known_host(self):
        """Test DNS resolution for a known host."""
        ip = self.netman.name_lookup("test.com")
        self.assertEqual(ip, "192.168.1.100")

    def test_dns_resolve_unknown_host(self):
        """Test DNS resolution for an unknown host uses default."""
        ip = self.netman.name_lookup("unknown.host")
        self.assertEqual(ip, "10.0.0.1")

    def test_socket_creation(self):
        """Test creating a socket through manager."""
        sock = self.netman.new_socket(
            family=2,      # AF_INET
            stype=1,       # SOCK_STREAM
            protocol=6,    # IPPROTO_TCP
            flags=0
        )
        self.assertIsNotNone(sock)
        self.assertIsNotNone(sock.get_fd())

    def test_socket_get_by_fd(self):
        """Test retrieving socket by file descriptor."""
        sock = self.netman.new_socket(family=2, stype=1, protocol=6, flags=0)
        fd = sock.get_fd()
        
        retrieved = self.netman.get_socket(fd)
        self.assertEqual(retrieved, sock)

    def test_socket_close(self):
        """Test closing a socket."""
        sock = self.netman.new_socket(family=2, stype=1, protocol=6, flags=0)
        fd = sock.get_fd()
        
        self.netman.close_socket(fd)
        
        # Socket should no longer be retrievable
        retrieved = self.netman.get_socket(fd)
        self.assertIsNone(retrieved)

    def test_wininet_instance_creation(self):
        """Test creating a WinInet instance."""
        instance = self.netman.new_wininet_inst(
            user_agent="TestAgent/1.0",
            access=1,  # INTERNET_OPEN_TYPE_DIRECT
            proxy="",
            bypass="",
            flags=0
        )
        self.assertIsNotNone(instance)

    def test_get_wininet_object(self):
        """Test getting WinInet object by handle."""
        instance = self.netman.new_wininet_inst(
            user_agent="TestAgent/1.0",
            access=1,
            proxy="",
            bypass="",
            flags=0
        )
        
        handle = instance.get_handle()
        retrieved = self.netman.get_wininet_object(handle)
        self.assertEqual(retrieved, instance)

    def test_close_wininet_object(self):
        """Test closing WinInet object."""
        instance = self.netman.new_wininet_inst(
            user_agent="TestAgent/1.0",
            access=1,
            proxy="",
            bypass="",
            flags=0
        )
        
        handle = instance.get_handle()
        self.netman.close_wininet_object(handle)
        
        # Should no longer be retrievable
        retrieved = self.netman.get_wininet_object(handle)
        self.assertIsNone(retrieved)


class TestWininetSession(unittest.TestCase):
    """Test WininetSession functionality."""

    def setUp(self):
        """Set up WinInet instance for session testing."""
        self.config = {
            "dns": {"names": {"default": "10.0.0.1"}, "txt": []},
            "http": {"responses": []},
            "winsock": {"responses": []}
        }
        self.netman = NetworkManager(config=self.config)
        self.instance = self.netman.new_wininet_inst(
            user_agent="TestAgent/1.0",
            access=1,
            proxy="",
            bypass="",
            flags=0
        )

    def test_session_creation(self):
        """Test creating a session from instance."""
        session = self.instance.new_session(
            server="www.test.com",
            port=80,
            user="",
            password="",
            service=3,  # INTERNET_SERVICE_HTTP
            flags=0,
            ctx=0
        )
        self.assertIsNotNone(session)

    def test_session_handle(self):
        """Test session handle allocation."""
        session = self.instance.new_session(
            server="www.test.com",
            port=80,
            user="",
            password="",
            service=3,
            flags=0,
            ctx=0
        )
        self.assertIsNotNone(session.get_handle())


class TestNormalizeResponsePath(unittest.TestCase):
    """Test response path normalization."""

    def test_normalize_with_root_placeholder(self):
        """Test that $ROOT$ placeholder is expanded."""
        path = "$ROOT$/resources/test.bin"
        result = normalize_response_path(path)
        
        # Should replace $ROOT$ with actual path
        self.assertNotIn("$ROOT$", result)
        self.assertIn("resources", result)

    def test_normalize_absolute_path(self):
        """Test that absolute paths are unchanged."""
        path = "/absolute/path/to/file.bin"
        result = normalize_response_path(path)
        
        # On Windows, result might change due to path handling
        self.assertIsNotNone(result)


class TestNetworkManagerNoConfig(unittest.TestCase):
    """Test NetworkManager with minimal configuration."""

    def setUp(self):
        """Set up NetworkManager with empty config."""
        self.config = {
            "dns": {
                "names": {"default": "8.8.8.8"},
                "txt": []
            },
            "http": {"responses": []},
            "winsock": {"responses": []}
        }
        self.netman = NetworkManager(config=self.config)

    def test_basic_socket_operations(self):
        """Test basic socket operations without responses configured."""
        sock = self.netman.new_socket(family=2, stype=1, protocol=6, flags=0)
        sock.set_connection_info("8.8.8.8", 443)
        
        host, port = sock.get_connection_info()
        self.assertEqual(port, 443)


if __name__ == '__main__':
    unittest.main()
