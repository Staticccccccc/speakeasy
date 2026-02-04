# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import uuid

from speakeasy.struct import EmuStruct, Ptr

S_OK = 0

RPC_C_AUTHN_LEVEL_DEFAULT = 0
RPC_C_AUTHN_LEVEL_NONE = 1
RPC_C_AUTHN_LEVEL_CONNECT = 2
RPC_C_AUTHN_LEVEL_CALL = 3
RPC_C_AUTHN_LEVEL_PKT = 4
RPC_C_AUTHN_LEVEL_PKT_INTEGRITY = 5
RPC_C_AUTHN_LEVEL_PKT_PRIVACY = 6

RPC_C_IMP_LEVEL_DEFAULT = 0
RPC_C_IMP_LEVEL_ANONYMOUS = 1
RPC_C_IMP_LEVEL_IDENTIFY = 2
RPC_C_IMP_LEVEL_IMPERSONATE = 3
RPC_C_IMP_LEVEL_DELEGATE = 4

CLSID_WbemLocator = '{4590F811-1D3A-11D0-891F-00AA004B2E24}'
CLSID_IWbemContext = '{674B6698-EE92-11D0-AD71-00C04FD8FDFF}'

IID_IWbemLocator = '{DC12A687-737F-11CF-884D-00AA004B2E24}'
IID_IWbemContext = '{44ACA674-E8FC-11D0-A07C-00C04FB68820}'

CLSID_WinHttpRequest = '{2087C2F4-2CEF-4953-A8AB-34A51C4DAEEB}'
IID_IWinHttpRequest = '{016FE2EC-B2C8-45F8-B23B-39E53A75396B}'

# Task Scheduler COM
CLSID_TaskScheduler = '{0F87369F-A4E5-4CFC-BD3E-73E6154572DD}'
IID_ITaskService = '{2FABA4C7-4DA9-4013-9697-20CC3FD40F85}'
IID_ITaskFolder = '{8CFAC062-A080-4C15-9A88-AA7C2AF80DFC}'
IID_IRegisteredTask = '{9C86F320-DEE3-4DD1-B972-A303F26B061E}'
IID_ITaskDefinition = '{F5BC8FC5-536D-4F77-B852-FBC1356FDEB6}'

CLSID_MMDeviceEnumerator = '{BCDE0395-E52F-467C-8E3D-C4579291692E}'
IID_IMMDeviceEnumerator = '{A95664D2-9614-4F35-A746-DE8DB63617E6}'

class ComInterface(object):
    def __init__(self, iface, name, ptr_size):
        self.iface = iface(ptr_size)
        self.address = 0
        self.name = name


