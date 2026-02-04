# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import speakeasy.winenv.arch as _arch
import speakeasy.windows.sessman as sessman
import speakeasy.winenv.defs.windows.user32 as windefs
import speakeasy.winenv.defs.windows.windef as windef

from .. import api

IDCANCEL = 2

IDI_APPLICATION = 32512
IDI_ASTERISK = 32516
IDI_ERROR = 32513
IDI_EXCLAMATION = 32515
IDI_HAND = 32513
IDI_INFORMATION = 32516
IDI_QUESTION = 32514
IDI_SHIELD = 32518
IDI_WARNING = 32515
IDI_WINLOGO = 32517

UOI_FLAGS = 1


class User32(api.ApiHandler):

    """
    Implements exported functions from user32.dll
    """

    name = 'user32'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(User32, self).__init__(emu)

        self.funcs = {}
        self.data = {}
        self.window_hooks = {}
        self.handle = 0
        self.win = None
        self.handles = []
        self.wndprocs = {}
        self.timer_count = 0
        self.sessman = sessman.SessionManager(config=None)

        super(User32, self).__get_hook_attrs__(self)

    def get_handle(self):
        self.handle += 4
        hnd = self.handle
        self.handles.append(hnd)
        return hnd

    def find_string_resource_by_id(self, pe, uID):
        if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
            for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                if entry.id == 6:  # "String Table"
                    for str_entry in entry.directory.entries:
                        s = str_entry.directory.strings.get(uID, None)
                        if s is not None:
                            return s
        return None

    @apihook('GetDesktopWindow', argc=0)
    def GetDesktopWindow(self, emu, argv, ctx={}):
        '''HWND GetDesktopWindow();'''

        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook('ShowWindow', argc=2)
    def ShowWindow(self, emu, argv, ctx={}):
        '''BOOL ShowWindow(
          HWND hWnd,
          int  nCmdShow
        );'''

        rv = 1

        return rv

    @apihook('CreateWindowStation', argc=4)
    def CreateWindowStation(self, emu, argv, ctx={}):
        '''
        HWINSTA CreateWindowStation(
            LPCSTR                lpwinsta,
            DWORD                 dwFlags,
            ACCESS_MASK           dwDesiredAccess,
            LPSECURITY_ATTRIBUTES lpsa
        );
        '''
        winsta, flags, access, sa = argv

        return self.get_handle()

    @apihook('CreateWindowStationW', argc=4)
    def CreateWindowStationW(self, emu, argv, ctx={}):
        '''
        HWINSTA CreateWindowStationW(
            LPCWSTR               lpwinsta,
            DWORD                 dwFlags,
            ACCESS_MASK           dwDesiredAccess,
            LPSECURITY_ATTRIBUTES lpsa
        );
        '''
        winsta, flags, access, sa = argv

        return self.get_handle()

    @apihook('SetProcessWindowStation', argc=1)
    def SetProcessWindowStation(self, emu, argv, ctx={}):
        '''
        BOOL SetProcessWindowStation(
            HWINSTA hWinSta
        );
        '''
        winsta, = argv

        rv = False
        if winsta:
            rv = True

        return rv

    @apihook('GetDC', argc=1)
    def GetDC(self, emu, argv, ctx={}):
        '''
        HDC GetDC(
          HWND hWnd
        );
        '''

        rv = self.sessman.get_device_context()

        return rv

    @apihook('GetWindowDC', argc=1)
    def GetWindowDC(self, emu, argv, ctx={}):
        '''
        HDC GetWindowDC(
          HWND hWnd
        );
        '''
        hWnd, = argv
        # Returns a DC for the entire window including title bar, menus, scroll bars
        rv = self.sessman.get_device_context()
        return rv

    @apihook('RegisterClassEx', argc=1)
    def RegisterClassEx(self, emu, argv, ctx={}):
        '''
        ATOM RegisterClassEx(
            const WNDCLASSEXA *Arg1
        );
        '''
        Arg1, = argv
        wclass = windefs.WNDCLASSEX(emu.get_ptr_size())
        wclass = self.mem_cast(wclass, Arg1)

        cn = None
        cw = self.get_char_width(ctx)
        if wclass.lpszClassName:
            cn = self.read_mem_string(wclass.lpszClassName, cw)

        atom = self.sessman.create_window_class(wclass, cn)

        return atom

    @apihook('RegisterClassW', argc=1)
    def RegisterClassW(self, emu, argv, ctx={}):
        '''
        ATOM RegisterClassW(
            const WNDCLASSW *lpWndClass
        );
        '''
        lpWndClass, = argv
        wc = windefs.WNDCLASS(emu.get_ptr_size())
        wc = self.mem_cast(wc, lpWndClass)

        cn = None
        cw = 2 # Wide
        if wc.lpszClassName:
            cn = self.read_mem_string(wc.lpszClassName, cw)

        atom = self.sessman.create_window_class(wc, cn)

        return atom

    @apihook('RegisterClassExW', argc=1)
    def RegisterClassExW(self, emu, argv, ctx={}):
        '''
        ATOM RegisterClassExW(
            const WNDCLASSEXW *Arg1
        );
        '''
        Arg1, = argv
        wclass = windefs.WNDCLASSEX(emu.get_ptr_size())
        wclass = self.mem_cast(wclass, Arg1)

        cn = None
        # Always wide for W API
        cw = 2
        if wclass.lpszClassName:
            cn = self.read_mem_string(wclass.lpszClassName, cw)

        atom = self.sessman.create_window_class(wclass, cn)

        return atom

    @apihook('UnregisterClass', argc=2)
    def UnregisterClass(self, emu, argv, ctx={}):
        '''
        BOOL UnregisterClass(
            LPCSTR    lpClassName,
            HINSTANCE hInstance
        );
        '''

        return 1

    @apihook('UnregisterClassW', argc=2)
    def UnregisterClassW(self, emu, argv, ctx={}):
        '''
        BOOL UnregisterClassW(
            LPCWSTR   lpClassName,
            HINSTANCE hInstance
        );
        '''

        return 1

    @apihook('SetCursorPos', argc=2)
    def SetCursorPos(self, emu, argv, ctx={}):
        '''
        BOOL SetCursorPos(
        int X,
        int Y
        );
        '''
        return 1

    @apihook('CloseDesktop', argc=1)
    def CloseDesktop(self, emu, argv, ctx={}):
        '''
        BOOL CloseDesktop(
        HDESK hDesktop
        );
        '''
        return 1

    @apihook('CloseWindowStation', argc=1)
    def CloseWindowStation(self, emu, argv, ctx={}):
        '''
        BOOL CloseWindowStation(
        HWINSTA hWinSta
        );
        '''
        return 1

    @apihook('GetThreadDesktop', argc=1)
    def GetThreadDesktop(self, emu, argv, ctx={}):
        '''
        HDESK GetThreadDesktop(
        DWORD dwThreadId
        );
        '''
        return 1

    @apihook('OpenWindowStation', argc=3)
    def OpenWindowStation(self, emu, argv, ctx={}):
        '''
        HWINSTA OpenWindowStation(
        LPCSTR      lpszWinSta,
        BOOL        fInherit,
        ACCESS_MASK dwDesiredAccess
        );
        '''
        return 1

    @apihook('OpenWindowStationW', argc=3)
    def OpenWindowStationW(self, emu, argv, ctx={}):
        '''
        HWINSTA OpenWindowStationW(
        LPCWSTR     lpszWinSta,
        BOOL        fInherit,
        ACCESS_MASK dwDesiredAccess
        );
        '''
        return 1

    @apihook('ChangeWindowMessageFilter', argc=2)
    def ChangeWindowMessageFilter(self, emu, argv, ctx={}):
        '''
        BOOL ChangeWindowMessageFilter(
            UINT  message,
            DWORD dwFlag
        );
        '''
        msg, flag = argv
        emu.enable_code_hook()
        return True

    @apihook('UpdateWindow', argc=1)
    def UpdateWindow(self, emu, argv, ctx={}):
        '''
        BOOL UpdateWindow(
            HWND hWnd
        );
        '''
        hnd, = argv
        window = self.sessman.get_window(hnd)
        if not window:
            return False

        wc = self.sessman.get_window_class(window.class_name)
        if wc.wclass.lpfnWndProc:
            cb_args = (hnd, windefs.WM_PAINT, 0, 0)
            self.setup_callback(wc.wclass.lpfnWndProc, cb_args, caller_argv=argv)

        return True

    @apihook('PostQuitMessage', argc=1)
    def PostQuitMessage(self, emu, argv, ctx={}):
        '''
        void PostQuitMessage(
            int nExitCode
        );
        '''
        return

    @apihook('DestroyWindow', argc=1)
    def DestroyWindow(self, emu, argv, ctx={}):
        '''
        BOOL DestroyWindow(
            HWND hWnd
        );
        '''
        return True

    @apihook('DefWindowProc', argc=4)
    def DefWindowProc(self, emu, argv, ctx={}):
        '''
        LRESULT LRESULT DefWindowProc(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        return 0

    @apihook('DefWindowProcW', argc=4)
    def DefWindowProcW(self, emu, argv, ctx={}):
        '''
        LRESULT LRESULT DefWindowProcW(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        return 0

    @apihook('CreateWindowEx', argc=12)
    def CreateWindowEx(self, emu, argv, ctx={}):
        '''
        HWND CreateWindowExA(
            DWORD     dwExStyle,
            LPCSTR    lpClassName,
            LPCSTR    lpWindowName,
            DWORD     dwStyle,
            int       X,
            int       Y,
            int       nWidth,
            int       nHeight,
            HWND      hWndParent,
            HMENU     hMenu,
            HINSTANCE hInstance,
            LPVOID    lpParam
        );
        '''
        cw = self.get_char_width(ctx)
        _, cn, wn, _, x, y, width, height, parent, menu, inst, param = argv
        if cn:
            cn = self.read_mem_string(cn, cw)
            argv[1] = cn
        else:
            cn = None
        if wn:
            wn = self.read_mem_string(wn, cw)
            argv[2] = wn
        else:
            wn = None
        hnd = self.sessman.create_window(wn, cn)
        return hnd

    @apihook('CreateWindowExW', argc=12)
    def CreateWindowExW(self, emu, argv, ctx={}):
        '''
        HWND CreateWindowExW(
            DWORD     dwExStyle,
            LPCWSTR   lpClassName,
            LPCWSTR   lpWindowName,
            DWORD     dwStyle,
            int       X,
            int       Y,
            int       nWidth,
            int       nHeight,
            HWND      hWndParent,
            HMENU     hMenu,
            HINSTANCE hInstance,
            LPVOID    lpParam
        );
        '''
        cw = 2
        _, cn, wn, _, x, y, width, height, parent, menu, inst, param = argv
        if cn:
            cn = self.read_mem_string(cn, cw)
            argv[1] = cn
        else:
            cn = None
        if wn:
            wn = self.read_mem_string(wn, cw)
            argv[2] = wn
        else:
            wn = None
        hnd = self.sessman.create_window(wn, cn)
        return hnd

    @apihook('SetLayeredWindowAttributes', argc=4)
    def SetLayeredWindowAttributes(self, emu, argv, ctx={}):
        '''
        BOOL SetLayeredWindowAttributes(
          [in] HWND     hwnd,
          [in] COLORREF crKey,
          [in] BYTE     bAlpha,
          [in] DWORD    dwFlags
        );
        '''
        hwnd, crKey, bAlpha, dwFlags = argv
        return 1

    @apihook('MessageBox', argc=4)
    def MessageBox(self, emu, argv, ctx={}):
        '''int MessageBox(
          HWND    hWnd,
          LPCTSTR lpText,
          LPCTSTR lpCaption,
          UINT    uType
        );'''
        hWnd, lpText, lpCaption, uType = argv

        cw = self.get_char_width(ctx)

        if lpText:
            text = self.read_mem_string(lpText, cw)
            argv[1] = text
        if lpCaption:
            cap = self.read_mem_string(lpCaption, cw)
            argv[2] = cap
        rv = IDCANCEL

        return rv

    @apihook('MessageBoxW', argc=4)
    def MessageBoxW(self, emu, argv, ctx={}):
        '''int MessageBoxW(
          HWND    hWnd,
          LPCWSTR lpText,
          LPCWSTR lpCaption,
          UINT    uType
        );'''
        hWnd, lpText, lpCaption, uType = argv

        cw = 2

        if lpText:
            text = self.read_mem_string(lpText, cw)
            argv[1] = text
        if lpCaption:
            cap = self.read_mem_string(lpCaption, cw)
            argv[2] = cap
        rv = IDCANCEL

        return rv

    @apihook('MessageBoxEx', argc=5)
    def MessageBoxEx(self, emu, argv, ctx={}):
        '''
        int MessageBoxExA(
            HWND   hWnd,
            LPCSTR lpText,
            LPCSTR lpCaption,
            UINT   uType,
            WORD   wLanguageId
        );
        '''
        av = argv[:-1]
        rv = self.MessageBox(emu, av, ctx)
        argv[:4] = av
        return rv

    @apihook('MessageBoxExW', argc=5)
    def MessageBoxExW(self, emu, argv, ctx={}):
        '''
        int MessageBoxExW(
            HWND   hWnd,
            LPCWSTR lpText,
            LPCWSTR lpCaption,
            UINT   uType,
            WORD   wLanguageId
        );
        '''
        av = argv[:-1]
        rv = self.MessageBoxW(emu, av, ctx)
        argv[:4] = av
        return rv

    @apihook('LoadString', argc=4)
    def LoadString(self, emu, argv, ctx={}):
        """
        int LoadStringW(
          HINSTANCE hInstance,
          UINT      uID,
          LPWSTR    lpBuffer,
          int       cchBufferMax
        );
        """

        hInstance, uID, lpBuffer, ccBufferMax = argv
        cw = self.get_char_width(ctx)
        size = 0

        if hInstance == 0:
            pe = emu.modules[0][0]
        else:
            pe = emu.get_mod_from_addr(hInstance)
            if pe and hInstance != pe.get_base():
                return 0

        s = self.find_string_resource_by_id(pe, uID)
        if s is None:
            # self.logger.info("unable to find resource string id %04X" % uID)
            return 0

        if cw == 2:
            encoded = s.encode('utf-16le')
        elif cw == 1:
            encoded = s.encode('utf-8')

        size = int(len(encoded) / cw)

        if size == 0:
            # self.logger.debug("resource id %04X not found" % uID)
            return 0

        if ccBufferMax == 0:
            # TODO this should be done properly, but requires more research
            offset = pe.get_memory_mapped_image().find(encoded)
            emu.mem_write(lpBuffer, (pe.get_base() + offset).to_bytes(emu.get_ptr_size(),
                                                                      'little'))
            return size

        if len(encoded) > ccBufferMax:
            encoded = encoded[:ccBufferMax * cw]

        emu.mem_write(lpBuffer, encoded)
        if cw == 1:
            argv[2] = s
        else:
            argv[2] = s

        return len(encoded)

    @apihook('LoadStringW', argc=4)
    def LoadStringW(self, emu, argv, ctx={}):
        """
        int LoadStringW(
          HINSTANCE hInstance,
          UINT      uID,
          LPWSTR    lpBuffer,
          int       cchBufferMax
        );
        """

        hInstance, uID, lpBuffer, ccBufferMax = argv
        cw = 2
        size = 0

        if hInstance == 0:
            pe = emu.modules[0][0]
        else:
            pe = emu.get_mod_from_addr(hInstance)
            if pe and hInstance != pe.get_base():
                return 0

        s = self.find_string_resource_by_id(pe, uID)
        if s is None:
            # self.logger.info("unable to find resource string id %04X" % uID)
            return 0

        encoded = s.encode('utf-16le')

        size = int(len(encoded) / cw)

        if size == 0:
            # self.logger.debug("resource id %04X not found" % uID)
            return 0

        if ccBufferMax == 0:
            # TODO this should be done properly, but requires more research
            offset = pe.get_memory_mapped_image().find(encoded)
            emu.mem_write(lpBuffer, (pe.get_base() + offset).to_bytes(emu.get_ptr_size(),
                                                                      'little'))
            return size

        if len(encoded) > ccBufferMax * cw:
            encoded = encoded[:ccBufferMax * cw]

        emu.mem_write(lpBuffer, encoded)
        argv[2] = s

        return len(encoded) // cw

    @apihook('GetCursorPos', argc=1)
    def GetCursorPos(self, emu, argv, ctx={}):
        """
        BOOL GetCursorPos(
          LPPOINT lpPoint
        );
        """

        lpPoint, = argv

        rv = 0
        return rv

    @apihook('GetAsyncKeyState', argc=1)
    def GetAsyncKeyState(self, emu, argv, ctx={}):
        '''
        SHORT GetAsyncKeyState(
          [in] int vKey
        );
        '''

        # From MS docs:
        # If the most significant bit is set, the key is down, 
        # and if the least significant bit is set, the key was 
        # pressed after the previous call to GetAsyncKeyState

        return 0

    @apihook('GetKeyboardType', argc=1)
    def GetKeyboardType(self, emu, argv, ctx={}):
        '''
        int GetKeyboardType(
          int nTypeFlag
        );
        '''
        _type, = argv
        if _type == 0:
            return 4
        elif _type == 1:
            return 0
        elif _type == 2:
            return 12
        return 0

    @apihook('GetKeyboardLayout', argc=1)
    def GetKeyboardLayout(self, emu, argv, ctx={}):
        '''
        HKL GetKeyboardLayout(
          DWORD idThread
        );
        '''
        idThread, = argv
        # Return default locale identifier (US English: 0x04090409)
        return 0x04090409

    @apihook('GetClassInfoW', argc=3)
    def GetClassInfoW(self, emu, argv, ctx={}):
        '''
        BOOL GetClassInfoW(
          HINSTANCE   hInstance,
          LPCWSTR     lpClassName,
          LPWNDCLASSW lpWndClass
        );
        '''
        hInstance, lpClassName, lpWndClass = argv
        
        cn = None
        if lpClassName < 0x10000:
            pass
        else:
            cn = self.read_mem_string(lpClassName, 2)
        
        if not cn:
            return 0

        wc = self.sessman.get_window_class(cn)
        if hasattr(wc, 'wclass'):
            return 1
            
        return 0

    @apihook('GetSystemMetrics', argc=1)
    def GetSystemMetrics(self, emu, argv, ctx={}):
        """
        int GetSystemMetrics(
          int nIndex
        );
        """

        nIndex, = argv

        rv = 1
        return rv

    @apihook('LoadBitmap', argc=2)
    def LoadBitmap(self, emu, argv, ctx={}):
        """
        HBITMAP LoadBitmap(
            HINSTANCE hInstance,
            LPCSTR    lpBitmapName
        );
        """
        hInstance, lpBitmapName = argv
        rv = self.get_handle()
        return rv

    @apihook('LoadBitmapW', argc=2)
    def LoadBitmapW(self, emu, argv, ctx={}):
        """
        HBITMAP LoadBitmapW(
            HINSTANCE hInstance,
            LPCWSTR   lpBitmapName
        );
        """
        hInstance, lpBitmapName = argv
        rv = self.get_handle()
        return rv

    @apihook('GetClientRect', argc=2)
    def GetClientRect(self, emu, argv, ctx={}):
        """
        BOOL GetClientRect(
          [in]  HWND   hWnd,
          [out] LPRECT lpRect
        );
        """
        return 0

    @apihook('RegisterWindowMessage', argc=1)
    def RegisterWindowMessage(self, emu, argv, ctx={}):
        '''
        UINT RegisterWindowMessageA(
          LPCSTR lpString
        );
        '''

        lpString, = argv
        rv = 0xc000

        cw = self.get_char_width(ctx)

        s = self.read_mem_string(lpString, cw)
        argv[0] = s

        return rv

    @apihook('RegisterWindowMessageW', argc=1)
    def RegisterWindowMessageW(self, emu, argv, ctx={}):
        '''
        UINT RegisterWindowMessageW(
          LPCWSTR lpString
        );
        '''
        lpString, = argv
        rv = 0xc000

        # Always wide for W API
        cw = 2
        s = self.read_mem_string(lpString, cw)
        argv[0] = s
        
        # Simple hash to generate unique ID within range 0xC000-0xFFFF
        rv += (hash(s) & 0x3FFF)

        return rv

    @apihook('RegisterClipboardFormatW', argc=1)
    def RegisterClipboardFormatW(self, emu, argv, ctx={}):
        '''
        UINT RegisterClipboardFormatW(
          LPCWSTR lpszFormat
        );
        '''
        lpszFormat, = argv
        rv = 0xC000 
        
        cw = 2
        s = self.read_mem_string(lpszFormat, cw)
        argv[0] = s
        
        rv += (hash(s) & 0x3FFF)

        return rv

    @apihook('RegisterDeviceNotificationW', argc=3)
    def RegisterDeviceNotificationW(self, emu, argv, ctx={}):
        '''
        HDEVNOTIFY RegisterDeviceNotificationW(
          HANDLE hRecipient,
          LPVOID NotificationFilter,
          DWORD  Flags
        );
        '''
        hRecipient, NotificationFilter, Flags = argv

        return self.get_handle()

    @apihook('SetProcessDpiAwarenessContext', argc=1)
    def SetProcessDpiAwarenessContext(self, emu, argv, ctx={}):
        '''
        BOOL SetProcessDpiAwarenessContext(
          DPI_AWARENESS_CONTEXT value
        );
        '''
        value, = argv
        return 1

    @apihook('wsprintf', argc=_arch.VAR_ARGS, conv=_arch.CALL_CONV_CDECL)
    def wsprintf(self, emu, argv, ctx={}):
        """
        int WINAPIV wsprintf(
          LPSTR  ,
          LPCSTR ,
          ...
        );
        """
        cw = self.get_char_width(ctx)

        buf, fmt = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2)
        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        if not fmt_cnt:
            self.write_mem_string(fmt_str, buf, cw)
            return len(fmt_str)

        _args = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2 + fmt_cnt)[2:]
        fin = self.do_str_format(fmt_str, _args)

        self.write_mem_string(fin, buf, cw)

        argv.append(fin)
        argv.append(fmt_str)
        return len(fin)

    @apihook('wsprintfW', argc=_arch.VAR_ARGS, conv=_arch.CALL_CONV_CDECL)
    def wsprintfW(self, emu, argv, ctx={}):
        """
        int WINAPIV wsprintfW(
          LPWSTR  ,
          LPCWSTR ,
          ...
        );
        """
        cw = 2

        buf, fmt = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2)
        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        if not fmt_cnt:
            self.write_mem_string(fmt_str, buf, cw)
            return len(fmt_str)

        _args = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2 + fmt_cnt)[2:]
        fin = self.do_str_format(fmt_str, _args)

        self.write_mem_string(fin, buf, cw)

        argv.append(fin)
        argv.append(fmt_str)
        return len(fin)

    @apihook('PeekMessage', argc=5)
    def PeekMessage(self, emu, argv, ctx={}):
        '''
        BOOL PeekMessageA(
            LPMSG lpMsg,
            HWND  hWnd,
            UINT  wMsgFilterMin,
            UINT  wMsgFilterMax,
            UINT  wRemoveMsg
        );
        '''
        return False

    @apihook('PeekMessageW', argc=5)
    def PeekMessageW(self, emu, argv, ctx={}):
        '''
        BOOL PeekMessageW(
            LPMSG lpMsg,
            HWND  hWnd,
            UINT  wMsgFilterMin,
            UINT  wMsgFilterMax,
            UINT  wRemoveMsg
        );
        '''
        return False

    @apihook('PostMessage', argc=4)
    def PostMessage(self, emu, argv, ctx={}):
        '''
        BOOL PostMessage(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        return True

    @apihook('PostMessageW', argc=4)
    def PostMessageW(self, emu, argv, ctx={}):
        '''
        BOOL PostMessageW(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        return True

    @apihook('SendMessage', argc=4)
    def SendMessage(self, emu, argv, ctx={}):
        '''
        LRESULT SendMessage(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        hWnd, Msg, wParam, lParam = argv
        if hWnd in self.wndprocs:
            emu.set_pc(self.wndprocs[hWnd])

        return False

    @apihook('SendMessageW', argc=4)
    def SendMessageW(self, emu, argv, ctx={}):
        '''
        LRESULT SendMessageW(
            HWND   hWnd,
            UINT   Msg,
            WPARAM wParam,
            LPARAM lParam
        );
        '''
        hWnd, Msg, wParam, lParam = argv
        if hWnd in self.wndprocs:
            emu.set_pc(self.wndprocs[hWnd])

        return False

    @apihook('SetWindowsHookEx', argc=4)
    def SetWindowsHookEx(self, emu, argv, ctx={}):
        '''
        HHOOK SetWindowsHookEx(
            int       idHook,
            HOOKPROC  lpfn,
            HINSTANCE hmod,
            DWORD     dwThreadId
        );
        '''
        idHook, lpfn, hmod, dwThreadId = argv

        hname = windefs.get_windowhook_flags(idHook)
        if hname:
            hname = hname[0]
            argv[0] = hname

        hnd = self.get_handle()
        self.window_hooks.update({hnd: (lpfn, hmod)})
        return hnd

    @apihook('SetWindowsHookExW', argc=4)
    def SetWindowsHookExW(self, emu, argv, ctx={}):
        '''
        HHOOK SetWindowsHookExW(
            int       idHook,
            HOOKPROC  lpfn,
            HINSTANCE hmod,
            DWORD     dwThreadId
        );
        '''
        idHook, lpfn, hmod, dwThreadId = argv

        hname = windefs.get_windowhook_flags(idHook)
        if hname:
            hname = hname[0]
            argv[0] = hname

        hnd = self.get_handle()
        self.window_hooks.update({hnd: (lpfn, hmod)})
        return hnd

    @apihook('UnhookWindowsHookEx', argc=1)
    def UnhookWindowsHookEx(self, emu, argv, ctx={}):
        '''
        BOOL UnhookWindowsHookEx(
            HHOOK hhk
        );
        '''
        hhk, = argv

        rv = False
        if self.window_hooks.get(hhk):
            self.window_hooks.pop(hhk)
            rv = True
        return rv

    @apihook('MsgWaitForMultipleObjects', argc=5)
    def MsgWaitForMultipleObjects(self, emu, argv, ctx={}):
        '''
        DWORD MsgWaitForMultipleObjects(
            DWORD        nCount,
            const HANDLE *pHandles,
            BOOL         fWaitAll,
            DWORD        dwMilliseconds,
            DWORD        dwWakeMask
        );
        '''
        return 0

    @apihook('GetMessage', argc=4)
    def GetMessage(self, emu, argv, ctx={}):
        '''
        BOOL GetMessage(
            LPMSG lpMsg,
            HWND  hWnd,
            UINT  wMsgFilterMin,
            UINT  wMsgFilterMax
        );
        '''
        lpMsg, hWnd, wMsgFilterMin, wMsgFilterMax = argv

        t = emu.get_current_thread()
        try:
            msg = t.message_queue.pop(0)
        except IndexError:
            # If the queue is empty but a timer is active, write a WM_TIMER message and return True
            if self.timer_count > 0:
                msg = windefs.MSG(emu.get_ptr_size())
                msg.hwnd = hWnd
                msg.message = windefs.WM_TIMER
            else:
                return False

        self.mem_write(lpMsg, msg.get_bytes())

        return True

    @apihook('GetMessageW', argc=4)
    def GetMessageW(self, emu, argv, ctx={}):
        '''
        BOOL GetMessageW(
            LPMSG lpMsg,
            HWND  hWnd,
            UINT  wMsgFilterMin,
            UINT  wMsgFilterMax
        );
        '''
        lpMsg, hWnd, wMsgFilterMin, wMsgFilterMax = argv

        t = emu.get_current_thread()
        try:
            msg = t.message_queue.pop(0)
        except IndexError:
            # If the queue is empty but a timer is active, write a WM_TIMER message and return True
            if self.timer_count > 0:
                msg = windefs.MSG(emu.get_ptr_size())
                msg.hwnd = hWnd
                msg.message = windefs.WM_TIMER
            else:
                return False

        self.mem_write(lpMsg, msg.get_bytes())

        return True

    @apihook('TranslateMessage', argc=1)
    def TranslateMessage(self, emu, argv, ctx={}):
        '''
        BOOL TranslateMessage(
            const MSG *lpMsg
        );
        '''
        return True

    @apihook('DispatchMessage', argc=1)
    def DispatchMessage(self, emu, argv, ctx={}):
        '''
        LRESULT DispatchMessage(
            const MSG *lpMsg
        );
        '''
        lpMsg, = argv

        msg = windefs.MSG(emu.get_ptr_size())
        msg = self.mem_cast(msg, lpMsg)

        return 0

    @apihook('DispatchMessageW', argc=1)
    def DispatchMessageW(self, emu, argv, ctx={}):
        '''
        LRESULT DispatchMessageW(
            const MSG *lpMsg
        );
        '''
        lpMsg, = argv

        msg = windefs.MSG(emu.get_ptr_size())
        msg = self.mem_cast(msg, lpMsg)

        return 0

    @apihook('GetForegroundWindow', argc=0)
    def GetForegroundWindow(self, emu, argv, ctx={}):
        '''
        HWND GetForegroundWindow();
        '''
        return self.get_handle()

    @apihook('LoadCursor', argc=2)
    def LoadCursor(self, emu, argv, ctx={}):
        '''
        HCURSOR LoadCursor(
        HINSTANCE hInstance,
        LPCSTR    lpCursorName
        );
        '''
        return self.get_handle()

    @apihook('LoadCursorW', argc=2)
    def LoadCursorW(self, emu, argv, ctx={}):
        '''
        HCURSOR LoadCursorW(
        HINSTANCE hInstance,
        LPCWSTR    lpCursorName
        );
        '''
        return self.get_handle()

    @apihook('FindWindow', argc=2)
    def FindWindow(self, emu, argv, ctx={}):
        '''
        HWND FindWindow(
            LPCSTR lpClassName,
            LPCSTR lpWindowName
        );
        '''
        lpClassName, lpWindowName = argv
        cw = self.get_char_width(ctx)
        if lpClassName:
            cn = self.read_mem_string(lpClassName, cw)
            argv[0] = cn
        if lpWindowName:
            wn = self.read_mem_string(lpWindowName, cw)
            argv[1] = wn
        return 0

    @apihook('FindWindowW', argc=2)
    def FindWindowW(self, emu, argv, ctx={}):
        '''
        HWND FindWindowW(
            LPCWSTR lpClassName,
            LPCWSTR lpWindowName
        );
        '''
        lpClassName, lpWindowName = argv
        cw = 2
        if lpClassName:
            cn = self.read_mem_string(lpClassName, cw)
            argv[0] = cn
        if lpWindowName:
            wn = self.read_mem_string(lpWindowName, cw)
            argv[1] = wn
        return 0

    @apihook('GetWindowText', argc=3)
    def GetWindowText(self, emu, argv, ctx={}):
        '''
        int GetWindowText(
            HWND  hWnd,
            LPSTR lpString,
            int   nMaxCount
        );
        '''
        hnd, pstr, maxc = argv

        cw = self.get_char_width(ctx)
        win_text = 'speakeasy window'
        if pstr:
            if cw == 2:
                wt = (win_text).encode('utf-16le')
            else:
                wt = (win_text).encode('utf-8')
            self.mem_write(pstr, wt)

        return len(win_text)

    @apihook('GetWindowTextW', argc=3)
    def GetWindowTextW(self, emu, argv, ctx={}):
        '''
        int GetWindowTextW(
            HWND  hWnd,
            LPWSTR lpString,
            int   nMaxCount
        );
        '''
        hnd, pstr, maxc = argv

        cw = 2
        win_text = 'speakeasy window'
        if pstr:
            wt = (win_text).encode('utf-16le')
            self.mem_write(pstr, wt)

        return len(win_text)

    @apihook('PaintDesktop', argc=1)
    def PaintDesktop(self, emu, argv, ctx={}):
        '''
        BOOL PaintDesktop(
        HDC hdc
        );
        '''
        return 0

    @apihook('wvsprintf', argc=_arch.VAR_ARGS, conv=_arch.CALL_CONV_CDECL)
    def wvsprintf(self, emu, argv, ctx={}):
        buf, fmt, va_list = emu.get_func_argv(_arch.CALL_CONV_CDECL, 3)[:3]
        cw = self.get_char_width(ctx)
        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        vargs = self.va_args(va_list, fmt_cnt)
        fin = self.do_str_format(fmt_str, vargs)
        self.write_string(fin, buf)
        argv.clear()
        argv.append(fin)
        argv.append(fmt_str)
        return len(fin)

    @apihook('wvsprintfW', argc=_arch.VAR_ARGS, conv=_arch.CALL_CONV_CDECL)
    def wvsprintfW(self, emu, argv, ctx={}):
        buf, fmt, va_list = emu.get_func_argv(_arch.CALL_CONV_CDECL, 3)[:3]
        cw = 2
        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        vargs = self.va_args(va_list, fmt_cnt)
        fin = self.do_str_format(fmt_str, vargs, is_wide=True)
        self.write_mem_string(fin, buf, cw)
        argv.clear()
        argv.append(fin)
        argv.append(fmt_str)
        return len(fin)

    @apihook('wsprintfW', argc=_arch.VAR_ARGS, conv=_arch.CALL_CONV_CDECL)
    def wsprintfW(self, emu, argv, ctx={}):
        buf, fmt = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2)[:2]
        cw = 2
        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        all_args = emu.get_func_argv(_arch.CALL_CONV_CDECL, 2 + fmt_cnt)
        vargs = all_args[2:]

        fin = self.do_str_format(fmt_str, vargs, is_wide=True)
        self.write_mem_string(fin, buf, cw)
        argv.clear()
        argv.append(fin)
        argv.append(fmt_str)
        return len(fin)

    @apihook('ReleaseDC', argc=2)
    def ReleaseDC(self, emu, argv, ctx={}):
        '''
        int ReleaseDC(
          HWND hWnd,
          HDC  hDC
        );
        '''
        return 0

    @apihook('CharNext', argc=1)
    def CharNext(self, emu, argv, ctx={}):
        '''
        LPSTR CharNext(
            LPCSTR lpsz
        );
        '''
        s, = argv
        rv = 0
        cw = self.get_char_width(ctx)
        if s:
            rv = s + cw
        return rv

    @apihook('CharNextW', argc=1)
    def CharNextW(self, emu, argv, ctx={}):
        '''
        LPWSTR CharNextW(
            LPCWSTR lpsz
        );
        '''
        s, = argv
        rv = 0
        cw = 2
        if s:
            rv = s + cw
        return rv

    @apihook('CharPrev', argc=2)
    def CharPrev(self, emu, argv, ctx={}):
        '''
        LPSTR CharPrev(
            LPCSTR lpszStart,
            LPCSTR lpszCurrent
        );
        '''
        '''
        Got this from wine.          
        https://github.com/wine-mirror/wine/blob/a8c1d5c108fc57e4d78e9db126f395c89083a83d/dlls/kernelbase/string.c
        '''
        s,c = argv
        cw = self.get_char_width(ctx)
        while(s<c):
            n  = s + cw
            if (n>=c): 
                break;
            s = n;

        return s

    @apihook('CharPrevW', argc=2)
    def CharPrevW(self, emu, argv, ctx={}):
        '''
        LPWSTR CharPrevW(
            LPCWSTR lpszStart,
            LPCWSTR lpszCurrent
        );
        '''
        s,c = argv
        cw = 2
        while(s<c):
            n  = s + cw
            if (n>=c):
                break;
            s = n;

        return s

    @apihook('EnumWindows', argc=2)
    def EnumWindows(self, emu, argv, ctx={}):
        '''
        BOOL EnumWindows(
            WNDENUMPROC lpEnumFunc,
            LPARAM      lParam
        );
        '''
        lpEnumFunc, lParam = argv
        rv = 1

        return rv

    @apihook('GetSysColor', argc=1)
    def GetSysColor(self, emu, argv, ctx={}):
        '''
        DWORD GetSysColor(
            int nIndex
        );
        '''
        nIndex, = argv
        rv = 1

        return rv

    @apihook('GetParent', argc=1)
    def GetParent(self, emu, argv, ctx={}):
        '''
        HWND GetParent(
            HWND hWnd
        );
        '''
        return self.get_handle()

    @apihook('GetSysColorBrush', argc=1)
    def GetSysColorBrush(self, emu, argv, ctx={}):
        '''
        HBRUSH GetSysColorBrush(
            int nIndex
        );
        '''
        nIndex, = argv
        rv = 1

        return rv

    @apihook('GetWindowLong', argc=2)
    def GetWindowLong(self, emu, argv, ctx={}):
        '''
        LONG GetWindowLongA(
            HWND hWnd,
            int  nIndex
        );
        '''
        hWnd, nIndex, = argv
        rv = 2

        return rv

    @apihook('GetWindowLongW', argc=2)
    def GetWindowLongW(self, emu, argv, ctx={}):
        '''
        LONG GetWindowLongW(
            HWND hWnd,
            int  nIndex
        );
        '''
        hWnd, nIndex, = argv
        rv = 2

        return rv

    @apihook('SetWindowLong', argc=3)
    def SetWindowLong(self, emu, argv, ctx={}):
        """
        LONG SetWindowLongA(
          HWND hWnd,
          int  nIndex,
          LONG dwNewLong
        );
        """
        hWnd, nIndex, dwNewLong = argv
        if ((self.get_ptr_size() == 4 and nIndex == 0xfffffffc) or
            (self.get_ptr_size() == 8 and nIndex == 0xfffffffffffffffc)):
            self.wndprocs[hWnd] = dwNewLong

        return 1

    @apihook('SetWindowLongW', argc=3)
    def SetWindowLongW(self, emu, argv, ctx={}):
        """
        LONG SetWindowLongW(
          HWND hWnd,
          int  nIndex,
          LONG dwNewLong
        );
        """
        hWnd, nIndex, dwNewLong = argv
        if ((self.get_ptr_size() == 4 and nIndex == 0xfffffffc) or
            (self.get_ptr_size() == 8 and nIndex == 0xfffffffffffffffc)):
            self.wndprocs[hWnd] = dwNewLong

        return 1

    @apihook('SetWindowLongPtrW', argc=3)
    def SetWindowLongPtrW(self, emu, argv, ctx={}):
        """
        LONG_PTR SetWindowLongPtrW(
          HWND     hWnd,
          int      nIndex,
          LONG_PTR dwNewLong
        );
        """
        hWnd, nIndex, dwNewLong = argv
        if ((self.get_ptr_size() == 4 and nIndex == 0xfffffffc) or
            (self.get_ptr_size() == 8 and nIndex == 0xfffffffffffffffc)):
            self.wndprocs[hWnd] = dwNewLong

        return 1

    @apihook('DialogBoxParam', argc=5)
    def DialogBoxParam(self, emu, argv, ctx={}):
        '''
        INT_PTR DialogBoxParam(
            HINSTANCE hInstance,
            LPCSTR    lpTemplateName,
            HWND      hWndParent,
            DLGPROC   lpDialogFunc,
            LPARAM    dwInitParam
        );
        '''
        hInstance, lpTemplateName, hWndParent, lpDialogFunc, dwInitParam = argv
        rv = self.get_handle()
        cw = self.get_char_width(ctx)
        if lpTemplateName:
            tname = self.read_mem_string(lpTemplateName, cw)
            argv[1] = tname

        return rv

    @apihook('DialogBoxParamW', argc=5)
    def DialogBoxParamW(self, emu, argv, ctx={}):
        '''
        INT_PTR DialogBoxParamW(
            HINSTANCE hInstance,
            LPCWSTR    lpTemplateName,
            HWND      hWndParent,
            DLGPROC   lpDialogFunc,
            LPARAM    dwInitParam
        );
        '''
        hInstance, lpTemplateName, hWndParent, lpDialogFunc, dwInitParam = argv
        rv = self.get_handle()
        cw = 2
        if lpTemplateName:
            tname = self.read_mem_string(lpTemplateName, cw)
            argv[1] = tname

        return rv

    @apihook('CreateDialogIndirectParam', argc=5)
    def CreateDialogIndirectParam(self, emu, argv, ctx={}):
        '''
        HWND CreateDialogIndirectParam(
        HINSTANCE       hInstance,
        LPCDLGTEMPLATEA lpTemplate,
        HWND            hWndParent,
        DLGPROC         lpDialogFunc,
        LPARAM          dwInitParam
        );
        '''

        hnd, template, hnd_parent, func, param, = argv

        cb_args = (hnd_parent, windefs.WM_INITDIALOG, param, 0)
        self.setup_callback(func, cb_args, caller_argv=argv)
        return self.get_handle()

    @apihook('CreateDialogIndirectParamW', argc=5)
    def CreateDialogIndirectParamW(self, emu, argv, ctx={}):
        '''
        HWND CreateDialogIndirectParamW(
        HINSTANCE       hInstance,
        LPCDLGTEMPLATEW lpTemplate,
        HWND            hWndParent,
        DLGPROC         lpDialogFunc,
        LPARAM          dwInitParam
        );
        '''

        hnd, template, hnd_parent, func, param, = argv

        cb_args = (hnd_parent, windefs.WM_INITDIALOG, param, 0)
        self.setup_callback(func, cb_args, caller_argv=argv)
        return self.get_handle()

    @apihook('GetMenuInfo', argc=2)
    def GetMenuInfo(self, emu, argv, ctx={}):
        '''
        BOOL GetMenuInfo(
            HMENU,
            LPMENUINFO
        );
        '''
        return 1

    @apihook('GetProcessWindowStation', argc=0)
    def GetProcessWindowStation(self, emu, argv, ctx={}):
        '''
        HWINSTA GetProcessWindowStation();
        '''
        sta = self.sessman.get_current_station()
        return sta.get_handle()

    @apihook('LoadAccelerators', argc=2)
    def LoadAccelerators(self, emu, argv, ctx={}):
        '''
        HACCEL LoadAccelerators(
        HINSTANCE hInstance,
        LPCSTR    lpTableName
        );
        '''
        return self.get_handle()

    @apihook('LoadAcceleratorsW', argc=2)
    def LoadAcceleratorsW(self, emu, argv, ctx={}):
        '''
        HACCEL LoadAcceleratorsW(
        HINSTANCE hInstance,
        LPCWSTR    lpTableName
        );
        '''
        return self.get_handle()

    @apihook('IsWindowVisible', argc=1)
    def IsWindowVisible(self, emu, argv, ctx={}):
        '''
        BOOL IsWindowVisible(
        HWND hWnd
        );
        '''
        return True

    @apihook('BeginPaint', argc=2)
    def BeginPaint(self, emu, argv, ctx={}):
        '''
        HDC BeginPaint(
        HWND          hWnd,
        LPPAINTSTRUCT lpPaint
        );
        '''
        return self.get_handle()

    @apihook('LookupIconIdFromDirectory', argc=2)
    def LookupIconIdFromDirectory(self, emu, argv, ctx={}):
        '''
        int LookupIconIdFromDirectory(
        PBYTE presbits,
        BOOL  fIcon
        );
        '''
        return 1

    @apihook('GetActiveWindow', argc=0)
    def GetActiveWindow(self, emu, argv, ctx={}):
        '''
        HWND GetActiveWindow();
        '''
        return self.get_handle()

    @apihook('GetLastActivePopup', argc=1)
    def GetLastActivePopup(self, emu, argv, ctx={}):
        '''
        HWND GetLastActivePopup(
        HWND hWnd
        );
        '''
        hWnd, = argv
        return self.get_handle()

    @apihook('GetUserObjectInformation', argc=5)
    def GetUserObjectInformation(self, emu, argv, ctx={}):
        '''
        BOOL GetUserObjectInformation(
            HANDLE  hObj,
            int     nIndex,
            PVOID   pvInfo,
            DWORD   nLength,
            LPDWORD lpnLengthNeeded
        );
        '''
        obj, index, info, length, needed = argv

        if index == UOI_FLAGS:
            uoi = windefs.USEROBJECTFLAGS(emu.get_ptr_size())
            uoi.fInherit = 1
            uoi.dwFlags = 1

            if info:
                self.mem_write(info, uoi.get_bytes())

        return True

    @apihook('GetUserObjectInformationW', argc=5)
    def GetUserObjectInformationW(self, emu, argv, ctx={}):
        '''
        BOOL GetUserObjectInformationW(
            HANDLE  hObj,
            int     nIndex,
            PVOID   pvInfo,
            DWORD   nLength,
            LPDWORD lpnLengthNeeded
        );
        '''
        obj, index, info, length, needed = argv

        if index == UOI_FLAGS:
            uoi = windefs.USEROBJECTFLAGS(emu.get_ptr_size())
            uoi.fInherit = 1
            uoi.dwFlags = 1

            if info:
                self.mem_write(info, uoi.get_bytes())

        return True

    @apihook('LoadIcon', argc=2)
    def LoadIcon(self, emu, argv, ctx={}):
        '''
        HICON LoadIcon(
            HINSTANCE hInstance,
            LPCSTR    lpIconName
        );
        '''
        inst, name, = argv

        if name not in (IDI_APPLICATION, IDI_ASTERISK, IDI_ERROR, IDI_EXCLAMATION, IDI_HAND,
                        IDI_INFORMATION, IDI_QUESTION, IDI_SHIELD, IDI_WARNING, IDI_WINLOGO):
            return 0
        return 1

    @apihook('LoadIconW', argc=2)
    def LoadIconW(self, emu, argv, ctx={}):
        '''
        HICON LoadIconW(
            HINSTANCE hInstance,
            LPCWSTR    lpIconName
        );
        '''
        inst, name, = argv

        if name not in (IDI_APPLICATION, IDI_ASTERISK, IDI_ERROR, IDI_EXCLAMATION, IDI_HAND,
                        IDI_INFORMATION, IDI_QUESTION, IDI_SHIELD, IDI_WARNING, IDI_WINLOGO):
            return 0
        return 1

    @apihook('GetRawInputDeviceList', argc=3)
    def GetRawInputDeviceList(self, emu, argv, ctx={}):
        """
        UINT GetRawInputDeviceList(
          PRAWINPUTDEVICELIST pRawInputDeviceList,
          PUINT               puiNumDevices,
          UINT                cbSize
        );
        """
        pRawInputDeviceList, puiNumDevices, cbSize = argv
        num_devices = 4
        self.mem_write(puiNumDevices, num_devices.to_bytes(4, 'little'))
        return num_devices

    @apihook('GetNextDlgTabItem', argc=3)
    def GetNextDlgTabItem(self, emu, argv, ctx={}):
        """
        HWND GetNextDlgTabItem(
          HWND hDlg,
          HWND hCtl,
          BOOL bPrevious
        );
        """
        return 0

    @apihook('GetCaretPos', argc=1)
    def GetCaretPos(self, emu, argv, ctx={}):
        """
        BOOL GetCaretPos(
          LPPOINT lpPoint
        );
        """
        lpPoint = argv[0]
        point = windef.POINT(emu.get_ptr_size())
        point.x = 0
        point.y = 0
        self.mem_write(lpPoint, self.get_bytes(point))
        return 1

    @apihook('GetMonitorInfo', argc=2)
    def GetMonitorInfo(self, emu, argv, ctx={}):
        """
        BOOL GetMonitorInfo(
          HMONITOR      hMonitor,
          LPMONITORINFO lpmi
        );
        """
        hMonitor, lpmi = argv
        mi = windef.MONITORINFO(emu.get_ptr_size())
        mi = self.mem_cast(mi, lpmi)
        # just a stub for now
        self.mem_write(lpmi, self.get_bytes(mi))
        return 1

    @apihook('GetMonitorInfoW', argc=2)
    def GetMonitorInfoW(self, emu, argv, ctx={}):
        """
        BOOL GetMonitorInfoW(
          HMONITOR      hMonitor,
          LPMONITORINFO lpmi
        );
        """
        hMonitor, lpmi = argv
        mi = windef.MONITORINFO(emu.get_ptr_size())
        mi = self.mem_cast(mi, lpmi)
        # just a stub for now
        self.mem_write(lpmi, self.get_bytes(mi))
        return 1

    @apihook('EndPaint', argc=2)
    def EndPaint(self, emu, argv, ctx={}):
        """
        BOOL EndPaint(
          HWND              hWnd,
          const PAINTSTRUCT *lpPaint
        );
        """
        return 1

    @apihook('GetDlgCtrlID', argc=1)
    def GetDlgCtrlID(self, emu, argv, ctx={}):
        """
        int GetDlgCtrlID(
          HWND hWnd
        );
        """
        return 1

    @apihook('GetUpdateRect', argc=3)
    def GetUpdateRect(self, emu, argv, ctx={}):
        """
        BOOL GetUpdateRect(
          HWND   hWnd,
          LPRECT lpRect,
          BOOL   bErase
        );
        """
        return 0

    @apihook('GetAltTabInfo', argc=5)
    def GetAltTabInfo(self, emu, argv, ctx={}):
        """
        BOOL GetAltTabInfoA(
          HWND        hwnd,
          int         iItem,
          PALTTABINFO pati,
          LPSTR       pszItemText,
          UINT        cchItemText
        );
        """
        return 0

    @apihook('GetAltTabInfoW', argc=5)
    def GetAltTabInfoW(self, emu, argv, ctx={}):
        """
        BOOL GetAltTabInfoW(
          HWND        hwnd,
          int         iItem,
          PALTTABINFO pati,
          LPWSTR      pszItemText,
          UINT        cchItemText
        );
        """
        return 0

    @apihook('GetUpdateRgn', argc=3)
    def GetUpdateRgn(self, emu, argv, ctx={}):
        """
        int GetUpdateRgn(
          HWND hWnd,
          HRGN hRgn,
          BOOL bErase
        );
        """
        return 0

    @apihook('FlashWindow', argc=2)
    def FlashWindow(self, emu, argv, ctx={}):
        """
        BOOL FlashWindow(
          HWND hWnd,
          BOOL bInvert
        );
        """
        return 1

    @apihook('IsClipboardFormatAvailable', argc=1)
    def IsClipboardFormatAvailable(self, emu, argv, ctx={}):
        """
        BOOL IsClipboardFormatAvailable(
          UINT format
        );
        """
        return 0

    @apihook('OpenClipboard', argc=1)
    def OpenClipboard(self, emu, argv, ctx={}):
        """
        BOOL OpenClipboard(
          HWND hWndNewOwner
        );
        """
        hWndNewOwner, = argv
        # Return TRUE to indicate the clipboard was opened successfully
        return 1

    @apihook('CloseClipboard', argc=0)
    def CloseClipboard(self, emu, argv, ctx={}):
        """
        BOOL CloseClipboard();
        """
        # Return TRUE to indicate the clipboard was closed successfully
        return 1

    @apihook('EmptyClipboard', argc=0)
    def EmptyClipboard(self, emu, argv, ctx={}):
        """
        BOOL EmptyClipboard();
        """
        # Return TRUE to indicate the clipboard was emptied successfully
        return 1

    @apihook('SetClipboardData', argc=2)
    def SetClipboardData(self, emu, argv, ctx={}):
        """
        HANDLE SetClipboardData(
          UINT   uFormat,
          HANDLE hMem
        );
        """
        uFormat, hMem = argv
        # Return the handle to indicate success
        return hMem if hMem else self.get_handle()

    @apihook('GetClipboardData', argc=1)
    def GetClipboardData(self, emu, argv, ctx={}):
        """
        HANDLE GetClipboardData(
          UINT uFormat
        );
        """
        uFormat, = argv
        # Return NULL to indicate no data available
        return 0

    @apihook('IsWindow', argc=1)
    def IsWindow(self, emu, argv, ctx={}):
        """
        BOOL IsWindow(
            HWND hWnd
        );
        """
        hnd, = argv

        return True

    @apihook('EnableWindow', argc=2)
    def EnableWindow(self, emu, argv, ctx={}):
        """
        BOOL EnableWindow(
        HWND hWnd,
        BOOL bEnable
        );
        """
        hnd, bEnable = argv

        return False

    @apihook('CharLowerBuff', argc=2)
    def CharLowerBuff(self, emu, argv, ctx={}):
        """
        DWORD CharLowerBuffA(
            LPSTR lpsz,
            DWORD cchLength
        );
        """
        _str, cchLength = argv
        cw = self.get_char_width(ctx)
        val = self.read_mem_string(_str, cw, max_chars=cchLength)
        argv[0] = val
        argv[1] = cchLength
        self.write_mem_string(val.lower(), _str, cw)
        return cchLength

    @apihook('CharLowerBuffW', argc=2)
    def CharLowerBuffW(self, emu, argv, ctx={}):
        """
        DWORD CharLowerBuffW(
            LPWSTR lpsz,
            DWORD cchLength
        );
        """
        _str, cchLength = argv
        cw = 2
        val = self.read_mem_string(_str, cw, max_chars=cchLength)
        argv[0] = val
        argv[1] = cchLength
        self.write_mem_string(val.lower(), _str, cw)
        return cchLength

    @apihook('CharUpperBuff', argc=2)
    def CharUpperBuff(self, emu, argv, ctx={}):
        """
        DWORD CharUpperBuffA(
            LPSTR lpsz,
            DWORD cchLength
        );
        """
        _str, cchLength = argv
        cw = self.get_char_width(ctx)
        val = self.read_mem_string(_str, cw, max_chars=cchLength)
        argv[0] = val
        argv[1] = cchLength
        self.write_mem_string(val.upper(), _str, cw)
        return cchLength

    @apihook('CharUpperBuffW', argc=2)
    def CharUpperBuffW(self, emu, argv, ctx={}):
        """
        DWORD CharUpperBuffW(
            LPWSTR lpsz,
            DWORD cchLength
        );
        """
        _str, cchLength = argv
        cw = 2
        val = self.read_mem_string(_str, cw, max_chars=cchLength)
        argv[0] = val
        argv[1] = cchLength
        self.write_mem_string(val.upper(), _str, cw)
        return cchLength

    @apihook('CharLower', argc=1)
    def CharLower(self, emu, argv, ctx={}):
        """
        LPSTR CharLowerA(
            LPSTR lpsz
        );
        """
        _str, = argv
        cw = self.get_char_width(ctx)
        bits = _str.bit_length()
        if bits <= 16:
            if cw == 1:
                val = chr(_str).lower().encode('ascii')
            else:
                val = chr(_str).lower().encode('utf-16le')
            return int.from_bytes(val, byteorder='little')
        else:
            val = self.read_mem_string(_str, cw)
            self.write_mem_string(val.lower(), _str, cw)
            return _str

    @apihook('CharLowerW', argc=1)
    def CharLowerW(self, emu, argv, ctx={}):
        """
        LPWSTR CharLowerW(
            LPWSTR lpsz
        );
        """
        _str, = argv
        cw = 2
        bits = _str.bit_length()
        if bits <= 16:
            val = chr(_str).lower().encode('utf-16le')
            return int.from_bytes(val, byteorder='little')
        else:
            val = self.read_mem_string(_str, cw)
            self.write_mem_string(val.lower(), _str, cw)
            return _str

    @apihook('CharUpper', argc=1)
    def CharUpper(self, emu, argv, ctx={}):
        """
        LPSTR CharUpperA(
            LPSTR lpsz
        );
        """
        _str, = argv
        cw = self.get_char_width(ctx)
        bits = _str.bit_length()
        if bits <= 16:
            if cw == 1:
                val = chr(_str).upper().encode('ascii')
            else:
                val = chr(_str).upper().encode('utf-16le')
            return int.from_bytes(val, byteorder='little')
        else:
            val = self.read_mem_string(_str, cw)
            self.write_mem_string(val.upper(), _str, cw)
            return _str

    @apihook('CharUpperW', argc=1)
    def CharUpperW(self, emu, argv, ctx={}):
        """
        LPWSTR CharUpperW(
            LPWSTR lpsz
        );
        """
        _str, = argv
        cw = 2
        bits = _str.bit_length()
        if bits <= 16:
            val = chr(_str).upper().encode('utf-16le')
            return int.from_bytes(val, byteorder='little')
        else:
            val = self.read_mem_string(_str, cw)
            self.write_mem_string(val.upper(), _str, cw)
            return _str

    @apihook('SetTimer', argc=4)
    def SetTimer(self, emu, argv, ctx={}):
        """
        UINT_PTR SetTimer(
          HWND      hWnd,
          UINT_PTR  nIDEvent,
          UINT      uElapse,
          TIMERPROC lpTimerFunc
        );
        """
        self.timer_count += 1

        return self.get_handle()

    @apihook('KillTimer', argc=2)
    def KillTimer(self, emu, argv, ctx={}):
        """
        BOOL KillTimer(
          HWND     hWnd,
          UINT_PTR uIDEvent
        );
        """
        self.timer_count -= 1

        return True

    @apihook('OpenDesktop', argc=4)
    def OpenDesktop(self, emu, argv, ctx={}):
        """
        HDESK OpenDesktopA(
            LPCSTR      lpszDesktop,
            DWORD       dwFlags,
            BOOL        fInherit,
            ACCESS_MASK dwDesiredAccess
        );
        """
        lpszDesktop, dwFlags, fInherit, dwDesiredAccess = argv
        cw = self.get_char_width(ctx)
        desktop = self.read_mem_string(lpszDesktop, cw)
        argv[0] = desktop
        return self.get_handle()

    @apihook('OpenDesktopW', argc=4)
    def OpenDesktopW(self, emu, argv, ctx={}):
        """
        HDESK OpenDesktopW(
            LPCWSTR     lpszDesktop,
            DWORD       dwFlags,
            BOOL        fInherit,
            ACCESS_MASK dwDesiredAccess
        );
        """
        lpszDesktop, dwFlags, fInherit, dwDesiredAccess = argv
        cw = 2
        desktop = self.read_mem_string(lpszDesktop, cw)
        argv[0] = desktop
        return self.get_handle()

    @apihook('SetThreadDesktop', argc=1)
    def SetThreadDesktop(self, emu, argv, ctx={}):
        """
        BOOL SetThreadDesktop(
            HDESK hDesktop
        );
        """
        return 0

    @apihook('GetKeyboardLayoutList', argc=2)
    def GetKeyboardLayoutList(self, emu, argv, ctx={}):
        """
        int GetKeyboardLayoutList(
          int nBuff,
          HKL *lpList
        );
        """
        nBuff, lpList = argv
        if not nBuff:
            # number of items
            return 1
        locale = 0x409      # English - United States
        self.mem_write(lpList, locale.to_bytes(2, 'little'))
        self.mem_write(lpList + 4, locale.to_bytes(2, 'little'))

        return 1

    @apihook("GetKBCodePage", argc=0)
    def GetKBCodePage(self, emu, argv, ctx={}):
        '''
        INT GetKBCodePage();
        '''
        # >>> ctypes.windll.user32.GetKBCodePage()
        # 437
        # https://docs.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
        return 437 # OEM United States

    @apihook("GetClipboardViewer", argc=0)
    def GetClipboardViewer(self, emu, argv, ctx={}):
        '''
        HWND GetClipboardViewer();
        '''
        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook("GetClipboardOwner", argc=0)
    def GetClipboardOwner(self, emu, argv, ctx={}):
        '''
        HWND GetClipboardOwner();
        '''
        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook("GetMenuCheckMarkDimensions", argc=0)
    def GetMenuCheckMarkDimensions(self, emu, argv, ctx={}):
        '''
        LONG GetMenuCheckMarkDimensions();
        '''
        # >>> ctypes.windll.user32.GetMenuCheckMarkDimensions()
        # 983055
        return 983055

    @apihook("GetOpenClipboardWindow", argc=0)
    def GetOpenClipboardWindow(self, emu, argv, ctx={}):
        '''
        HWND GetOpenClipboardWindow();
        '''
        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook("GetFocus", argc=0)
    def GetFocus(self, emu, argv, ctx={}):
        '''
        HWND GetFocus();
        '''
        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook("GetCursor", argc=0)
    def GetCursor(self, emu, argv, ctx={}):
        '''
        HCURSOR GetCursor();
        '''
        hnd = 0

        desk = self.sessman.get_current_desktop()
        window = desk.get_desktop_window()
        hnd = window.get_handle()

        return hnd

    @apihook("GetClipboardSequenceNumber", argc=0)
    def GetClipboardSequenceNumber(self, emu, argv, ctx={}):
        '''
        DWORD GetClipboardSequenceNumber();
        '''
        # >>> ctypes.windll.user32.GetClipboardSequenceNumber()
        # 295
        return 295

    @apihook("GetCaretBlinkTime", argc=0)
    def GetCaretBlinkTime(self, emu, argv, ctx={}):
        '''
        UINT GetCaretBlinkTime();
        '''
        # >>> ctypes.windll.user32.GetCaretBlinkTime()
        # 530
        return 530

    @apihook("GetDoubleClickTime", argc=0)
    def GetDoubleClickTime(self, emu, argv, ctx={}):
        '''
        UINT GetDoubleClickTime();
        '''
        # >>> ctypes.windll.user32.GetDoubleClickTime()
        # 500
        return 500

    @apihook('SystemParametersInfo', argc=4)
    def SystemParametersInfo(self, emu, argv, ctx={}):
        '''
        BOOL SystemParametersInfoA(
            UINT  uiAction,
            UINT  uiParam,
            PVOID pvParam,
            UINT  fWinIni
        );
        '''
        uiAction, uiParam, pvParam, fWinIni = argv
        
        # Just return success for most queries
        # In a full implementation, we would handle specific uiAction values
        return 1

    @apihook('CreateDialogParam', argc=5)
    def CreateDialogParam(self, emu, argv, ctx={}):
        '''
        HWND CreateDialogParamA(
            HINSTANCE hInstance,
            LPCSTR    lpTemplateName,
            HWND      hWndParent,
            DLGPROC   lpDialogFunc,
            LPARAM    dwInitParam
        );
        '''
        hInstance, lpTemplateName, hWndParent, lpDialogFunc, dwInitParam = argv
        
        cw = self.get_char_width(ctx)
        # Check if lpTemplateName is a resource ID (MAKEINTRESOURCE)
        # If high-order word is 0, it's a resource ID, not a pointer
        if lpTemplateName and lpTemplateName > 0xFFFF:
            tname = self.read_mem_string(lpTemplateName, cw)
            argv[1] = tname
        else:
            argv[1] = 'RESOURCE_ID_%d' % lpTemplateName
        
        return self.get_handle()

    @apihook('CreateDialogParamW', argc=5)
    def CreateDialogParamW(self, emu, argv, ctx={}):
        '''
        HWND CreateDialogParamW(
            HINSTANCE hInstance,
            LPCWSTR   lpTemplateName,
            HWND      hWndParent,
            DLGPROC   lpDialogFunc,
            LPARAM    dwInitParam
        );
        '''
        hInstance, lpTemplateName, hWndParent, lpDialogFunc, dwInitParam = argv
        
        cw = 2
        # Check if lpTemplateName is a resource ID (MAKEINTRESOURCE)
        # If high-order word is 0, it's a resource ID, not a pointer
        if lpTemplateName and lpTemplateName > 0xFFFF:
            tname = self.read_mem_string(lpTemplateName, cw)
            argv[1] = tname
        else:
            argv[1] = 'RESOURCE_ID_%d' % lpTemplateName
        
        return self.get_handle()

    @apihook('SetRectEmpty', argc=1)
    def SetRectEmpty(self, emu, argv, ctx={}):
        """
        BOOL SetRectEmpty(
          LPRECT lprc
        );
        """
        lprc, = argv
        if lprc:
            # Set all members of RECT to 0 (left, top, right, bottom)
            # RECT is 16 bytes (4 LONG values)
            self.mem_write(lprc, b'\x00' * 16)
        return 1  # TRUE for success

    @apihook('EnumDisplayMonitors', argc=4)
    def EnumDisplayMonitors(self, emu, argv, ctx={}):
        """
        BOOL EnumDisplayMonitors(
          HDC             hdc,
          LPCRECT         lprcClip,
          MONITORENUMPROC lpfnEnum,
          LPARAM          dwData
        );
        """
        hdc, lprcClip, lpfnEnum, dwData = argv
        # For a single-monitor emulated environment, we just return TRUE
        # without calling the callback, or we could call it once for the primary monitor
        # For simplicity, just return TRUE indicating success
        return 1  # TRUE

    @apihook('PostThreadMessageA', argc=4)
    def PostThreadMessageA(self, emu, argv, ctx={}):
        """
        BOOL PostThreadMessageA(
          DWORD  idThread,
          UINT   Msg,
          WPARAM wParam,
          LPARAM lParam
        );
        """
        idThread, Msg, wParam, lParam = argv
        # Return TRUE to indicate the message was posted successfully
        return 1

    @apihook('PostThreadMessageW', argc=4)
    def PostThreadMessageW(self, emu, argv, ctx={}):
        """
        BOOL PostThreadMessageW(
          DWORD  idThread,
          UINT   Msg,
          WPARAM wParam,
          LPARAM lParam
        );
        """
        idThread, Msg, wParam, lParam = argv
        return 1

    @apihook('PostMessageA', argc=4)
    def PostMessageA(self, emu, argv, ctx={}):
        """
        BOOL PostMessageA(
          HWND   hWnd,
          UINT   Msg,
          WPARAM wParam,
          LPARAM lParam
        );
        """
        hWnd, Msg, wParam, lParam = argv
        return 1

    @apihook('PostMessageW', argc=4)
    def PostMessageW(self, emu, argv, ctx={}):
        """
        BOOL PostMessageW(
          HWND   hWnd,
          UINT   Msg,
          WPARAM wParam,
          LPARAM lParam
        );
        """
        hWnd, Msg, wParam, lParam = argv
        return 1

    @apihook('GetInputState', argc=0)
    def GetInputState(self, emu, argv, ctx={}):
        """
        BOOL GetInputState();
        """
        # Returns FALSE - no mouse/keyboard input pending in emulation
        return 0

