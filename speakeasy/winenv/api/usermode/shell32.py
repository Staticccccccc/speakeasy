# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.
from speakeasy.const import PROC_CREATE
from .. import api
import shlex
import speakeasy.winenv.defs.windows.windows as windefs
import speakeasy.winenv.defs.windows.shell32 as shell32_defs


class Shell32(api.ApiHandler):

    """
    Implements exported functions from shell32.dll
    """

    name = 'shell32'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(Shell32, self).__init__(emu)

        self.funcs = {}
        self.data = {}
        self.window_hooks = {}
        self.handle = 0
        self.win = None
        self.curr_handle = 0x2800

        super(Shell32, self).__get_hook_attrs__(self)

    def get_handle(self):
        self.curr_handle += 4
        return self.curr_handle

    @apihook('SHCreateDirectoryEx', argc=3)
    def SHCreateDirectoryEx(self, emu, argv, ctx={}):
        '''
        int SHCreateDirectoryExA(
            HWND                      hwnd,
            LPCSTR                    pszPath,
            const SECURITY_ATTRIBUTES *psa
        );
        '''

        hwnd, pszPath, psa = argv

        cw = self.get_char_width(ctx)
        dn = ''
        if pszPath:
            dn = self.read_mem_string(pszPath, cw)
            argv[1] = dn

            self.log_file_access(dn, 'directory_create')

        return 0

    @apihook('SHCreateDirectoryExW', argc=3)
    def SHCreateDirectoryExW(self, emu, argv, ctx={}):
        '''
        int SHCreateDirectoryExW(
            HWND                      hwnd,
            LPCWSTR                    pszPath,
            const SECURITY_ATTRIBUTES *psa
        );
        '''

        hwnd, pszPath, psa = argv

        cw = 2
        dn = ''
        if pszPath:
            dn = self.read_mem_string(pszPath, cw)
            argv[1] = dn

            self.log_file_access(dn, 'directory_create')

        return 0

    @apihook('ShellExecute', argc=6)
    def ShellExecute(self, emu, argv, ctx={}):
        '''
        HINSTANCE ShellExecuteA(
            HWND   hwnd,
            LPCSTR lpOperation,
            LPCSTR lpFile,
            LPCSTR lpParameters,
            LPCSTR lpDirectory,
            INT    nShowCmd
        );
        '''

        hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd = argv

        cw = self.get_char_width(ctx)

        fn = ''
        param = ''
        dn = ''
        if lpOperation:
            op = self.read_mem_string(lpOperation, cw)
            argv[1] = op
        if lpFile:
            fn = self.read_mem_string(lpFile, cw)
            argv[2] = fn
        if lpParameters:
            param = self.read_mem_string(lpParameters, cw)
            argv[3] = param
        if lpDirectory:
            dn = self.read_mem_string(lpDirectory, cw)
            argv[4] = dn

        if dn and fn:
            fn = '%s\\%s' % (dn, fn)

        proc = emu.create_process(path=fn, cmdline=param)
        self.log_process_event(proc, PROC_CREATE)

        return 33

    @apihook('ShellExecuteW', argc=6)
    def ShellExecuteW(self, emu, argv, ctx={}):
        '''
        HINSTANCE ShellExecuteW(
            HWND   hwnd,
            LPCWSTR lpOperation,
            LPCWSTR lpFile,
            LPCWSTR lpParameters,
            LPCWSTR lpDirectory,
            INT    nShowCmd
        );
        '''

        hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd = argv

        cw = 2

        fn = ''
        param = ''
        dn = ''
        if lpOperation:
            op = self.read_mem_string(lpOperation, cw)
            argv[1] = op
        if lpFile:
            fn = self.read_mem_string(lpFile, cw)
            argv[2] = fn
        if lpParameters:
            param = self.read_mem_string(lpParameters, cw)
            argv[3] = param
        if lpDirectory:
            dn = self.read_mem_string(lpDirectory, cw)
            argv[4] = dn

        if dn and fn:
            fn = '%s\\%s' % (dn, fn)

        proc = emu.create_process(path=fn, cmdline=param)
        self.log_process_event(proc, PROC_CREATE)

        return 33

    @apihook('ShellExecuteEx', argc=1)
    def ShellExecuteEx(self, emu, argv, ctx={}):
        '''
        BOOL ShellExecuteExA(
            [in, out] SHELLEXECUTEINFOA *pExecInfo
        );
        '''
        lpShellExecuteInfo, = argv

        sei = shell32_defs.SHELLEXECUTEINFOA(emu.get_ptr_size())
        sei_struct = self.mem_cast(sei, lpShellExecuteInfo)

        self.ShellExecute(
            emu,
            [
                0,
                sei_struct.lpVerb,
                sei_struct.lpFile,
                sei_struct.lpParameters, sei_struct.lpDirectory,
                0
            ],
            ctx
        )

        return True

    @apihook('ShellExecuteExW', argc=1)
    def ShellExecuteExW(self, emu, argv, ctx={}):
        '''
        BOOL ShellExecuteExW(
            [in, out] SHELLEXECUTEINFOW *pExecInfo
        );
        '''
        lpShellExecuteInfo, = argv

        sei = shell32_defs.SHELLEXECUTEINFOA(emu.get_ptr_size())
        sei_struct = self.mem_cast(sei, lpShellExecuteInfo)

        self.ShellExecuteW(
            emu,
            [
                0,
                sei_struct.lpVerb,
                sei_struct.lpFile,
                sei_struct.lpParameters, sei_struct.lpDirectory,
                0
            ],
            ctx
        )

        return True

    @apihook('IsUserAnAdmin', argc=0, ordinal=680)
    def IsUserAnAdmin(self, emu, argv, ctx={}):
        """
        BOOL IsUserAnAdmin();
        """
        return emu.get_user().get('is_admin', False)

    @apihook('SHGetMalloc', argc=1)
    def SHGetMalloc(self, emu, argv, ctx={}):
        """
        SHSTDAPI SHGetMalloc(
            IMalloc **ppMalloc
        );
        """
        ppMalloc, = argv

        if ppMalloc:
            ci = emu.com.get_interface(emu, emu.get_ptr_size(), 'IMalloc')
            self.mem_write(ppMalloc, ci.address.to_bytes(emu.get_ptr_size(), 'little'))
        rv = windefs.S_OK
        return rv

    @apihook('CommandLineToArgv', argc=2)
    def CommandLineToArgv(self, emu, argv, ctx={}):
        """
        LPWSTR * CommandLineToArgv(
            LPCWSTR lpCmdLine,
            int     *pNumArgs
        );
        """
        cmdline, argc = argv

        cw = self.get_char_width(ctx)
        cl = self.read_mem_string(cmdline, cw)

        ptrsize = emu.get_ptr_size()

        split = shlex.split(cl)
        nargs = len(split)

        # Get the total size we need
        size = (len(split) + 1) * ptrsize
        size += (len(cl) * cw) + (len(split) * cw)

        # Allocate the array
        buf = self.mem_alloc(size, tag='api.CommandLineToArgv')
        ptrs = buf
        strs = buf + ((len(split) + 1) * ptrsize)
        for i, p in enumerate(split):
            self.mem_write(ptrs + (i * ptrsize), strs.to_bytes(emu.get_ptr_size(), 'little'))

            p += '\x00'
            if cw == 2:
                s = p.encode('utf-16le')
            else:
                s = p.encode('utf-8')
            self.mem_write(strs, s)

            strs += len(s)

        if argc:
            self.mem_write(argc, nargs.to_bytes(4, "little"))

        return buf

    @apihook('CommandLineToArgvW', argc=2)
    def CommandLineToArgvW(self, emu, argv, ctx={}):
        """
        LPWSTR * CommandLineToArgvW(
            LPCWSTR lpCmdLine,
            int     *pNumArgs
        );
        """
        cmdline, argc = argv

        cw = 2
        cl = self.read_mem_string(cmdline, cw)

        ptrsize = emu.get_ptr_size()

        split = shlex.split(cl)
        nargs = len(split)

        # Get the total size we need
        size = (len(split) + 1) * ptrsize
        size += (len(cl) * cw) + (len(split) * cw)

        # Allocate the array
        buf = self.mem_alloc(size, tag='api.CommandLineToArgvW')
        ptrs = buf
        strs = buf + ((len(split) + 1) * ptrsize)
        for i, p in enumerate(split):
            self.mem_write(ptrs + (i * ptrsize), strs.to_bytes(emu.get_ptr_size(), 'little'))

            p += '\x00'
            s = p.encode('utf-16le')
            self.mem_write(strs, s)

            strs += len(s)

        if argc:
            self.mem_write(argc, nargs.to_bytes(4, "little"))

        return buf

    @apihook('ExtractIcon', argc=3)
    def ExtractIcon(self, emu, argv, ctx={}):
        """
        HICON ExtractIconA(
          HINSTANCE hInst,
          LPCSTR    pszExeFileName,
          UINT      nIconIndex
        );
        """

        return self.get_handle()

    @apihook('ExtractIconW', argc=3)
    def ExtractIconW(self, emu, argv, ctx={}):
        """
        HICON ExtractIconW(
          HINSTANCE hInst,
          LPCWSTR    pszExeFileName,
          UINT      nIconIndex
        );
        """

        return self.get_handle()

    @apihook('SHGetFolderPath', argc=5)
    def SHGetFolderPath(self, emu, argv, ctx={}):
        """
        HWND   hwnd,
        int    csidl,
        HANDLE hToken,
        DWORD  dwFlags,
        LPWSTR pszPath
        """
        hwnd, csidl, hToken, dwFlags, pszPath = argv
        if csidl in shell32_defs.CSIDL:
            argv[1] = shell32_defs.CSIDL[csidl]
        if csidl == 0x1a:
            # CSIDL_APPDATA
            path = "C:\\Users\\{}\\AppData\\Roaming".format(emu.get_user()['name'])
        elif csidl == 0x28:
            # csidl_profile
            path = "C:\\Users\\{}".format(emu.get_user()['name'])
        elif csidl == 0 or csidl == 0x10:
            # CSIDL_DESKTOP or CSIDL_DESKTOPDIRECTORY
            path = "C:\\Users\\{}\\Desktop".format(emu.get_user()['name'])
        elif csidl == 2:
            # CSIDL_PROGRAMS
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs".format(emu.get_user()['name']) # noqa
        elif csidl == 6 or csidl == 0x1f:
            # CSIDL_FAVORITES or CSIDL_COMMON_FAVORITES
            path = "C:\\Users\\{}\\Favorites".format(emu.get_user()['name'])
        elif csidl == 7:
            # CSIDL_STARTUP
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(emu.get_user()['name']) # noqa
        elif csidl == 8:
            # CSIDL_RECENT
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Recent".format(emu.get_user()['name']) # noqa
        elif csidl == 9:
            # csidl_sendto
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\SendTo".format(emu.get_user()['name']) # noqa
        elif csidl == 0xb:
            # CSIDL_STARTMENU
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu".format(emu.get_user()['name']) # noqa
        elif csidl == 0x13:
            # CSIDL_NETHOOD
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts".format(emu.get_user()['name']) # noqa
        elif csidl == 0x15:
            # CSIDL_TEMPLATES
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Templates".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1b:
            # CSIDL_PRINTHOOD
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Printer Shortcuts".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1c:
            # CSIDL_LOCAL_APPDATA
            path = "C:\\Users\\{}\\AppData\\Local".format(emu.get_user()['name'])
        elif csidl == 0x20:
            # CSIDL_INTERNET_CACHE
            path = "C:\\Users\\{}\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet File".format(emu.get_user()['name']) # noqa
        elif csidl == 0x21:
            # CSIDL_COOKIES
            path = "C:\\Users\\{}\\AppData\\AppData\\Roaming\\Microsoft\\Windows\\Cookies".format(emu.get_user()['name']) # noqa
        elif csidl == 0x22:
            # CSIDL_HISTORY
            path = "C:\\Users\\{}\\AppData\\Local\\Microsoft\\Windows\\History".format(emu.get_user()['name']) # noqa
        elif csidl == 0x27:
            # CSIDL_MYPICTURES
            path = "C:\\Users\\{}\\Pictures".format(emu.get_user()['name'])
        elif csidl == 0x2f or csidl == 0x30:
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Administrative Tools".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1d:
            # CSIDL_ALTSTARTUP
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1e:
            path = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        elif csidl == 0x2a or csidl == 0x26:
            path = "C:\\Program Files"
        elif csidl == 0x2b or csidl == 0x2c:
            path = "C:\\Program Files\\Common Files"
        elif csidl == 0x24:
            path = "C:\\Windows"
        elif csidl == 0x25:
            path = "C:\\Windows\\System32"
        elif csidl == 0x14:
            path = "C:\\Windows\\Fonts"
        elif csidl == 0x23:
            path = "C:\\ProgramData"
        else:
            # Temp
            path = "C:\\Windows\\Temp"

        emu.write_mem_string(path, pszPath, self.get_char_width(ctx))
        return 0

    @apihook('SHGetFolderPathW', argc=5)
    def SHGetFolderPathW(self, emu, argv, ctx={}):
        """
        HWND   hwnd,
        int    csidl,
        HANDLE hToken,
        DWORD  dwFlags,
        LPWSTR pszPath
        """
        hwnd, csidl, hToken, dwFlags, pszPath = argv
        if csidl in shell32_defs.CSIDL:
            argv[1] = shell32_defs.CSIDL[csidl]
        if csidl == 0x1a:
            # CSIDL_APPDATA
            path = "C:\\Users\\{}\\AppData\\Roaming".format(emu.get_user()['name'])
        elif csidl == 0x28:
            # csidl_profile
            path = "C:\\Users\\{}".format(emu.get_user()['name'])
        elif csidl == 0 or csidl == 0x10:
            # CSIDL_DESKTOP or CSIDL_DESKTOPDIRECTORY
            path = "C:\\Users\\{}\\Desktop".format(emu.get_user()['name'])
        elif csidl == 2:
            # CSIDL_PROGRAMS
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs".format(emu.get_user()['name']) # noqa
        elif csidl == 6 or csidl == 0x1f:
            # CSIDL_FAVORITES or CSIDL_COMMON_FAVORITES
            path = "C:\\Users\\{}\\Favorites".format(emu.get_user()['name'])
        elif csidl == 7:
            # CSIDL_STARTUP
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(emu.get_user()['name']) # noqa
        elif csidl == 8:
            # CSIDL_RECENT
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Recent".format(emu.get_user()['name']) # noqa
        elif csidl == 9:
            # csidl_sendto
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\SendTo".format(emu.get_user()['name']) # noqa
        elif csidl == 0xb:
            # CSIDL_STARTMENU
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu".format(emu.get_user()['name']) # noqa
        elif csidl == 0x13:
            # CSIDL_NETHOOD
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Network Shortcuts".format(emu.get_user()['name']) # noqa
        elif csidl == 0x15:
            # CSIDL_TEMPLATES
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Templates".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1b:
            # CSIDL_PRINTHOOD
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Printer Shortcuts".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1c:
            # CSIDL_LOCAL_APPDATA
            path = "C:\\Users\\{}\\AppData\\Local".format(emu.get_user()['name'])
        elif csidl == 0x20:
            # CSIDL_INTERNET_CACHE
            path = "C:\\Users\\{}\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet File".format(emu.get_user()['name']) # noqa
        elif csidl == 0x21:
            # CSIDL_COOKIES
            path = "C:\\Users\\{}\\AppData\\AppData\\Roaming\\Microsoft\\Windows\\Cookies".format(emu.get_user()['name']) # noqa
        elif csidl == 0x22:
            # CSIDL_HISTORY
            path = "C:\\Users\\{}\\AppData\\Local\\Microsoft\\Windows\\History".format(emu.get_user()['name']) # noqa
        elif csidl == 0x27:
            # CSIDL_MYPICTURES
            path = "C:\\Users\\{}\\Pictures".format(emu.get_user()['name'])
        elif csidl == 0x2f or csidl == 0x30:
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Administrative Tools".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1d:
            # CSIDL_ALTSTARTUP
            path = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(emu.get_user()['name']) # noqa
        elif csidl == 0x1e:
            path = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        elif csidl == 0x2a or csidl == 0x26:
            path = "C:\\Program Files"
        elif csidl == 0x2b or csidl == 0x2c:
            path = "C:\\Program Files\\Common Files"
        elif csidl == 0x24:
            path = "C:\\Windows"
        elif csidl == 0x25:
            path = "C:\\Windows\\System32"
        elif csidl == 0x14:
            path = "C:\\Windows\\Fonts"
        elif csidl == 0x23:
            path = "C:\\ProgramData"
        else:
            # Temp
            path = "C:\\Windows\\Temp"

        emu.write_mem_string(path, pszPath, 2)
        return 0

    @apihook('SHGetKnownFolderPath', argc=4)
    def SHGetKnownFolderPath(self, emu, argv, ctx={}):
        """
        HRESULT SHGetKnownFolderPath(
          REFKNOWNFOLDERID rfid,
          DWORD            dwFlags,
          HANDLE           hToken,
          PWSTR            *ppszPath
        );
        """
        rfid, dwFlags, hToken, ppszPath = argv

        # Known folder GUIDs (common ones)
        # Read the GUID from memory (16 bytes)
        path = "C:\\Windows\\Temp"  # Default fallback

        if rfid:
            guid_bytes = self.mem_read(rfid, 16)
            # Convert to GUID string for matching
            # GUID format: Data1 (4 bytes), Data2 (2 bytes), Data3 (2 bytes), Data4 (8 bytes)
            import struct
            d1, d2, d3 = struct.unpack('<IHH', guid_bytes[:8])
            d4 = guid_bytes[8:16]
            guid_str = '{%08X-%04X-%04X-%s-%s}' % (
                d1, d2, d3,
                d4[:2].hex().upper(),
                d4[2:].hex().upper()
            )
            argv[0] = guid_str

            # Map known folder GUIDs to paths
            known_folders = {
                # FOLDERID_RoamingAppData
                '{3EB685DB-65F9-4CF6-A03A-E3EF65729F3D}': "C:\\Users\\{}\\AppData\\Roaming",
                # FOLDERID_LocalAppData
                '{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}': "C:\\Users\\{}\\AppData\\Local",
                # FOLDERID_LocalAppDataLow
                '{A520A1A4-1780-4FF6-BD18-167343C5AF16}': "C:\\Users\\{}\\AppData\\LocalLow",
                # FOLDERID_Desktop
                '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}': "C:\\Users\\{}\\Desktop",
                # FOLDERID_Documents
                '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}': "C:\\Users\\{}\\Documents",
                # FOLDERID_Downloads
                '{374DE290-123F-4565-9164-39C4925E467B}': "C:\\Users\\{}\\Downloads",
                # FOLDERID_Profile
                '{5E6C858F-0E22-4760-9AFE-EA3317B67173}': "C:\\Users\\{}",
                # FOLDERID_ProgramData
                '{62AB5D82-FDC1-4DC3-A9DD-070D1D495D97}': "C:\\ProgramData",
                # FOLDERID_ProgramFiles
                '{905E63B6-C1BF-494E-B29C-65B732D3D21A}': "C:\\Program Files",
                # FOLDERID_ProgramFilesX86
                '{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}': "C:\\Program Files (x86)",
                # FOLDERID_System
                '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}': "C:\\Windows\\System32",
                # FOLDERID_Windows
                '{F38BF404-1D43-42F2-9305-67DE0B28FC23}': "C:\\Windows",
                # FOLDERID_Startup
                '{B97D20BB-F46A-4C97-BA10-5E3608430854}': "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                # FOLDERID_Programs
                '{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}': "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
                # FOLDERID_StartMenu
                '{625B53C3-AB48-4EC1-BA1F-A1EF4146FC19}': "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu",
                # FOLDERID_Fonts
                '{FD228CB7-AE11-4AE3-864C-16F3910AB8FE}': "C:\\Windows\\Fonts",
                # FOLDERID_CommonStartup
                '{82A5EA35-D9CD-47C5-9629-E15D2F714E6E}': "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup",
            }

            user_name = emu.get_user()['name']
            if guid_str in known_folders:
                path = known_folders[guid_str].format(user_name)

        # Allocate memory for the path string (CoTaskMemAlloc style)
        path_wide = (path + '\x00').encode('utf-16le')
        path_ptr = self.mem_alloc(len(path_wide), tag='api.SHGetKnownFolderPath')
        self.mem_write(path_ptr, path_wide)

        # Write the pointer to ppszPath
        if ppszPath:
            self.mem_write(ppszPath, path_ptr.to_bytes(emu.get_ptr_size(), 'little'))

        return windefs.S_OK  # 0
