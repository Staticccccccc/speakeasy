# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

from .. import api
import speakeasy.winenv.defs.windows.com as comdefs


class ComApi(api.ApiHandler):
    """
    Implements COM interfaces
    """
    name = 'com_api'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(ComApi, self).__init__(emu)

        self.funcs = {}
        self.data = {}

        super(ComApi, self).__get_hook_attrs__(self)

    # First argument (self) is not reflected in method definitions; note this increases argc by 1
    @apihook('IUnknown.QueryInterface', argc=3)
    def IUnknown_QueryInterface(self, emu, argv, ctx={}):
        """
        HRESULT QueryInterface(
            REFIID riid,
            void   **ppvObject
        );
        """
        # not implemented
        return comdefs.S_OK

    @apihook('IUnknown.AddRef', argc=1)
    def IUnknown_AddRef(self, emu, argv, ctx={}):
        """
        ULONG AddRef();
        """
        # not implemented
        return 1

    @apihook('IUnknown.Release', argc=1)
    def IUnknown_Release(self, emu, argv, ctx={}):
        """
        ULONG Release();
        """
        # not implemented
        return 0

    @apihook('IWbemLocator.ConnectServer', argc=9)
    def IWbemLocator_ConnectServer(self, emu, argv, ctx={}):
        """
        HRESULT ConnectServer(
            const BSTR    strNetworkResource,
            const BSTR    strUser,
            const BSTR    strPassword,
            const BSTR    strLocale,
            long          lSecurityFlags,
            const BSTR    strAuthority,
            IWbemContext  *pCtx,
            IWbemServices **ppNamespace
        );
        """
        ptr, strNetworkResource, strUser, strPassword, strLocale, lSecurityFlags, strAuthority, \
            pCtx, ppNamespace = argv
        argv[1] = self.read_wide_string(strNetworkResource)

        if ppNamespace:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IWbemServices')
            pNamespace = self.mem_alloc(emu.get_ptr_size(),
                                        tag='emu.COM.ppNamespace_IWbemServices')
            self.mem_write(pNamespace, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppNamespace, pNamespace.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('IWbemServices.ExecQuery', argc=6)
    def IWbemServices_ExecQuery(self, emu, argv, ctx={}):
        """
        HRESULT ExecQuery(
            const BSTR           strQueryLanguage,
            const BSTR           strQuery,
            long                 lFlags,
            IWbemContext         *pCtx,
            IEnumWbemClassObject **ppEnum
        );
        """
        ptr, strQueryLanguage, strQuery, lFlags, pCtx, ppEnum = argv
        argv[1] = self.read_wide_string(strQueryLanguage)
        argv[2] = self.read_wide_string(strQuery)

        # not implemented so returning -1
        return -1

    @apihook('IWinHttpRequest.Open', argc=6)
    def IWinHttpRequest_Open(self, emu, argv, ctx={}):
        """
        HRESULT Open(
            BSTR    Method,
            BSTR    Url,
            VARIANT Async,
            VARIANT User,
            VARIANT Password,
            VARIANT LogonPolicy
        );
        """
        ptr, method, url, async_v, user, password, logon = argv
        method_str = self.read_wide_string(method)
        url_str = self.read_wide_string(url)
        
        if self.emu.logger:
            self.emu.logger.info('IWinHttpRequest::Open(%s, %s)', method_str, url_str)

        return comdefs.S_OK

    @apihook('IWinHttpRequest.Send', argc=2)
    def IWinHttpRequest_Send(self, emu, argv, ctx={}):
        """
        HRESULT Send(
            VARIANT Body
        );
        """
        if self.emu.logger:
            self.emu.logger.info('IWinHttpRequest::Send')
        return comdefs.S_OK

    @apihook('IWinHttpRequest.SetRequestHeader', argc=3)
    def IWinHttpRequest_SetRequestHeader(self, emu, argv, ctx={}):
        """
        HRESULT SetRequestHeader(
            BSTR Header,
            BSTR Value
        );
        """
        ptr, header, value = argv
        header_str = self.read_wide_string(header)
        value_str = self.read_wide_string(value)

        if self.emu.logger:
            self.emu.logger.info('IWinHttpRequest::SetRequestHeader(%s, %s)', header_str, value_str)
        
        return comdefs.S_OK

    @apihook('IWinHttpRequest.ResponseText', argc=2)
    def IWinHttpRequest_ResponseText(self, emu, argv, ctx={}):
        """
        HRESULT ResponseText(
            BSTR *Body
        );
        """
        ptr, body = argv
        
        # Return empty string or mock data
        # For now, just empty string
        s = 'Mock Response'.encode('utf-16le') + b'\x00\x00'
        buf = self.mem_alloc(len(s), tag='api.IWinHttpRequest.ResponseText')
        self.mem_write(buf, s)
        self.mem_write(body, buf.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('IWinHttpRequest.Status', argc=2)
    def IWinHttpRequest_Status(self, emu, argv, ctx={}):
        """
        HRESULT Status(
            long *Status
        );
        """
        ptr, status = argv
        self.mem_write(status, (200).to_bytes(4, 'little'))
        return comdefs.S_OK
