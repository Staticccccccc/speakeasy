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

    # Generic COM stub for unmapped vtable entries
    @apihook('COM.GenericStub', argc=8)
    def COM_GenericStub(self, emu, argv, ctx={}):
        """
        Generic fallback handler for unmapped COM interface methods.
        Returns S_OK (0) to allow emulation to continue.
        This catches any COM method call that doesn't have a specific implementation.
        """
        # The ctx should contain interface and method info if available
        iface_name = ctx.get('iface_name', 'Unknown')
        method_index = ctx.get('method_index', -1)
        if self.emu.logger:
            self.emu.logger.debug('COM GenericStub called: %s method[%d] with %d args',
                                  iface_name, method_index, len(argv))
        return comdefs.S_OK


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

    # ====== IDispatch methods ======

    @apihook('IDispatch.GetTypeInfoCount', argc=2)
    def IDispatch_GetTypeInfoCount(self, emu, argv, ctx={}):
        """
        HRESULT GetTypeInfoCount(UINT *pctinfo);
        """
        ptr, pctinfo = argv
        if pctinfo:
            self.mem_write(pctinfo, (1).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IDispatch.GetTypeInfo', argc=4)
    def IDispatch_GetTypeInfo(self, emu, argv, ctx={}):
        """
        HRESULT GetTypeInfo(UINT iTInfo, LCID lcid, ITypeInfo **ppTInfo);
        """
        ptr, iTInfo, lcid, ppTInfo = argv
        if ppTInfo:
            self.mem_write(ppTInfo, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IDispatch.GetIDsOfNames', argc=6)
    def IDispatch_GetIDsOfNames(self, emu, argv, ctx={}):
        """
        HRESULT GetIDsOfNames(REFIID riid, LPOLESTR *rgszNames, UINT cNames, LCID lcid, DISPID *rgDispId);
        """
        ptr, riid, rgszNames, cNames, lcid, rgDispId = argv
        # Return fake DISPID values
        if rgDispId and cNames > 0:
            for i in range(cNames):
                self.mem_write(rgDispId + i * 4, (i + 1).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IDispatch.Invoke', argc=9)
    def IDispatch_Invoke(self, emu, argv, ctx={}):
        """
        HRESULT Invoke(DISPID dispIdMember, REFIID riid, LCID lcid, WORD wFlags,
                       DISPPARAMS *pDispParams, VARIANT *pVarResult,
                       EXCEPINFO *pExcepInfo, UINT *puArgErr);
        """
        # Just return success - we're not actually invoking anything
        return comdefs.S_OK

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

    # ====== Task Scheduler COM Interfaces ======
    # Since vtables are flattened, we need interface-specific IUnknown/IDispatch methods

    @apihook('ITaskService.QueryInterface', argc=3)
    def ITaskService_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskService.AddRef', argc=1)
    def ITaskService_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('ITaskService.Release', argc=1)
    def ITaskService_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('ITaskService.GetTypeInfoCount', argc=2)
    def ITaskService_GetTypeInfoCount(self, emu, argv, ctx={}):
        ptr, pctinfo = argv
        if pctinfo:
            self.mem_write(pctinfo, (1).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.GetTypeInfo', argc=4)
    def ITaskService_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskService.GetIDsOfNames', argc=6)
    def ITaskService_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskService.Invoke', argc=9)
    def ITaskService_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskService.Connect', argc=5)

    def ITaskService_Connect(self, emu, argv, ctx={}):
        """
        HRESULT Connect(
            VARIANT serverName,
            VARIANT user,
            VARIANT domain,
            VARIANT password
        );
        """
        ptr, serverName, user, domain, password = argv
        # Just return success - we're not actually connecting to a scheduler
        return comdefs.S_OK

    @apihook('ITaskService.GetFolder', argc=3)
    def ITaskService_GetFolder(self, emu, argv, ctx={}):
        """
        HRESULT GetFolder(
            BSTR path,
            ITaskFolder **ppFolder
        );
        """
        ptr, path, ppFolder = argv
        
        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str

        if ppFolder:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskFolder')
            pFolder = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppFolder_ITaskFolder')
            self.mem_write(pFolder, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppFolder, pFolder.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('ITaskService.NewTask', argc=3)
    def ITaskService_NewTask(self, emu, argv, ctx={}):
        """
        HRESULT NewTask(
            DWORD flags,
            ITaskDefinition **ppDefinition
        );
        """
        ptr, flags, ppDefinition = argv

        if ppDefinition:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskDefinition')
            pDef = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppDefinition_ITaskDefinition')
            self.mem_write(pDef, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppDefinition, pDef.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('ITaskService.Connected', argc=2)
    def ITaskService_Connected(self, emu, argv, ctx={}):
        """
        HRESULT Connected(
            VARIANT_BOOL *pConnected
        );
        """
        ptr, pConnected = argv
        if pConnected:
            # VARIANT_TRUE = -1 (0xFFFF)
            self.mem_write(pConnected, (0xFFFF).to_bytes(2, 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.GetRunningTasks', argc=3)
    def ITaskService_GetRunningTasks(self, emu, argv, ctx={}):
        """
        HRESULT GetRunningTasks(
            long flags,
            IRunningTaskCollection **ppRunningTasks
        );
        """
        ptr, flags, ppRunningTasks = argv
        # Return empty collection (NULL pointer)
        if ppRunningTasks:
            self.mem_write(ppRunningTasks, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.TargetServer', argc=2)
    def ITaskService_TargetServer(self, emu, argv, ctx={}):
        """
        HRESULT get_TargetServer(
            BSTR *pServer
        );
        """
        ptr, pServer = argv
        if pServer:
            # Return empty string
            self.mem_write(pServer, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.ConnectedUser', argc=2)
    def ITaskService_ConnectedUser(self, emu, argv, ctx={}):
        """
        HRESULT get_ConnectedUser(
            BSTR *pUser
        );
        """
        ptr, pUser = argv
        if pUser:
            self.mem_write(pUser, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.ConnectedDomain', argc=2)
    def ITaskService_ConnectedDomain(self, emu, argv, ctx={}):
        """
        HRESULT get_ConnectedDomain(
            BSTR *pDomain
        );
        """
        ptr, pDomain = argv
        if pDomain:
            self.mem_write(pDomain, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskService.HighestVersion', argc=2)
    def ITaskService_HighestVersion(self, emu, argv, ctx={}):
        """
        HRESULT get_HighestVersion(
            DWORD *pVersion
        );
        """
        ptr, pVersion = argv
        if pVersion:
            # Return version 1.3 (Windows 7+)
            self.mem_write(pVersion, (0x10003).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.RegisterTaskDefinition', argc=9)
    def ITaskFolder_RegisterTaskDefinition(self, emu, argv, ctx={}):
        """
        HRESULT RegisterTaskDefinition(
            BSTR path,
            ITaskDefinition *pDefinition,
            long flags,
            VARIANT userId,
            VARIANT password,
            TASK_LOGON_TYPE logonType,
            VARIANT sddl,
            IRegisteredTask **ppTask
        );
        """
        # argc=9: ptr + 8 params
        ptr = argv[0] if len(argv) > 0 else 0
        path = argv[1] if len(argv) > 1 else 0
        ppTask = argv[8] if len(argv) > 8 else 0

        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str
            if self.emu.logger:
                self.emu.logger.info('ITaskFolder::RegisterTaskDefinition - Task: %s', path_str)

        if ppTask:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IRegisteredTask')
            pTask = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppTask_IRegisteredTask')
            self.mem_write(pTask, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppTask, pTask.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('ITaskFolder.RegisterTask', argc=9)
    def ITaskFolder_RegisterTask(self, emu, argv, ctx={}):
        """
        HRESULT RegisterTask(
            BSTR path,
            BSTR xmlText,
            long flags,
            VARIANT userId,
            VARIANT password,
            TASK_LOGON_TYPE logonType,
            VARIANT sddl,
            IRegisteredTask **ppTask
        );
        """
        # argc=9: ptr + 8 params
        if len(argv) >= 9:
            ptr, path, xmlText, flags, userId, password, logonType, sddl, ppTask = argv[:9]
        else:
            ptr = argv[0] if len(argv) > 0 else 0
            path = argv[1] if len(argv) > 1 else 0
            ppTask = argv[-1] if len(argv) > 1 else 0

        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str
            if self.emu.logger:
                self.emu.logger.info('ITaskFolder::RegisterTask - Task: %s', path_str)

        if ppTask:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IRegisteredTask')
            pTask = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppTask_IRegisteredTask')
            self.mem_write(pTask, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppTask, pTask.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('ITaskFolder.CreateFolder', argc=4)
    def ITaskFolder_CreateFolder(self, emu, argv, ctx={}):
        """
        HRESULT CreateFolder(
            BSTR subFolderName,
            VARIANT sddl,
            ITaskFolder **ppFolder
        );
        """
        ptr, subFolderName, sddl, ppFolder = argv

        if subFolderName:
            name_str = self.read_wide_string(subFolderName)
            argv[1] = name_str

        if ppFolder:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskFolder')
            pFolder = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppFolder_ITaskFolder')
            self.mem_write(pFolder, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppFolder, pFolder.to_bytes(emu.get_ptr_size(), 'little'))

        return comdefs.S_OK

    @apihook('ITaskFolder.DeleteTask', argc=3)
    def ITaskFolder_DeleteTask(self, emu, argv, ctx={}):
        """
        HRESULT DeleteTask(
            BSTR name,
            long flags
        );
        """
        ptr, name, flags = argv

        if name:
            name_str = self.read_wide_string(name)
            argv[1] = name_str
            if self.emu.logger:
                self.emu.logger.info('ITaskFolder::DeleteTask - Task: %s', name_str)

        return comdefs.S_OK

    # ====== ITaskFolder IUnknown/IDispatch methods ======

    @apihook('ITaskFolder.QueryInterface', argc=3)
    def ITaskFolder_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskFolder.AddRef', argc=1)
    def ITaskFolder_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('ITaskFolder.Release', argc=1)
    def ITaskFolder_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('ITaskFolder.GetTypeInfoCount', argc=2)
    def ITaskFolder_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskFolder.GetTypeInfo', argc=4)
    def ITaskFolder_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskFolder.GetIDsOfNames', argc=6)
    def ITaskFolder_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskFolder.Invoke', argc=9)
    def ITaskFolder_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== ITaskDefinition IUnknown/IDispatch methods ======

    @apihook('ITaskDefinition.QueryInterface', argc=3)
    def ITaskDefinition_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskDefinition.AddRef', argc=1)
    def ITaskDefinition_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('ITaskDefinition.Release', argc=1)
    def ITaskDefinition_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('ITaskDefinition.GetTypeInfoCount', argc=2)
    def ITaskDefinition_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskDefinition.GetTypeInfo', argc=4)
    def ITaskDefinition_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskDefinition.GetIDsOfNames', argc=6)
    def ITaskDefinition_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskDefinition.Invoke', argc=9)
    def ITaskDefinition_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== IRegisteredTask IUnknown/IDispatch methods ======

    @apihook('IRegisteredTask.QueryInterface', argc=3)
    def IRegisteredTask_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegisteredTask.AddRef', argc=1)
    def IRegisteredTask_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('IRegisteredTask.Release', argc=1)
    def IRegisteredTask_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('IRegisteredTask.GetTypeInfoCount', argc=2)
    def IRegisteredTask_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegisteredTask.GetTypeInfo', argc=4)
    def IRegisteredTask_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegisteredTask.GetIDsOfNames', argc=6)
    def IRegisteredTask_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegisteredTask.Invoke', argc=9)
    def IRegisteredTask_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegisteredTask.Run', argc=3)
    def IRegisteredTask_Run(self, emu, argv, ctx={}):
        """
        HRESULT Run(
            VARIANT params,
            IRunningTask **ppRunningTask
        );
        """
        ptr, params, ppRunningTask = argv
        # Simply return success - task "ran"
        return comdefs.S_OK

    # ====== ITaskFolder additional methods ======

    @apihook('ITaskFolder.Name', argc=2)
    def ITaskFolder_Name(self, emu, argv, ctx={}):
        """
        HRESULT get_Name(BSTR *pName);
        """
        ptr, pName = argv
        if pName:
            name = 'Root'.encode('utf-16le') + b'\x00\x00'
            buf = self.mem_alloc(len(name), tag='api.ITaskFolder.Name')
            self.mem_write(buf, name)
            self.mem_write(pName, buf.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.Path', argc=2)
    def ITaskFolder_Path(self, emu, argv, ctx={}):
        """
        HRESULT get_Path(BSTR *pPath);
        """
        ptr, pPath = argv
        if pPath:
            path = '\\'.encode('utf-16le') + b'\x00\x00'
            buf = self.mem_alloc(len(path), tag='api.ITaskFolder.Path')
            self.mem_write(buf, path)
            self.mem_write(pPath, buf.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.GetFolder', argc=3)
    def ITaskFolder_GetFolder(self, emu, argv, ctx={}):
        """
        HRESULT GetFolder(BSTR path, ITaskFolder **ppFolder);
        """
        ptr, path, ppFolder = argv
        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str

        if ppFolder:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskFolder')
            pFolder = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppFolder_ITaskFolder')
            self.mem_write(pFolder, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppFolder, pFolder.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.GetFolders', argc=3)
    def ITaskFolder_GetFolders(self, emu, argv, ctx={}):
        """
        HRESULT GetFolders(long flags, ITaskFolderCollection **ppFolders);
        """
        ptr, flags, ppFolders = argv
        if ppFolders:
            self.mem_write(ppFolders, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.DeleteFolder', argc=3)
    def ITaskFolder_DeleteFolder(self, emu, argv, ctx={}):
        """
        HRESULT DeleteFolder(BSTR subFolderName, long flags);
        """
        ptr, subFolderName, flags = argv
        if subFolderName:
            name_str = self.read_wide_string(subFolderName)
            argv[1] = name_str
        return comdefs.S_OK

    @apihook('ITaskFolder.GetTask', argc=3)
    def ITaskFolder_GetTask(self, emu, argv, ctx={}):
        """
        HRESULT GetTask(BSTR path, IRegisteredTask **ppTask);
        """
        ptr, path, ppTask = argv
        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str

        if ppTask:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IRegisteredTask')
            pTask = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppTask_IRegisteredTask')
            self.mem_write(pTask, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppTask, pTask.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.GetTasks', argc=3)
    def ITaskFolder_GetTasks(self, emu, argv, ctx={}):
        """
        HRESULT GetTasks(long flags, IRegisteredTaskCollection **ppTasks);
        """
        ptr, flags, ppTasks = argv
        if ppTasks:
            self.mem_write(ppTasks, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.GetSecurityDescriptor', argc=3)
    def ITaskFolder_GetSecurityDescriptor(self, emu, argv, ctx={}):
        """
        HRESULT GetSecurityDescriptor(long securityInformation, BSTR *pSddl);
        """
        ptr, securityInformation, pSddl = argv
        if pSddl:
            self.mem_write(pSddl, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskFolder.SetSecurityDescriptor', argc=3)
    def ITaskFolder_SetSecurityDescriptor(self, emu, argv, ctx={}):
        """
        HRESULT SetSecurityDescriptor(BSTR sddl, long flags);
        """
        return comdefs.S_OK

    # ====== ITaskDefinition methods ======

    @apihook('ITaskDefinition.RegistrationInfo', argc=2)
    def ITaskDefinition_RegistrationInfo(self, emu, argv, ctx={}):
        """HRESULT get_RegistrationInfo(IRegistrationInfo **ppRegistrationInfo);"""
        ptr, ppRegistrationInfo = argv
        if ppRegistrationInfo:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IRegistrationInfo')
            pRegInfo = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppRegistrationInfo')
            self.mem_write(pRegInfo, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppRegistrationInfo, pRegInfo.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK


    @apihook('ITaskDefinition.Triggers', argc=2)
    def ITaskDefinition_Triggers(self, emu, argv, ctx={}):
        """HRESULT get_Triggers(ITriggerCollection **ppTriggers);"""
        ptr, ppTriggers = argv
        if ppTriggers:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITriggerCollection')
            pTriggers = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppTriggers')
            self.mem_write(pTriggers, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppTriggers, pTriggers.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskDefinition.Settings', argc=2)
    def ITaskDefinition_Settings(self, emu, argv, ctx={}):
        """HRESULT get_Settings(ITaskSettings **ppSettings);"""
        ptr, ppSettings = argv
        if ppSettings:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskSettings')
            pSettings = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppSettings')
            self.mem_write(pSettings, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppSettings, pSettings.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskDefinition.Data', argc=2)
    def ITaskDefinition_Data(self, emu, argv, ctx={}):
        """HRESULT get_Data(BSTR *pData);"""
        ptr, pData = argv
        if pData:
            self.mem_write(pData, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskDefinition.Principal', argc=2)
    def ITaskDefinition_Principal(self, emu, argv, ctx={}):
        """HRESULT get_Principal(IPrincipal **ppPrincipal);"""
        ptr, ppPrincipal = argv
        if ppPrincipal:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IPrincipal')
            pPrincipal = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppPrincipal')
            self.mem_write(pPrincipal, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppPrincipal, pPrincipal.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskDefinition.Actions', argc=2)
    def ITaskDefinition_Actions(self, emu, argv, ctx={}):
        """HRESULT get_Actions(IActionCollection **ppActions);"""
        ptr, ppActions = argv
        if ppActions:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IActionCollection')
            pActions = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppActions')
            self.mem_write(pActions, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppActions, pActions.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('ITaskDefinition.XmlText', argc=2)
    def ITaskDefinition_XmlText(self, emu, argv, ctx={}):
        """HRESULT get_XmlText(BSTR *pXml);"""
        ptr, pXml = argv
        if pXml:
            self.mem_write(pXml, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    # ====== IRegisteredTask additional methods ======

    @apihook('IRegisteredTask.Name', argc=2)
    def IRegisteredTask_Name(self, emu, argv, ctx={}):
        """HRESULT get_Name(BSTR *pName);"""
        ptr, pName = argv
        if pName:
            name = 'Task'.encode('utf-16le') + b'\x00\x00'
            buf = self.mem_alloc(len(name), tag='api.IRegisteredTask.Name')
            self.mem_write(buf, name)
            self.mem_write(pName, buf.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.Path', argc=2)
    def IRegisteredTask_Path(self, emu, argv, ctx={}):
        """HRESULT get_Path(BSTR *pPath);"""
        ptr, pPath = argv
        if pPath:
            path = '\\Task'.encode('utf-16le') + b'\x00\x00'
            buf = self.mem_alloc(len(path), tag='api.IRegisteredTask.Path')
            self.mem_write(buf, path)
            self.mem_write(pPath, buf.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.State', argc=2)
    def IRegisteredTask_State(self, emu, argv, ctx={}):
        """HRESULT get_State(TASK_STATE *pState);"""
        ptr, pState = argv
        if pState:
            # TASK_STATE_READY = 3
            self.mem_write(pState, (3).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.Enabled', argc=2)
    def IRegisteredTask_Enabled(self, emu, argv, ctx={}):
        """HRESULT get_Enabled(VARIANT_BOOL *pEnabled);"""
        ptr, pEnabled = argv
        if pEnabled:
            # VARIANT_TRUE = -1
            self.mem_write(pEnabled, (0xFFFF).to_bytes(2, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.RunEx', argc=6)
    def IRegisteredTask_RunEx(self, emu, argv, ctx={}):
        """HRESULT RunEx(VARIANT params, long flags, long sessionStateChangeType, BSTR user, IRunningTask **ppRunningTask);"""
        return comdefs.S_OK

    @apihook('IRegisteredTask.GetInstances', argc=3)
    def IRegisteredTask_GetInstances(self, emu, argv, ctx={}):
        """HRESULT GetInstances(long flags, IRunningTaskCollection **ppRunningTasks);"""
        ptr, flags, ppRunningTasks = argv
        if ppRunningTasks:
            self.mem_write(ppRunningTasks, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.LastRunTime', argc=2)
    def IRegisteredTask_LastRunTime(self, emu, argv, ctx={}):
        """HRESULT get_LastRunTime(DATE *pLastRunTime);"""
        ptr, pLastRunTime = argv
        if pLastRunTime:
            self.mem_write(pLastRunTime, (0).to_bytes(8, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.LastTaskResult', argc=2)
    def IRegisteredTask_LastTaskResult(self, emu, argv, ctx={}):
        """HRESULT get_LastTaskResult(long *pLastTaskResult);"""
        ptr, pLastTaskResult = argv
        if pLastTaskResult:
            self.mem_write(pLastTaskResult, (0).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.NumberOfMissedRuns', argc=2)
    def IRegisteredTask_NumberOfMissedRuns(self, emu, argv, ctx={}):
        """HRESULT get_NumberOfMissedRuns(long *pNumberOfMissedRuns);"""
        ptr, pNumberOfMissedRuns = argv
        if pNumberOfMissedRuns:
            self.mem_write(pNumberOfMissedRuns, (0).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.NextRunTime', argc=2)
    def IRegisteredTask_NextRunTime(self, emu, argv, ctx={}):
        """HRESULT get_NextRunTime(DATE *pNextRunTime);"""
        ptr, pNextRunTime = argv
        if pNextRunTime:
            self.mem_write(pNextRunTime, (0).to_bytes(8, 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.Definition', argc=2)
    def IRegisteredTask_Definition(self, emu, argv, ctx={}):
        """HRESULT get_Definition(ITaskDefinition **ppDefinition);"""
        ptr, ppDefinition = argv
        if ppDefinition:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'ITaskDefinition')
            pDef = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppDefinition_ITaskDefinition')
            self.mem_write(pDef, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppDefinition, pDef.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.Xml', argc=2)
    def IRegisteredTask_Xml(self, emu, argv, ctx={}):
        """HRESULT get_Xml(BSTR *pXml);"""
        ptr, pXml = argv
        if pXml:
            self.mem_write(pXml, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.GetSecurityDescriptor', argc=3)
    def IRegisteredTask_GetSecurityDescriptor(self, emu, argv, ctx={}):
        """HRESULT GetSecurityDescriptor(long securityInformation, BSTR *pSddl);"""
        ptr, securityInformation, pSddl = argv
        if pSddl:
            self.mem_write(pSddl, (0).to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IRegisteredTask.SetSecurityDescriptor', argc=3)
    def IRegisteredTask_SetSecurityDescriptor(self, emu, argv, ctx={}):
        """HRESULT SetSecurityDescriptor(BSTR sddl, long flags);"""
        return comdefs.S_OK

    @apihook('IRegisteredTask.Stop', argc=2)
    def IRegisteredTask_Stop(self, emu, argv, ctx={}):
        """HRESULT Stop(long flags);"""
        return comdefs.S_OK

    @apihook('IRegisteredTask.GetRunTimes', argc=6)
    def IRegisteredTask_GetRunTimes(self, emu, argv, ctx={}):
        """HRESULT GetRunTimes(LPSYSTEMTIME pstStart, LPSYSTEMTIME pstEnd, DWORD *pCount, LPSYSTEMTIME *pRunTimes);"""
        return comdefs.S_OK

    # ====== IRegistrationInfo methods ======

    @apihook('IRegistrationInfo.QueryInterface', argc=3)
    def IRegistrationInfo_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegistrationInfo.AddRef', argc=1)
    def IRegistrationInfo_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('IRegistrationInfo.Release', argc=1)
    def IRegistrationInfo_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('IRegistrationInfo.GetTypeInfoCount', argc=2)
    def IRegistrationInfo_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegistrationInfo.GetTypeInfo', argc=4)
    def IRegistrationInfo_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegistrationInfo.GetIDsOfNames', argc=6)
    def IRegistrationInfo_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Invoke', argc=9)
    def IRegistrationInfo_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Description', argc=2)
    def IRegistrationInfo_Description(self, emu, argv, ctx={}):
        """HRESULT get/put_Description(BSTR *pDescription / BSTR description);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Author', argc=2)
    def IRegistrationInfo_Author(self, emu, argv, ctx={}):
        """HRESULT get/put_Author(BSTR *pAuthor / BSTR author);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Version', argc=2)
    def IRegistrationInfo_Version(self, emu, argv, ctx={}):
        """HRESULT get/put_Version(BSTR *pVersion / BSTR version);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Date', argc=2)
    def IRegistrationInfo_Date(self, emu, argv, ctx={}):
        """HRESULT get/put_Date(BSTR *pDate / BSTR date);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Documentation', argc=2)
    def IRegistrationInfo_Documentation(self, emu, argv, ctx={}):
        """HRESULT get/put_Documentation(BSTR *pDocumentation / BSTR documentation);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.XmlText', argc=2)
    def IRegistrationInfo_XmlText(self, emu, argv, ctx={}):
        """HRESULT get/put_XmlText(BSTR *pText / BSTR text);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.URI', argc=2)
    def IRegistrationInfo_URI(self, emu, argv, ctx={}):
        """HRESULT get/put_URI(BSTR *pUri / BSTR uri);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.SecurityDescriptor', argc=2)
    def IRegistrationInfo_SecurityDescriptor(self, emu, argv, ctx={}):
        """HRESULT get/put_SecurityDescriptor(VARIANT *pSddl / VARIANT sddl);"""
        return comdefs.S_OK

    @apihook('IRegistrationInfo.Source', argc=2)
    def IRegistrationInfo_Source(self, emu, argv, ctx={}):
        """HRESULT get/put_Source(BSTR *pSource / BSTR source);"""
        return comdefs.S_OK

    # ====== IPrincipal methods ======

    @apihook('IPrincipal.QueryInterface', argc=3)
    def IPrincipal_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.AddRef', argc=1)
    def IPrincipal_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('IPrincipal.Release', argc=1)
    def IPrincipal_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('IPrincipal.GetTypeInfoCount', argc=2)
    def IPrincipal_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.GetTypeInfo', argc=4)
    def IPrincipal_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.GetIDsOfNames', argc=6)
    def IPrincipal_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.Invoke', argc=9)
    def IPrincipal_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_Id', argc=2)
    def IPrincipal_get_Id(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_Id', argc=2)
    def IPrincipal_put_Id(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_DisplayName', argc=2)
    def IPrincipal_get_DisplayName(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_DisplayName', argc=2)
    def IPrincipal_put_DisplayName(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_UserId', argc=2)
    def IPrincipal_get_UserId(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_UserId', argc=2)
    def IPrincipal_put_UserId(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_LogonType', argc=2)
    def IPrincipal_get_LogonType(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_LogonType', argc=2)
    def IPrincipal_put_LogonType(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_GroupId', argc=2)
    def IPrincipal_get_GroupId(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_GroupId', argc=2)
    def IPrincipal_put_GroupId(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.get_RunLevel', argc=2)
    def IPrincipal_get_RunLevel(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.put_RunLevel', argc=2)
    def IPrincipal_put_RunLevel(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # Reserved methods for IPrincipal2 compatibility (offset 0x98-0xB8)
    @apihook('IPrincipal.Reserved1', argc=1)
    def IPrincipal_Reserved1(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.Reserved2', argc=1)
    def IPrincipal_Reserved2(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.Reserved3', argc=1)
    def IPrincipal_Reserved3(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.Reserved4', argc=1)
    def IPrincipal_Reserved4(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IPrincipal.Reserved5', argc=1)
    def IPrincipal_Reserved5(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== IActionCollection methods ======


    @apihook('IActionCollection.QueryInterface', argc=3)
    def IActionCollection_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.AddRef', argc=1)
    def IActionCollection_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('IActionCollection.Release', argc=1)
    def IActionCollection_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('IActionCollection.GetTypeInfoCount', argc=2)
    def IActionCollection_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.GetTypeInfo', argc=4)
    def IActionCollection_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.GetIDsOfNames', argc=6)
    def IActionCollection_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.Invoke', argc=9)
    def IActionCollection_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.Count', argc=2)
    def IActionCollection_Count(self, emu, argv, ctx={}):
        ptr, pCount = argv
        if pCount:
            self.mem_write(pCount, (0).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IActionCollection.Item', argc=3)
    def IActionCollection_Item(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection._NewEnum', argc=2)
    def IActionCollection__NewEnum(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.XmlText', argc=2)
    def IActionCollection_XmlText(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.Create', argc=3)
    def IActionCollection_Create(self, emu, argv, ctx={}):
        """
        HRESULT Create(TASK_ACTION_TYPE type, IAction **ppAction);
        type: 0=TASK_ACTION_EXEC, 5=TASK_ACTION_COM_HANDLER, etc.
        """
        ptr, actionType, ppAction = argv
        if ppAction:
            # Return IExecAction (most common)
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IExecAction')
            pAction = self.mem_alloc(emu.get_ptr_size(), tag='emu.COM.ppAction')
            self.mem_write(pAction, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
            self.mem_write(ppAction, pAction.to_bytes(emu.get_ptr_size(), 'little'))
        return comdefs.S_OK

    @apihook('IActionCollection.Remove', argc=2)
    def IActionCollection_Remove(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.Clear', argc=1)
    def IActionCollection_Clear(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IActionCollection.Context', argc=2)
    def IActionCollection_Context(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== ITriggerCollection methods ======

    @apihook('ITriggerCollection.QueryInterface', argc=3)
    def ITriggerCollection_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.AddRef', argc=1)
    def ITriggerCollection_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('ITriggerCollection.Release', argc=1)
    def ITriggerCollection_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('ITriggerCollection.GetTypeInfoCount', argc=2)
    def ITriggerCollection_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.GetTypeInfo', argc=4)
    def ITriggerCollection_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.GetIDsOfNames', argc=6)
    def ITriggerCollection_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.Invoke', argc=9)
    def ITriggerCollection_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.Count', argc=2)
    def ITriggerCollection_Count(self, emu, argv, ctx={}):
        ptr, pCount = argv
        if pCount:
            self.mem_write(pCount, (0).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('ITriggerCollection.Item', argc=3)
    def ITriggerCollection_Item(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection._NewEnum', argc=2)
    def ITriggerCollection__NewEnum(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.Create', argc=3)
    def ITriggerCollection_Create(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.Remove', argc=2)
    def ITriggerCollection_Remove(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITriggerCollection.Clear', argc=1)
    def ITriggerCollection_Clear(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== ITaskSettings methods ======

    @apihook('ITaskSettings.QueryInterface', argc=3)
    def ITaskSettings_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.AddRef', argc=1)
    def ITaskSettings_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('ITaskSettings.Release', argc=1)
    def ITaskSettings_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('ITaskSettings.GetTypeInfoCount', argc=2)
    def ITaskSettings_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.GetTypeInfo', argc=4)
    def ITaskSettings_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.GetIDsOfNames', argc=6)
    def ITaskSettings_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.Invoke', argc=9)
    def ITaskSettings_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ITaskSettings properties - all get/put separated
    @apihook('ITaskSettings.get_AllowDemandStart', argc=2)
    def ITaskSettings_get_AllowDemandStart(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_AllowDemandStart', argc=2)
    def ITaskSettings_put_AllowDemandStart(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_RestartInterval', argc=2)
    def ITaskSettings_get_RestartInterval(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_RestartInterval', argc=2)
    def ITaskSettings_put_RestartInterval(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_RestartCount', argc=2)
    def ITaskSettings_get_RestartCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_RestartCount', argc=2)
    def ITaskSettings_put_RestartCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_MultipleInstances', argc=2)
    def ITaskSettings_get_MultipleInstances(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_MultipleInstances', argc=2)
    def ITaskSettings_put_MultipleInstances(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_StopIfGoingOnBatteries', argc=2)
    def ITaskSettings_get_StopIfGoingOnBatteries(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_StopIfGoingOnBatteries', argc=2)
    def ITaskSettings_put_StopIfGoingOnBatteries(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_DisallowStartOnBatteries', argc=2)
    def ITaskSettings_get_DisallowStartOnBatteries(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_DisallowStartOnBatteries', argc=2)
    def ITaskSettings_put_DisallowStartOnBatteries(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_AllowHardTerminate', argc=2)
    def ITaskSettings_get_AllowHardTerminate(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_AllowHardTerminate', argc=2)
    def ITaskSettings_put_AllowHardTerminate(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_StartWhenAvailable', argc=2)
    def ITaskSettings_get_StartWhenAvailable(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_StartWhenAvailable', argc=2)
    def ITaskSettings_put_StartWhenAvailable(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_XmlText', argc=2)
    def ITaskSettings_get_XmlText(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_XmlText', argc=2)
    def ITaskSettings_put_XmlText(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_RunOnlyIfNetworkAvailable', argc=2)
    def ITaskSettings_get_RunOnlyIfNetworkAvailable(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_RunOnlyIfNetworkAvailable', argc=2)
    def ITaskSettings_put_RunOnlyIfNetworkAvailable(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_ExecutionTimeLimit', argc=2)
    def ITaskSettings_get_ExecutionTimeLimit(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_ExecutionTimeLimit', argc=2)
    def ITaskSettings_put_ExecutionTimeLimit(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_Enabled', argc=2)
    def ITaskSettings_get_Enabled(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_Enabled', argc=2)
    def ITaskSettings_put_Enabled(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_DeleteExpiredTaskAfter', argc=2)
    def ITaskSettings_get_DeleteExpiredTaskAfter(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_DeleteExpiredTaskAfter', argc=2)
    def ITaskSettings_put_DeleteExpiredTaskAfter(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_Priority', argc=2)
    def ITaskSettings_get_Priority(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_Priority', argc=2)
    def ITaskSettings_put_Priority(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_Compatibility', argc=2)
    def ITaskSettings_get_Compatibility(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_Compatibility', argc=2)
    def ITaskSettings_put_Compatibility(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_Hidden', argc=2)
    def ITaskSettings_get_Hidden(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_Hidden', argc=2)
    def ITaskSettings_put_Hidden(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_IdleSettings', argc=2)
    def ITaskSettings_get_IdleSettings(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_IdleSettings', argc=2)
    def ITaskSettings_put_IdleSettings(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_RunOnlyIfIdle', argc=2)
    def ITaskSettings_get_RunOnlyIfIdle(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_RunOnlyIfIdle', argc=2)
    def ITaskSettings_put_RunOnlyIfIdle(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_WakeToRun', argc=2)
    def ITaskSettings_get_WakeToRun(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_WakeToRun', argc=2)
    def ITaskSettings_put_WakeToRun(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.get_NetworkSettings', argc=2)
    def ITaskSettings_get_NetworkSettings(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('ITaskSettings.put_NetworkSettings', argc=2)
    def ITaskSettings_put_NetworkSettings(self, emu, argv, ctx={}):
        return comdefs.S_OK

    # ====== IExecAction methods ======

    @apihook('IExecAction.QueryInterface', argc=3)
    def IExecAction_QueryInterface(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.AddRef', argc=1)
    def IExecAction_AddRef(self, emu, argv, ctx={}):
        return 1

    @apihook('IExecAction.Release', argc=1)
    def IExecAction_Release(self, emu, argv, ctx={}):
        return 0

    @apihook('IExecAction.GetTypeInfoCount', argc=2)
    def IExecAction_GetTypeInfoCount(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.GetTypeInfo', argc=4)
    def IExecAction_GetTypeInfo(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.GetIDsOfNames', argc=6)
    def IExecAction_GetIDsOfNames(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.Invoke', argc=9)
    def IExecAction_Invoke(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.get_Id', argc=2)
    def IExecAction_get_Id(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.put_Id', argc=2)
    def IExecAction_put_Id(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.get_Type', argc=2)
    def IExecAction_get_Type(self, emu, argv, ctx={}):
        ptr, pType = argv
        if pType:
            # TASK_ACTION_EXEC = 0
            self.mem_write(pType, (0).to_bytes(4, 'little'))
        return comdefs.S_OK

    @apihook('IExecAction.get_Path', argc=2)
    def IExecAction_get_Path(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.put_Path', argc=2)
    def IExecAction_put_Path(self, emu, argv, ctx={}):
        ptr, path = argv
        if path:
            path_str = self.read_wide_string(path)
            argv[1] = path_str
            if self.emu.logger:
                self.emu.logger.info('IExecAction::put_Path - %s', path_str)
        return comdefs.S_OK

    @apihook('IExecAction.get_Arguments', argc=2)
    def IExecAction_get_Arguments(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.put_Arguments', argc=2)
    def IExecAction_put_Arguments(self, emu, argv, ctx={}):
        ptr, args = argv
        if args:
            args_str = self.read_wide_string(args)
            argv[1] = args_str
            if self.emu.logger:
                self.emu.logger.info('IExecAction::put_Arguments - %s', args_str)
        return comdefs.S_OK

    @apihook('IExecAction.get_WorkingDirectory', argc=2)
    def IExecAction_get_WorkingDirectory(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.put_WorkingDirectory', argc=2)
    def IExecAction_put_WorkingDirectory(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.Reserved1', argc=1)
    def IExecAction_Reserved1(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.Reserved2', argc=1)
    def IExecAction_Reserved2(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.Reserved3', argc=1)
    def IExecAction_Reserved3(self, emu, argv, ctx={}):
        return comdefs.S_OK

    @apihook('IExecAction.Reserved4', argc=1)
    def IExecAction_Reserved4(self, emu, argv, ctx={}):
        return comdefs.S_OK
