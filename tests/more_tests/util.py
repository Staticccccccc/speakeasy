# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

"""
Utility functions for extended speakeasy tests.
"""

import os
import sys
import json
import lzma
import multiprocessing as mp

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speakeasy import Speakeasy


def get_test_bin_path(bin_name):
    """Get path to a test binary in the bins directory."""
    fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bins', bin_name)
    return fp


def get_test_bin_data(bin_name):
    """Load and decompress a test binary."""
    fp = get_test_bin_path(bin_name)
    with lzma.open(fp) as f:
        file_content = f.read()
    return file_content


def get_config():
    """Load the test configuration."""
    fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.json')
    with open(fp, 'r') as f:
        return json.load(f)


def get_minimal_config():
    """Get a minimal configuration for unit tests."""
    return {
        "config_version": 0.2,
        "emu_engine": "unicorn",
        "timeout": 60,
        "system": "windows",
        "analysis": {
            "memory_tracing": False,
            "strings": False
        },
        "exceptions": {
            "dispatch_handlers": True
        },
        "os_ver": {
            "name": "windows",
            "major": 6,
            "minor": 1,
            "build": 7601
        },
        "current_dir": "C:\\Windows\\system32",
        "command_line": "test.exe",
        "env": {
            "comspec": "C:\\Windows\\system32\\cmd.exe",
            "systemroot": "C:\\Windows\\system32",
            "windir": "C:\\Windows"
        },
        "hostname": "testbox",
        "user": {
            "name": "testuser"
        },
        "symlinks": [],
        "filesystem": {
            "files": []
        },
        "registry": {
            "keys": [
                {
                    "path": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Test",
                    "values": [
                        {
                            "name": "StringValue",
                            "type": "REG_SZ",
                            "data": "TestData"
                        },
                        {
                            "name": "DwordValue",
                            "type": "REG_DWORD",
                            "data": "0x12345678"
                        }
                    ]
                }
            ]
        },
        "network": {
            "dns": {
                "names": {
                    "default": "10.1.2.3",
                    "test.com": "192.168.1.1"
                }
            },
            "http": {
                "responses": []
            },
            "winsock": {
                "responses": []
            }
        },
        "processes": [
            {
                "name": "main",
                "base_addr": "0x00400000",
                "path": "C:\\Windows\\system32\\main.exe",
                "command_line": "test.exe",
                "is_main_exe": True,
                "session": 1
            }
        ],
        "modules": {
            "modules_always_exist": False,
            "system_modules": [],
            "user_modules": []
        }
    }


def _run_module(q, cfg, target, logger, argv):
    """Run a module in a separate process."""
    se = Speakeasy(config=cfg, logger=logger, argv=argv)
    module = se.load_module(data=target)
    se.run_module(module, all_entrypoints=True)
    report = se.get_report()
    q.put(report)


def run_test(cfg, target, logger=None, argv=[]):
    """Run a test binary and return the report."""
    q = mp.Queue()
    p = mp.Process(target=_run_module, args=(q, cfg, target, logger, argv))
    p.start()
    return q.get()


def _run_shellcode(q, cfg, data, arch, logger):
    """Run shellcode in a separate process."""
    se = Speakeasy(config=cfg, logger=logger)
    sc_addr = se.load_shellcode(fpath=None, arch=arch, data=data)
    se.run_shellcode(sc_addr)
    report = se.get_report()
    q.put(report)


def run_shellcode_test(cfg, data, arch='x86', logger=None):
    """Run shellcode and return the report."""
    q = mp.Queue()
    p = mp.Process(target=_run_shellcode, args=(q, cfg, data, arch, logger))
    p.start()
    return q.get()
