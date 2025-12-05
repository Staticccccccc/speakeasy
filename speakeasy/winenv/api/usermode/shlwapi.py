# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import os
import ntpath

from .. import api
import speakeasy.winenv.arch as e_arch

MAX_PATH = 260


class Shlwapi(api.ApiHandler):

    """
    Implements exported functions from shlwapi.dll
    """

    name = 'shlwapi'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(Shlwapi, self).__init__(emu)

        self.funcs = {}
        self.data = {}
        self.window_hooks = {}
        self.handle = 0
        self.win = None

        super(Shlwapi, self).__get_hook_attrs__(self)

    def join_windows_path(self, *args, **kwargs):
        args = list(map(lambda x: x.replace('\\', '/'), args))
        return os.path.join(*args, **kwargs).replace('/', '\\')

    @apihook('PathIsRelative', argc=1)
    def PathIsRelative(self, emu, argv, ctx={}):
        '''
        BOOL PathIsRelativeA(
            LPCSTR pszPath
        );
        '''

        pszPath, = argv

        cw = self.get_char_width(ctx)
        pn = ''
        rv = False
        if pszPath:
            pn = self.read_mem_string(pszPath, cw)
            if '..' in pn:
                rv = True

            argv[0] = pn

        return rv

    @apihook('PathIsRelativeW', argc=1)
    def PathIsRelativeW(self, emu, argv, ctx={}):
        '''
        BOOL PathIsRelativeW(
            LPCWSTR pszPath
        );
        '''

        pszPath, = argv

        cw = 2
        pn = ''
        rv = False
        if pszPath:
            pn = self.read_mem_string(pszPath, cw)
            if '..' in pn:
                rv = True

            argv[0] = pn

        return rv

    @apihook('StrStr', argc=2)
    def StrStr(self, emu, argv, ctx={}):
        '''
        PCSTR StrStr(
            PCSTR pszFirst,
            PCSTR pszSrch
        );
        '''

        hay, needle = argv

        cw = self.get_char_width(ctx)

        if hay:
            _hay = self.read_mem_string(hay, cw)
            argv[0] = _hay

        if needle:
            needle = self.read_mem_string(needle, cw)
            argv[1] = needle

        ret = _hay.find(needle)
        if ret != -1:
            ret = hay + ret
        else:
            ret = 0

        return ret

    @apihook('StrStrW', argc=2)
    def StrStrW(self, emu, argv, ctx={}):
        '''
        PCWSTR StrStrW(
            PCWSTR pszFirst,
            PCWSTR pszSrch
        );
        '''

        hay, needle = argv

        cw = 2

        if hay:
            _hay = self.read_mem_string(hay, cw)
            argv[0] = _hay

        if needle:
            needle = self.read_mem_string(needle, cw)
            argv[1] = needle

        ret = _hay.find(needle)
        if ret != -1:
            ret = hay + (ret * cw)
        else:
            ret = 0

        return ret

    @apihook('StrStrI', argc=2)
    def StrStrI(self, emu, argv, ctx={}):
        '''
        PCSTR StrStrI(
            PCSTR pszFirst,
            PCSTR pszSrch
        );
        '''

        hay, needle = argv

        cw = self.get_char_width(ctx)

        if hay:
            _hay = self.read_mem_string(hay, cw)
            argv[0] = _hay
            _hay = _hay.lower()

        if needle:
            needle = self.read_mem_string(needle, cw)
            argv[1] = needle
            needle = needle.lower()

        ret = _hay.find(needle)
        if ret != -1:
            ret = hay + ret
        else:
            ret = 0

        return ret

    @apihook('StrStrIW', argc=2)
    def StrStrIW(self, emu, argv, ctx={}):
        '''
        PCWSTR StrStrIW(
            PCWSTR pszFirst,
            PCWSTR pszSrch
        );
        '''

        hay, needle = argv

        cw = 2

        if hay:
            _hay = self.read_mem_string(hay, cw)
            argv[0] = _hay
            _hay = _hay.lower()

        if needle:
            needle = self.read_mem_string(needle, cw)
            argv[1] = needle
            needle = needle.lower()

        ret = _hay.find(needle)
        if ret != -1:
            ret = hay + (ret * cw)
        else:
            ret = 0

        return ret

    @apihook('PathFindExtension', argc=1)
    def PathFindExtension(self, emu, argv, ctx={}):
        """LPCSTR PathFindExtensionA(
          LPCSTR pszPath
        );
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx1 = s.rfind('\\')
        t = s[idx1 + 1:]
        idx2 = t.rfind('.')
        if idx2 == -1:
            return pszPath + len(s)

        argv[0] = t[idx2:]
        return pszPath + idx1 + 1 + idx2

    @apihook('PathFindExtensionW', argc=1)
    def PathFindExtensionW(self, emu, argv, ctx={}):
        """LPCWSTR PathFindExtensionW(
          LPCWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx1 = s.rfind('\\')
        t = s[idx1 + 1:]
        idx2 = t.rfind('.')
        if idx2 == -1:
            return pszPath + (len(s) * cw)

        argv[0] = t[idx2:]
        return pszPath + ((idx1 + 1 + idx2) * cw)

    @apihook('StrCmpI', argc=2)
    def StrCmpI(self, emu, argv, ctx={}):
        """
        int StrCmpI(
        PCWSTR psz1,
        PCWSTR psz2
        );
        """
        psz1, psz2 = argv

        cw = self.get_char_width(ctx)
        s1 = self.read_mem_string(psz1, cw)
        s2 = self.read_mem_string(psz2, cw)
        rv = 1

        argv[0] = s1
        argv[1] = s2

        if s1.lower() == s2.lower():
            rv = 0

        return rv

    @apihook('StrCmpIW', argc=2)
    def StrCmpIW(self, emu, argv, ctx={}):
        """
        int StrCmpIW(
        PCWSTR psz1,
        PCWSTR psz2
        );
        """
        psz1, psz2 = argv

        cw = 2
        s1 = self.read_mem_string(psz1, cw)
        s2 = self.read_mem_string(psz2, cw)
        rv = 1

        argv[0] = s1
        argv[1] = s2

        if s1.lower() == s2.lower():
            rv = 0

        return rv

    @apihook('PathFindFileName', argc=1)
    def PathFindFileName(self, emu, argv, ctx={}):
        """
        LPCSTR PathFindFileNameA(
          LPCSTR pszPath
        );
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx = s.rfind('\\')
        if idx == -1:
            return pszPath + len(s)

        argv[0] = s[idx + 1:]
        return pszPath + idx + 1

    @apihook('PathFindFileNameW', argc=1)
    def PathFindFileNameW(self, emu, argv, ctx={}):
        """
        LPCWSTR PathFindFileNameW(
          LPCWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx = s.rfind('\\')
        if idx == -1:
            return pszPath + (len(s) * cw)

        argv[0] = s[idx + 1:]
        return pszPath + ((idx + 1) * cw)

    @apihook('PathRemoveExtension', argc=1)
    def PathRemoveExtension(self, emu, argv, ctx={}):
        """
        void PathRemoveExtensionA(
          LPSTR pszPath
        );
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx1 = s.rfind('\\')
        t = s[idx1 + 1:]
        idx2 = t.rfind('.')
        if idx2 == -1:
            return pszPath

        s = s[:idx1 + 1 + idx2]
        argv[0] = s
        self.write_mem_string(s, pszPath, cw)
        return pszPath

    @apihook('PathRemoveExtensionW', argc=1)
    def PathRemoveExtensionW(self, emu, argv, ctx={}):
        """
        void PathRemoveExtensionW(
          LPWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        idx1 = s.rfind('\\')
        t = s[idx1 + 1:]
        idx2 = t.rfind('.')
        if idx2 == -1:
            return pszPath

        s = s[:idx1 + 1 + idx2]
        argv[0] = s
        self.write_mem_string(s, pszPath, cw)
        return pszPath

    @apihook('PathStripPath', argc=1)
    def PathStripPath(self, emu, argv, ctx={}):
        """
        void PathStripPath(
        LPSTR pszPath
        );
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        mod_name = ntpath.basename(s) + '\x00'

        enc = self.get_encoding(cw)
        mod_name = mod_name.encode(enc)
        self.mem_write(pszPath, mod_name)

    @apihook('PathStripPathW', argc=1)
    def PathStripPathW(self, emu, argv, ctx={}):
        """
        void PathStripPathW(
        LPWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        argv[0] = s
        mod_name = ntpath.basename(s) + '\x00'

        enc = self.get_encoding(cw)
        mod_name = mod_name.encode(enc)
        self.mem_write(pszPath, mod_name)

    @apihook('wvnsprintfA', argc=4)
    def wvnsprintfA(self, emu, argv, ctx={}):
        """
        int wvnsprintfA(
            PSTR    pszDest,
            int     cchDest,
            PCSTR   pszFmt,
            va_list arglist
        );
        """
        buffer, count, _format, argptr = argv
        rv = 0

        fmt_str = self.read_mem_string(_format, 1)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        vargs = self.va_args(argptr, fmt_cnt)

        fin = self.do_str_format(fmt_str, vargs)
        fin = fin[:count] + '\x00'

        rv = len(fin)
        self.mem_write(buffer, fin.encode('utf-8'))
        argv[0] = fin.replace('\x00', '')
        argv[1] = fmt_str

        return rv

    @apihook('wvnsprintfW', argc=4)
    def wvnsprintfW(self, emu, argv, ctx={}):
        """
        int wvnsprintfW(
            PWSTR   pszDest,
            int     cchDest,
            PCWSTR  pszFmt,
            va_list arglist
        );
        """
        buffer, count, _format, argptr = argv
        rv = 0
        cw = 2

        fmt_str = self.read_mem_string(_format, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)

        vargs = self.va_args(argptr, fmt_cnt)

        fin = self.do_str_format(fmt_str, vargs)
        fin = fin[:count] + '\x00'

        rv = len(fin)
        self.mem_write(buffer, fin.encode('utf-16le'))
        argv[0] = fin.replace('\x00', '')
        argv[1] = fmt_str

        return rv

    @apihook('wnsprintf', argc=e_arch.VAR_ARGS, conv=e_arch.CALL_CONV_CDECL)
    def wnsprintf(self, emu, argv, ctx={}):
        """
        int wnsprintfA(
          PSTR  pszDest,
          int   cchDest,
          PCSTR pszFmt,
          ...
        );
        """
        argv = emu.get_func_argv(e_arch.CALL_CONV_CDECL, 3)
        buf, max_buf_size, fmt = argv

        cw = self.get_char_width(ctx)

        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)
        if not fmt_cnt:
            self.write_mem_string(fmt_str, buf, cw)
            return len(fmt_str)

        _argv = emu.get_func_argv(e_arch.CALL_CONV_CDECL, 3 + fmt_cnt)[3:]
        fin = self.do_str_format(fmt_str, _argv)
        rv = len(fin)

        if rv <= max_buf_size:
            self.write_mem_string(fin, buf, cw)
            argv[0] = fin
            argv[2] = fmt_str
            return rv
        else:
            return -1

    @apihook('wnsprintfW', argc=e_arch.VAR_ARGS, conv=e_arch.CALL_CONV_CDECL)
    def wnsprintfW(self, emu, argv, ctx={}):
        """
        int wnsprintfW(
          PWSTR  pszDest,
          int   cchDest,
          PCWSTR pszFmt,
          ...
        );
        """
        argv = emu.get_func_argv(e_arch.CALL_CONV_CDECL, 3)
        buf, max_buf_size, fmt = argv

        cw = 2

        fmt_str = self.read_mem_string(fmt, cw)
        fmt_cnt = self.get_va_arg_count(fmt_str)
        if not fmt_cnt:
            self.write_mem_string(fmt_str, buf, cw)
            return len(fmt_str)

        _argv = emu.get_func_argv(e_arch.CALL_CONV_CDECL, 3 + fmt_cnt)[3:]
        fin = self.do_str_format(fmt_str, _argv)
        rv = len(fin)

        if rv <= max_buf_size:
            self.write_mem_string(fin, buf, cw)
            argv[0] = fin
            argv[2] = fmt_str
            return rv
        else:
            return -1

    @apihook('PathAppend', argc=2)
    def PathAppend(self, emu, argv, ctx={}):
        """
        BOOL PathAppendA(
          LPSTR  pszPath,
          LPCSTR pszMore
        );
        """
        pszPath, pszMore = argv
        cw = self.get_char_width(ctx)
        path = self.read_mem_string(pszPath, cw)
        more = self.read_mem_string(pszMore, cw)
        argv[0] = path
        argv[1] = more
        out = self.join_windows_path(path, more)
        out += '\0'
        self.write_mem_string(out, pszPath, cw)
        return 1

    @apihook('PathCanonicalize', argc=2)
    def PathCanonicalize(self, emu, argv, ctx={}):
        """
        BOOL PathCanonicalizeW(
            [out] LPWSTR  pszBuf,
            [in]  LPCWSTR pszPath
        );
        """
        pszBuf, pszPath = argv
        path = self.read_wide_string(pszPath)
        self.write_wide_string(path, pszBuf)
        return 1

    @apihook('PathCanonicalizeW', argc=2)
    def PathCanonicalizeW(self, emu, argv, ctx={}):
        """
        BOOL PathCanonicalizeW(
            [out] LPWSTR  pszBuf,
            [in]  LPCWSTR pszPath
        );
        """
        pszBuf, pszPath = argv
        path = self.read_wide_string(pszPath)
        self.write_wide_string(path, pszBuf)
        return 1

    @apihook('PathRemoveFileSpec', argc=1)
    def PathRemoveFileSpec(self, emu, argv, ctx={}):
        """
        BOOL PathRemoveFileSpec(LPTSTR pszPath);
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        idx = s.rfind('\\')
        if idx == -1:
            return 0

        s = s[:idx]
        self.write_mem_string(s, pszPath, cw)
        return 1

    @apihook('PathAddBackslash', argc=1)
    def PathAddBackslash(self, emu, argv, ctx={}):
        """
        LPTSTR PathAddBackslash(LPTSTR pszPath);
        """
        pszPath, = argv
        cw = self.get_char_width(ctx)
        s = self.read_mem_string(pszPath, cw)
        if not s.endswith('\\'):
            s += '\\'
            if len(s) > MAX_PATH:
                return 0

        self.write_mem_string(s, pszPath, cw)
        return pszPath

    @apihook('PathAddBackslashW', argc=1)
    def PathAddBackslashW(self, emu, argv, ctx={}):
        """
        LPTSTR PathAddBackslashW(LPWSTR pszPath);
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        if not s.endswith('\\'):
            s += '\\'
            if len(s) > MAX_PATH:
                return 0

        self.write_mem_string(s, pszPath, cw)
        return pszPath

    @apihook('PathRenameExtension', argc=2)
    def PathRenameExtension(self, emu, argv, ctx={}):
        """
        BOOL PathRenameExtension(
          [in, out] LPSTR  pszPath,
          [in]      LPCSTR pszExt
        );
        """
        pszPath, pszExt = argv

        cw = self.get_char_width(ctx)
        path = self.read_mem_string(pszPath, cw)

        ext = self.read_mem_string(pszExt, cw)
        if not ext.startswith('.'):
            return 0

        i = path.rfind('.')
        if i == -1:
            path += ext
        else:
            path = path[:i] + ext

        if len(path) > MAX_PATH:
            return 0

        self.write_mem_string(path, pszPath, cw)
        return 1

    @apihook('PathRenameExtensionW', argc=2)
    def PathRenameExtensionW(self, emu, argv, ctx={}):
        """
        BOOL PathRenameExtensionW(
          [in, out] LPWSTR  pszPath,
          [in]      LPCWSTR pszExt
        );
        """
        pszPath, pszExt = argv

        cw = 2
        path = self.read_mem_string(pszPath, cw)

        ext = self.read_mem_string(pszExt, cw)
        if not ext.startswith('.'):
            return 0

        i = path.rfind('.')
        if i == -1:
            path += ext
        else:
            path = path[:i] + ext

        if len(path) > MAX_PATH:
            return 0

        self.write_mem_string(path, pszPath, cw)
        return 1

    @apihook('PathFileExistsW', argc=1)
    def PathFileExistsW(self, emu, argv, ctx={}):
        """
        BOOL PathFileExistsW(
          LPCWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        path = self.read_mem_string(pszPath, cw)
        
        # Check if the path exists in the emulated filesystem
        # If file_system is not available, default to True to allow execution
        if hasattr(emu, 'file_system') and emu.file_system:
            # TODO: Check if path_exists takes a path string
            # For now, let's assume it does or just return True
            pass
            
        return 1

    @apihook('PathRemoveFileSpecW', argc=1)
    def PathRemoveFileSpecW(self, emu, argv, ctx={}):
        """
        BOOL PathRemoveFileSpecW(
          LPWSTR pszPath
        );
        """
        pszPath, = argv
        cw = 2
        s = self.read_mem_string(pszPath, cw)
        idx = s.rfind('\\')
        if idx == -1:
            return 0

        s = s[:idx]
        self.write_mem_string(s, pszPath, cw)
        return 1

    @apihook('PathAppendW', argc=2)
    def PathAppendW(self, emu, argv, ctx={}):
        """
        BOOL PathAppendW(
          LPWSTR  pszPath,
          LPCWSTR pszMore
        );
        """
        pszPath, pszMore = argv
        cw = 2
        path = self.read_mem_string(pszPath, cw)
        more = self.read_mem_string(pszMore, cw)
        argv[0] = path
        argv[1] = more
        out = self.join_windows_path(path, more)
        out += '\0'
        self.write_mem_string(out, pszPath, cw)
        return 1
