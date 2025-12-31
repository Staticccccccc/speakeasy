# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import ctypes

import speakeasy.winenv.defs.windows.com as comdefs
import speakeasy.winenv.api.usermode.com_api as com_api
from speakeasy.errors import Win32EmuError


class COM(object):
    """
    The Component Object Model (COM) manager for the emulator. This will manage COM interfaces.
    """
    def __init__(self, config):
        super(COM, self).__init__()
        self.interfaces = {}
        self.config = config
        self._generic_stub_addr = None  # Cache for generic stub address

    def _get_generic_stub_addr(self, emu):
        """Get or create the address for the generic COM stub handler."""
        if self._generic_stub_addr is None:
            # Get the generic stub method
            if hasattr(com_api.ComApi, 'COM_GenericStub'):
                method = getattr(com_api.ComApi, 'COM_GenericStub')
                self._generic_stub_addr = emu.add_callback(com_api.ComApi.name, 
                                                           method.__apihook__[0])
        return self._generic_stub_addr

    def get_interface(self, emu, ptr_size, name):
        """
        Get COM interface.
        All vtable slots are first filled with a generic fallback handler,
        then specific implementations are overlaid where available.
        """
        iface = comdefs.IFACE_TYPES.get(name)
        if not iface:
            raise Win32EmuError('Invalid COM interface: %s' % (name))

        ci = comdefs.ComInterface(iface, name, ptr_size)
        vtable_size = emu.sizeof(ci.iface)
        com_ptr = emu.mem_map(vtable_size, tag='emu.COM.%s' % (name))
        ci.address = com_ptr

        # Get the generic stub address
        generic_stub_addr = self._get_generic_stub_addr(emu)

        # First pass: fill ALL vtable slots with the generic fallback handler
        # This ensures no slot is left as NULL (0), preventing crashes
        num_slots = vtable_size // ptr_size
        for i in range(num_slots):
            if generic_stub_addr:
                emu.mem_write(com_ptr + i * ptr_size, 
                              generic_stub_addr.to_bytes(ptr_size, 'little'))

        # Second pass: overlay specific implementations where available
        fields = ci.iface.__dict__['__fields__']
        field_offset = 0
        for field in fields:
            field_name, field_obj = field
            # Determine if the field is an inherited interface (e.g., IUnknown)
            if issubclass(field_obj, ctypes.Structure):
                if field_name not in comdefs.IFACE_TYPES:
                    raise Win32EmuError('COM interface %s inherits unsupported interface %s' %
                                        (name, field_name))

                # Iterate inherited interface fields
                for subfield in field_obj._fields_:
                    subfield_name, subfield_type = subfield
                    if issubclass(subfield_type, (ctypes.c_uint32, ctypes.c_ulong,
                                                  ctypes.c_ulonglong)):
                        # Try interface-specific method first, then generic inherited method
                        method_names = [
                            '%s_%s' % (name, subfield_name),  # e.g., ITaskService_QueryInterface
                            '%s_%s' % (field_name, subfield_name)  # e.g., IUnknown_QueryInterface
                        ]
                        for method_name in method_names:
                            if hasattr(com_api.ComApi, method_name):
                                method = getattr(com_api.ComApi, method_name)
                                addr = emu.add_callback(com_api.ComApi.name, method.__apihook__[0])
                                emu.mem_write(com_ptr + field_offset, addr.to_bytes(ptr_size, 'little'))
                                break

                    field_offset += ptr_size
            elif issubclass(field_obj, (ctypes.c_uint32, ctypes.c_ulong, ctypes.c_ulonglong)):
                # Field is a method; hook if supported
                method_name = '%s_%s' % (name, field_name)
                if hasattr(com_api.ComApi, method_name):
                    method = getattr(com_api.ComApi, method_name)
                    addr = emu.add_callback(com_api.ComApi.name, method.__apihook__[0])
                    emu.mem_write(com_ptr + field_offset, addr.to_bytes(ptr_size, 'little'))

                field_offset += ptr_size
            else:
                raise Win32EmuError('Invalid field type encountered for %s.%s' %
                                    (name, field_name))

        return ci
