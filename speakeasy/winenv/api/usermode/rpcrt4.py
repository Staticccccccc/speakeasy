# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import random
import uuid

import speakeasy.winenv.defs.windows.windows as windefs
import speakeasy.winenv.arch as _arch

from .. import api

class RPCRT4(api.ApiHandler):
    """
    Implements exported functions from rpcrt4.dll
    """
    name = 'rpcrt4'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):
        super(RPCRT4, self).__init__(emu)
        self.rpc_binding_handle = 0x1000  # Counter for RPC binding handles

    def get_rpc_handle(self):
        """Generate a new RPC binding handle"""
        self.rpc_binding_handle += 4
        return self.rpc_binding_handle

    @apihook('UuidCreate', argc=1)
    def UuidCreate(self, emu, argv, ctx={}):
        """
        RPC_STATUS UuidCreate(
          UUID *Uuid
        );
        """
        uuidp, = argv

        if not uuidp:
            return 1

        new_uuid = windefs.GUID()
        new_uuid.Data1 = random.randint(0, 0xffffffff)
        new_uuid.Data2 = random.randint(0, 0xffffffff) & 0xffff
        new_uuid.Data3 = random.randint(0, 0xffffffff) & 0xffff
        new_uuid.Data4 = random.randbytes(8)

        self.mem_write(uuidp, new_uuid.get_bytes())

        return 0
    
    @apihook('UuidToStringA', argc=2)
    def UuidToStringA(self, emu, argv, ctx={}):
        """
        RPC_STATUS UuidToStringA(
          const UUID *Uuid,
          RPC_CSTR   *StringUuid
        );
        """
        uuidp, stringp = argv

        if not uuidp or not stringp:
            return 1

        uuid_bytes = self.mem_read(uuidp, windefs.GUID().sizeof())
        uuid_obj = uuid.UUID(bytes=uuid_bytes)

        string = str(uuid_obj)

        self.mem_write(stringp, string.encode("utf-8"))

        return 0

    @apihook('RpcStringBindingComposeW', argc=6)
    def RpcStringBindingComposeW(self, emu, argv, ctx={}):
        """
        RPC_STATUS RpcStringBindingComposeW(
          RPC_WSTR ObjUuid,
          RPC_WSTR ProtSeq,
          RPC_WSTR NetworkAddr,
          RPC_WSTR Endpoint,
          RPC_WSTR Options,
          RPC_WSTR *StringBinding
        );
        """
        obj_uuid, prot_seq, network_addr, endpoint, options, string_binding = argv

        # Read the input strings (wide strings)
        uuid_str = ''
        if obj_uuid:
            uuid_str = self.read_mem_string(obj_uuid, 2)
            argv[0] = uuid_str

        protseq_str = ''
        if prot_seq:
            protseq_str = self.read_mem_string(prot_seq, 2)
            argv[1] = protseq_str

        addr_str = ''
        if network_addr:
            addr_str = self.read_mem_string(network_addr, 2)
            argv[2] = addr_str

        endpoint_str = ''
        if endpoint:
            endpoint_str = self.read_mem_string(endpoint, 2)
            argv[3] = endpoint_str

        options_str = ''
        if options:
            options_str = self.read_mem_string(options, 2)
            argv[4] = options_str

        # Compose the string binding in the format:
        # ObjUuid@ProtSeq:NetworkAddr[Endpoint,Options]
        binding = ''
        if uuid_str:
            binding += uuid_str + '@'
        if protseq_str:
            binding += protseq_str
        if addr_str:
            binding += ':' + addr_str
        if endpoint_str or options_str:
            binding += '['
            if endpoint_str:
                binding += endpoint_str
            if options_str:
                if endpoint_str:
                    binding += ','
                binding += options_str
            binding += ']'

        # Write the result if StringBinding is provided
        if string_binding:
            # Allocate memory for the string and write it
            binding_bytes = (binding + '\x00').encode('utf-16le')
            ptr = self.mem_alloc(len(binding_bytes), tag='api.RpcStringBindingComposeW')
            self.mem_write(ptr, binding_bytes)
            # Write the pointer to the output parameter
            self.mem_write(string_binding, ptr.to_bytes(emu.get_ptr_size(), 'little'))

        return 0  # RPC_S_OK

    @apihook('RpcBindingFromStringBindingW', argc=2)
    def RpcBindingFromStringBindingW(self, emu, argv, ctx={}):
        """
        RPC_STATUS RpcBindingFromStringBindingW(
          RPC_WSTR           StringBinding,
          RPC_BINDING_HANDLE *Binding
        );
        """
        string_binding, binding = argv

        # Read the string binding if provided
        if string_binding:
            binding_str = self.read_mem_string(string_binding, 2)
            argv[0] = binding_str

        # Create a new RPC binding handle
        if binding:
            handle = self.get_rpc_handle()
            self.mem_write(binding, handle.to_bytes(emu.get_ptr_size(), 'little'))

        return 0  # RPC_S_OK

    @apihook('RpcBindingSetAuthInfoExA', argc=7)
    def RpcBindingSetAuthInfoExA(self, emu, argv, ctx={}):
        """
        RPC_STATUS RpcBindingSetAuthInfoExA(
          RPC_BINDING_HANDLE       Binding,
          RPC_CSTR                 ServerPrincName,
          unsigned long            AuthnLevel,
          unsigned long            AuthnSvc,
          RPC_AUTH_IDENTITY_HANDLE AuthIdentity,
          unsigned long            AuthzSvc,
          RPC_SECURITY_QOS         *SecurityQos
        );
        """
        binding, server_princ_name, authn_level, authn_svc, auth_identity, authz_svc, security_qos = argv

        # Read the server principal name if provided
        if server_princ_name:
            princ_name = self.read_mem_string(server_princ_name, 1)
            argv[1] = princ_name

        # This is a stub - in emulation we don't need actual authentication
        # Just return success
        return 0  # RPC_S_OK

    @apihook('RpcStringFreeW', argc=1)
    def RpcStringFreeW(self, emu, argv, ctx={}):
        """
        RPC_STATUS RpcStringFreeW(
          RPC_WSTR *String
        );
        """
        string_ptr, = argv

        if string_ptr:
            # Read the pointer to the string
            ptr_size = emu.get_ptr_size()
            ptr_bytes = self.mem_read(string_ptr, ptr_size)
            str_ptr = int.from_bytes(ptr_bytes, 'little')
            
            # Free the string memory if it's valid
            if str_ptr:
                self.mem_free(str_ptr)
            
            # Set the pointer to NULL
            self.mem_write(string_ptr, (0).to_bytes(ptr_size, 'little'))

        return 0  # RPC_S_OK

    @apihook('NdrClientCall2', argc=2, conv=_arch.CALL_CONV_CDECL)
    def NdrClientCall2(self, emu, argv, ctx={}):
        """
        CLIENT_CALL_RETURN RPC_VAR_ENTRY NdrClientCall2(
          PMIDL_STUB_DESC pStubDescriptor,
          PFORMAT_STRING  pFormat,
          ...
        );

        This is the client-side entry point for /Oicf mode RPC stubs.
        It's a variadic function used for RPC marshaling.
        """
        pStubDescriptor, pFormat = argv

        # This is a stub - actual RPC calls cannot be made during emulation
        # Return 0 to indicate success
        return 0