class IUnknown(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr


class IDispatch(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr


class IMalloc(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.Alloc = Ptr
        self.Realloc = Ptr
        self.Free = Ptr
        self.GetSize = Ptr
        self.DidAlloc = Ptr
        self.HeapMinimize = Ptr


class IWbemLocator(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.ConnectServer = Ptr


class IWbemServices(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.OpenNamespace = Ptr
        self.CancelAsyncCall = Ptr
        self.QueryObjectSink = Ptr
        self.GetObject = Ptr
        self.GetObjectAsync = Ptr
        self.PutClass = Ptr
        self.PutClassAsync = Ptr
        self.DeleteClass = Ptr
        self.DeleteClassAsync = Ptr
        self.CreateClassEnum = Ptr
        self.CreateClassEnumAsync = Ptr
        self.PutInstance = Ptr
        self.PutInstanceAsync = Ptr
        self.DeleteInstance = Ptr
        self.DeleteInstanceAsync = Ptr
        self.CreateInstanceEnum = Ptr
        self.CreateInstanceEnumAsync = Ptr
        self.ExecQuery = Ptr
        self.ExecQueryAsync = Ptr
        self.ExecNotificationQuery = Ptr
        self.ExecNotificationQueryAsync = Ptr
        self.ExecMethod = Ptr
        self.ExecMethodAsync = Ptr


class IWbemContext(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.Clone = Ptr
        self.GetNames = Ptr
        self.BeginEnumeration = Ptr
        self.Next = Ptr
        self.EndEnumeration = Ptr
        self.SetValue = Ptr
        self.GetValue = Ptr
        self.DeleteValue = Ptr
        self.DeleteAll = Ptr


class IWinHttpRequest(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.SetProxy = Ptr
        self.SetCredentials = Ptr
        self.Open = Ptr
        self.SetRequestHeader = Ptr
        self.GetResponseHeader = Ptr
        self.GetAllResponseHeaders = Ptr
        self.Send = Ptr
        self.WaitForResponse = Ptr
        self.Abort = Ptr
        self.SetTimeouts = Ptr
        self.SetClientCertificate = Ptr
        self.SetAutoLogonPolicy = Ptr
        self.Status = Ptr
        self.StatusText = Ptr
        self.ResponseText = Ptr
        self.ResponseBody = Ptr
        self.ResponseStream = Ptr
        self.Option = Ptr


class ITaskService(EmuStruct):
    """
    ITaskService vtable - flattened to avoid nesting issues.
    Inherits from: IDispatch -> IUnknown
    Total: 7 (IDispatch) + 9 (ITaskService) = 16 methods
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown methods (indices 0-2, offsets 0x00-0x10)
        self.QueryInterface = Ptr       # [0] offset 0x00
        self.AddRef = Ptr               # [1] offset 0x08
        self.Release = Ptr              # [2] offset 0x10
        # IDispatch methods (indices 3-6, offsets 0x18-0x30)
        self.GetTypeInfoCount = Ptr     # [3] offset 0x18
        self.GetTypeInfo = Ptr          # [4] offset 0x20
        self.GetIDsOfNames = Ptr        # [5] offset 0x28
        self.Invoke = Ptr               # [6] offset 0x30
        # ITaskService methods (indices 7-15, offsets 0x38-0x78)
        self.GetFolder = Ptr            # [7] offset 0x38
        self.GetRunningTasks = Ptr      # [8] offset 0x40
        self.NewTask = Ptr              # [9] offset 0x48
        self.Connect = Ptr              # [10] offset 0x50
        self.Connected = Ptr            # [11] offset 0x58
        self.TargetServer = Ptr         # [12] offset 0x60
        self.ConnectedUser = Ptr        # [13] offset 0x68
        self.ConnectedDomain = Ptr      # [14] offset 0x70
        self.HighestVersion = Ptr       # [15] offset 0x78


class ITaskFolder(EmuStruct):
    """
    ITaskFolder vtable - flattened.
    Inherits from: IDispatch -> IUnknown
    Total: 7 (IDispatch) + 13 (ITaskFolder) = 20 methods
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown methods (indices 0-2)
        self.QueryInterface = Ptr       # [0] offset 0x00
        self.AddRef = Ptr               # [1] offset 0x08
        self.Release = Ptr              # [2] offset 0x10
        # IDispatch methods (indices 3-6)
        self.GetTypeInfoCount = Ptr     # [3] offset 0x18
        self.GetTypeInfo = Ptr          # [4] offset 0x20
        self.GetIDsOfNames = Ptr        # [5] offset 0x28
        self.Invoke = Ptr               # [6] offset 0x30
        # ITaskFolder methods (indices 7-19)
        self.Name = Ptr                 # [7] offset 0x38
        self.Path = Ptr                 # [8] offset 0x40
        self.GetFolder = Ptr            # [9] offset 0x48
        self.GetFolders = Ptr           # [10] offset 0x50
        self.CreateFolder = Ptr         # [11] offset 0x58
        self.DeleteFolder = Ptr         # [12] offset 0x60
        self.GetTask = Ptr              # [13] offset 0x68
        self.GetTasks = Ptr             # [14] offset 0x70
        self.DeleteTask = Ptr           # [15] offset 0x78
        self.RegisterTask = Ptr         # [16] offset 0x80
        self.RegisterTaskDefinition = Ptr  # [17] offset 0x88
        self.GetSecurityDescriptor = Ptr   # [18] offset 0x90
        self.SetSecurityDescriptor = Ptr   # [19] offset 0x98


class ITaskDefinition(EmuStruct):
    """
    ITaskDefinition vtable - flattened.
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # ITaskDefinition methods (indices 7+)
        self.RegistrationInfo = Ptr     # [7]
        self.Triggers = Ptr             # [8]
        self.Settings = Ptr             # [9]
        self.Data = Ptr                 # [10]
        self.Principal = Ptr            # [11]
        self.Actions = Ptr              # [12]
        self.XmlText = Ptr              # [13]


class IRegisteredTask(EmuStruct):
    """
    IRegisteredTask vtable - flattened.
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # IRegisteredTask methods (indices 7+)
        self.Name = Ptr                 # [7]
        self.Path = Ptr                 # [8]
        self.State = Ptr                # [9]
        self.Enabled = Ptr              # [10]
        self.Run = Ptr                  # [11]
        self.RunEx = Ptr                # [12]
        self.GetInstances = Ptr         # [13]
        self.LastRunTime = Ptr          # [14]
        self.LastTaskResult = Ptr       # [15]
        self.NumberOfMissedRuns = Ptr   # [16]
        self.NextRunTime = Ptr          # [17]
        self.Definition = Ptr           # [18]
        self.Xml = Ptr                  # [19]
        self.GetSecurityDescriptor = Ptr  # [20]
        self.SetSecurityDescriptor = Ptr  # [21]
        self.Stop = Ptr                 # [22]
        self.GetRunTimes = Ptr          # [23]


class IRegistrationInfo(EmuStruct):
    """
    IRegistrationInfo vtable - flattened.
    Used by ITaskDefinition.RegistrationInfo
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # IRegistrationInfo properties (indices 7+)
        self.Description = Ptr          # get/put_Description
        self.Author = Ptr               # get/put_Author
        self.Version = Ptr              # get/put_Version
        self.Date = Ptr                 # get/put_Date
        self.Documentation = Ptr        # get/put_Documentation
        self.XmlText = Ptr              # get/put_XmlText
        self.URI = Ptr                  # get/put_URI
        self.SecurityDescriptor = Ptr   # get/put_SecurityDescriptor
        self.Source = Ptr               # get/put_Source


class IPrincipal(EmuStruct):
    """
    IPrincipal vtable - flattened with get/put separated.
    Offset 0xB0 = index 22 is being called, so we need enough methods.
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr       # [0] 0x00
        self.AddRef = Ptr               # [1] 0x08
        self.Release = Ptr              # [2] 0x10
        self.GetTypeInfoCount = Ptr     # [3] 0x18
        self.GetTypeInfo = Ptr          # [4] 0x20
        self.GetIDsOfNames = Ptr        # [5] 0x28
        self.Invoke = Ptr               # [6] 0x30
        # IPrincipal properties - get/put separated (indices 7+)
        self.get_Id = Ptr               # [7] 0x38
        self.put_Id = Ptr               # [8] 0x40
        self.get_DisplayName = Ptr      # [9] 0x48
        self.put_DisplayName = Ptr      # [10] 0x50
        self.get_UserId = Ptr           # [11] 0x58
        self.put_UserId = Ptr           # [12] 0x60
        self.get_LogonType = Ptr        # [13] 0x68
        self.put_LogonType = Ptr        # [14] 0x70
        self.get_GroupId = Ptr          # [15] 0x78
        self.put_GroupId = Ptr          # [16] 0x80
        self.get_RunLevel = Ptr         # [17] 0x88
        self.put_RunLevel = Ptr         # [18] 0x90
        # Additional padding for potential IPrincipal2 methods
        self.Reserved1 = Ptr            # [19] 0x98
        self.Reserved2 = Ptr            # [20] 0xA0
        self.Reserved3 = Ptr            # [21] 0xA8
        self.Reserved4 = Ptr            # [22] 0xB0
        self.Reserved5 = Ptr            # [23] 0xB8


class IActionCollection(EmuStruct):
    """IActionCollection vtable - flattened."""
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # IActionCollection properties/methods (indices 7+)
        self.Count = Ptr
        self.Item = Ptr
        self._NewEnum = Ptr
        self.XmlText = Ptr
        self.Create = Ptr
        self.Remove = Ptr
        self.Clear = Ptr
        self.Context = Ptr


class ITriggerCollection(EmuStruct):
    """ITriggerCollection vtable - flattened."""
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # ITriggerCollection properties/methods (indices 7+)
        self.Count = Ptr
        self.Item = Ptr
        self._NewEnum = Ptr
        self.Create = Ptr
        self.Remove = Ptr
        self.Clear = Ptr


class ITaskSettings(EmuStruct):
    """
    ITaskSettings vtable - flattened with get/put separated.
    Many properties, need get/put for each to match real vtable.
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr       # [0] 0x00
        self.AddRef = Ptr               # [1] 0x08
        self.Release = Ptr              # [2] 0x10
        self.GetTypeInfoCount = Ptr     # [3] 0x18
        self.GetTypeInfo = Ptr          # [4] 0x20
        self.GetIDsOfNames = Ptr        # [5] 0x28
        self.Invoke = Ptr               # [6] 0x30
        # ITaskSettings properties - get/put separated (indices 7+)
        self.get_AllowDemandStart = Ptr        # [7] 0x38
        self.put_AllowDemandStart = Ptr        # [8] 0x40
        self.get_RestartInterval = Ptr         # [9] 0x48
        self.put_RestartInterval = Ptr         # [10] 0x50
        self.get_RestartCount = Ptr            # [11] 0x58
        self.put_RestartCount = Ptr            # [12] 0x60
        self.get_MultipleInstances = Ptr       # [13] 0x68
        self.put_MultipleInstances = Ptr       # [14] 0x70
        self.get_StopIfGoingOnBatteries = Ptr  # [15] 0x78
        self.put_StopIfGoingOnBatteries = Ptr  # [16] 0x80
        self.get_DisallowStartOnBatteries = Ptr  # [17] 0x88
        self.put_DisallowStartOnBatteries = Ptr  # [18] 0x90
        self.get_AllowHardTerminate = Ptr      # [19] 0x98
        self.put_AllowHardTerminate = Ptr      # [20] 0xA0
        self.get_StartWhenAvailable = Ptr      # [21] 0xA8
        self.put_StartWhenAvailable = Ptr      # [22] 0xB0
        self.get_XmlText = Ptr                 # [23] 0xB8
        self.put_XmlText = Ptr                 # [24] 0xC0
        self.get_RunOnlyIfNetworkAvailable = Ptr  # [25] 0xC8
        self.put_RunOnlyIfNetworkAvailable = Ptr  # [26] 0xD0
        self.get_ExecutionTimeLimit = Ptr      # [27] 0xD8
        self.put_ExecutionTimeLimit = Ptr      # [28] 0xE0
        self.get_Enabled = Ptr                 # [29] 0xE8
        self.put_Enabled = Ptr                 # [30] 0xF0
        self.get_DeleteExpiredTaskAfter = Ptr  # [31] 0xF8
        self.put_DeleteExpiredTaskAfter = Ptr  # [32] 0x100
        self.get_Priority = Ptr                # [33] 0x108
        self.put_Priority = Ptr                # [34] 0x110
        self.get_Compatibility = Ptr           # [35] 0x118
        self.put_Compatibility = Ptr           # [36] 0x120
        self.get_Hidden = Ptr                  # [37] 0x128
        self.put_Hidden = Ptr                  # [38] 0x130
        self.get_IdleSettings = Ptr            # [39] 0x138
        self.put_IdleSettings = Ptr            # [40] 0x140
        self.get_RunOnlyIfIdle = Ptr           # [41] 0x148
        self.put_RunOnlyIfIdle = Ptr           # [42] 0x150
        self.get_WakeToRun = Ptr               # [43] 0x158
        self.put_WakeToRun = Ptr               # [44] 0x160
        self.get_NetworkSettings = Ptr         # [45] 0x168
        self.put_NetworkSettings = Ptr         # [46] 0x170


class IExecAction(EmuStruct):
    """
    IExecAction vtable - flattened.
    Inherits from IAction. Returned by IActionCollection.Create(TASK_ACTION_EXEC).
    """
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        # IUnknown + IDispatch (indices 0-6)
        self.QueryInterface = Ptr
        self.AddRef = Ptr
        self.Release = Ptr
        self.GetTypeInfoCount = Ptr
        self.GetTypeInfo = Ptr
        self.GetIDsOfNames = Ptr
        self.Invoke = Ptr
        # IAction properties (indices 7-8)
        self.get_Id = Ptr               # [7]
        self.put_Id = Ptr               # [8]
        self.get_Type = Ptr             # [9]
        # IExecAction properties (indices 10+)
        self.get_Path = Ptr             # [10]
        self.put_Path = Ptr             # [11]
        self.get_Arguments = Ptr        # [12]
        self.put_Arguments = Ptr        # [13]
        self.get_WorkingDirectory = Ptr # [14]
        self.put_WorkingDirectory = Ptr # [15]
        # Additional padding
        self.Reserved1 = Ptr            # [16]
        self.Reserved2 = Ptr            # [17]
        self.Reserved3 = Ptr            # [18]
        self.Reserved4 = Ptr            # [19]


class IMMDeviceEnumerator(EmuStruct):
    def __init__(self, ptr_size):
        super().__init__(ptr_size)
        self.IUnknown = IUnknown
        self.EnumAudioEndpoints = Ptr
        self.GetDefaultAudioEndpoint = Ptr
        self.GetDevice = Ptr
        self.RegisterEndpointNotificationCallback = Ptr
        self.UnregisterEndpointNotificationCallback = Ptr


IFACE_TYPES = {'IUnknown': IUnknown,
               'IDispatch': IDispatch,
               'IMalloc':  IMalloc,
               'IWbemLocator': IWbemLocator,
               'IWbemServices': IWbemServices,
               'IWbemContext': IWbemContext,
               'IWinHttpRequest': IWinHttpRequest,
               'ITaskService': ITaskService,
               'ITaskFolder': ITaskFolder,
               'ITaskDefinition': ITaskDefinition,
               'IRegisteredTask': IRegisteredTask,
               'IRegistrationInfo': IRegistrationInfo,
               'IPrincipal': IPrincipal,
               'IActionCollection': IActionCollection,
               'ITriggerCollection': ITriggerCollection,
               'ITaskSettings': ITaskSettings,
               'IExecAction': IExecAction,
               'IMMDeviceEnumerator': IMMDeviceEnumerator}



def get_define_int(define, prefix=''):
    for k, v in globals().items():
        if not isinstance(v, int) or v != define:
            continue
        if prefix:
            if k.startswith(prefix):
                return k
        else:
            return k


def get_define_str(define, prefix=''):
    for k, v in globals().items():
        if not isinstance(v, str) or v != define:
            continue
        if prefix:
            if k.startswith(prefix):
                return k
        else:
            return k


def get_clsid(define):
    return get_define_str(define, prefix='CLSID_')


def get_iid(define):
    return get_define_str(define, prefix='IID_')


def get_rpc_authlevel(define):
    return get_define_int(define, prefix='RPC_C_AUTHN_LEVEL_')


def get_rcp_implevel(define):
    return get_define_int(define, prefix='RPC_C_IMP_LEVEL_')


def convert_guid_bytes_to_str(guid_bytes):
    u = uuid.UUID(bytes_le=guid_bytes)
    return ('{%s}' % u).upper()
