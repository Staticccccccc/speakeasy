# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

from .. import api


class GDI32(api.ApiHandler):

    """
    Implements exported functions from gdi32.dll
    """

    name = 'gdi32'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(GDI32, self).__init__(emu)

        self.funcs = {}
        self.data = {}
        self.handle = 0
        self.count = 0
        super(GDI32, self).__get_hook_attrs__(self)

    def get_handle(self):
        self.handle += 4
        hnd = self.handle
        return hnd

    @apihook('CreateBitmap', argc=5)
    def CreateBitmap(self, emu, argv, ctx={}):
        '''
        HBITMAP CreateBitmap(
            int        nWidth,
            int        nHeight,
            UINT       nPlanes,
            UINT       nBitCount,
            const VOID *lpBits
        );
        '''
        return self.get_handle()

    @apihook('MoveToEx', argc=1)
    def MoveToEx(self, emu, argv, ctx={}):
        """
        BOOL MoveToEx(
          HDC     hdc,
          int     x,
          int     y,
          LPPOINT lppt
        );
        """
        return 1

    @apihook('LineTo', argc=1)
    def LineTo(self, emu, argv, ctx={}):
        """
        BOOL LineTo(
          HDC hdc,
          int x,
          int y
        )
        """
        return 1

    @apihook('GetStockObject', argc=1)
    def GetStockObject(self, emu, argv, ctx={}):
        """
        HGDIOBJ GetStockObject(
            int i
        );
        """
        return 0

    @apihook('GetMapMode', argc=1)
    def GetMapMode(self, emu, argv, ctx={}):
        """
        int GetMapMode(
            HDC hdc
        );
        """
        return 1

    @apihook('GetDeviceCaps', argc=2)
    def GetDeviceCaps(self, emu, argv, ctx={}):
        """
        int GetDeviceCaps(
            HDC hdc,
            int index
        );
        """
        return 16

    @apihook('GetSystemPaletteEntries', argc=4)
    def GetSystemPaletteEntries(self, emu, argv, ctx={}):
        """
        UINT GetSystemPaletteEntries(
          HDC              hdc,
          UINT             iStart,
          UINT             cEntries,
          LPPALETTEENTRY   pPalEntries
        );
        """
        return 0

    @apihook('GdiSetBatchLimit', argc=1)
    def GdiSetBatchLimit(self, emu, argv, ctx={}):
        """
        DWORD GdiSetBatchLimit(
          DWORD dw
        );
        """
        return 0

    @apihook('MaskBlt', argc=12)
    def MaskBlt(self, emu, argv, ctx={}):
        """
        BOOL MaskBlt(
          HDC     hdcDest,
          int     xDest,
          int     yDest,
          int     width,
          int     height,
          HDC     hdcSrc,
          int     xSrc,
          int     ySrc,
          HBITMAP hbmMask,
          int     xMask,
          int     yMask,
          DWORD   rop
        );
        """
        return 1

    @apihook('BitBlt', argc=9)
    def BitBlt(self, emu, argv, ctx={}):
        """
        BOOL BitBlt(
        HDC   hdc,
        int   x,
        int   y,
        int   cx,
        int   cy,
        HDC   hdcSrc,
        int   x1,
        int   y1,
        DWORD rop
        """
        return 1

    @apihook('DeleteDC', argc=1)
    def DeleteDC(self, emu, argv, ctx={}):
        """
        BOOL DeleteDC(
        HDC hdc
        );
        """
        return 1

    @apihook('SelectObject', argc=2)
    def SelectObject(self, emu, argv, ctx={}):
        """
        HGDIOBJ SelectObject(
          HDC     hdc,
          HGDIOBJ h
        );
        """
        return 0

    @apihook('DeleteObject', argc=1)
    def DeleteObject(self, emu, argv, ctx={}):
        """
        BOOL DeleteObject(
        HGDIOBJ ho
        );
        """
        return 1

    @apihook('CreateCompatibleBitmap', argc=3)
    def CreateCompatibleBitmap(self, emu, argv, ctx={}):
        """
        HBITMAP CreateCompatibleBitmap(
        HDC hdc,
        int cx,
        int cy
        );
        """
        return 0

    @apihook('CreateCompatibleDC', argc=1)
    def CreateCompatibleDC(self, emu, argv, ctx={}):
        """
        HDC CreateCompatibleDC(
        HDC hdc
        );
        """
        return 0

    @apihook('CreatePalette', argc=1)
    def CreatePalette(self, emu, argv, ctx={}):
        """
        HPALETTE CreatePalette(
          const LOGPALETTE *plpal
        );
        """
        return self.get_handle()

    @apihook('GetObjectW', argc=3)
    def GetObjectW(self, emu, argv, ctx={}):
        """
        int GetObjectW(
          HGDIOBJ hgdiobj,
          int     cbBuffer,
          LPVOID  lpvObject
        );
        """
        hgdiobj, cbBuffer, lpvObject = argv
        
        # We don't track object types/sizes in this simple emulation yet.
        # We'll return a size large enough for common structures (BITMAP, LOGPEN, etc.)
        # BITMAP is ~24-32 bytes.
        # LOGFONTW is 92 bytes.
        
        # If lpvObject is NULL, return the bytes required. 
        # Since we don't know which object it is, we'll mimic a BITMAP size or just return cbBuffer if non-zero?
        # A safe bet for unknown objects often accessed by malware (like bitmaps) is standard BITMAP size.
        
        # 32-bit: 24 bytes, 64-bit: 32 bytes (approx)
        ptr_size = self.get_ptr_size()
        default_size = 24 if ptr_size == 4 else 32
        
        if not lpvObject:
            return default_size
            
        if cbBuffer == 0:
            return 0
            
        # Write zeros to the buffer
        count = min(cbBuffer, default_size)
        self.mem_write(lpvObject, b'\x00' * count)
        
        return count

    @apihook('GetDIBits', argc=7)
    def GetDIBits(self, emu, argv, ctx={}):
        """
        int GetDIBits(
        HDC          hdc,
        HBITMAP      hbm,
        UINT         start,
        UINT         cLines,
        LPVOID       lpvBits,
        LPBITMAPINFO lpbmi,
        UINT         usage
        );
        """
        return 0

    @apihook('CreateDIBSection', argc=6)
    def CreateDIBSection(self, emu, argv, ctx={}):
        """
        HBITMAP CreateDIBSection(
          [in]  HDC              hdc,
          [in]  const BITMAPINFO *pbmi,
          [in]  UINT             usage,
          [out] VOID             **ppvBits,
          [in]  HANDLE           hSection,
          [in]  DWORD            offset
        );
        """
        return 0

    @apihook('CreateDCA', argc=4)
    def CreateDCA(self, emu, argv, ctx={}):
        """
        HDC CreateDCA(
        LPCSTR         pwszDriver,
        LPCSTR         pwszDevice,
        LPCSTR         pszPort,
        const DEVMODEA *pdm
        );
        """
        return 0

        return 0

    @apihook('CreateDCW', argc=4)
    def CreateDCW(self, emu, argv, ctx={}):
        """
        HDC CreateDCW(
        LPCWSTR        pwszDriver,
        LPCWSTR        pwszDevice,
        LPCWSTR        pszPort,
        const DEVMODEW *pdm
        );
        """
        return 0

    @apihook('GetTextCharacterExtra', argc=1)
    def GetTextCharacterExtra(self, emu, argv, ctx={}):
        """
        int GetTextCharacterExtra(
          HDC hdc
        );
        """
        return 0x8000000

    @apihook('StretchBlt', argc=11)
    def StretchBlt(self, emu, argv, ctx={}):
        """
        BOOL StretchBlt(
          HDC   hdcDest,
          int   xDest,
          int   yDest,
          int   wDest,
          int   hDest,
          HDC   hdcSrc,
          int   xSrc,
          int   ySrc,
          int   wSrc,
          int   hSrc,
          DWORD rop
        );
        """
        return 0

    @apihook('CreateSolidBrush', argc=1)
    def CreateSolidBrush(self, emu, argv, ctx={}):
        """
        HBRUSH CreateSolidBrush(
          COLORREF color
        );
        """
        color, = argv
        # Return a handle to the brush
        return self.get_handle()

    @apihook('CreatePen', argc=3)
    def CreatePen(self, emu, argv, ctx={}):
        """
        HPEN CreatePen(
          int      iStyle,
          int      cWidth,
          COLORREF color
        );
        """
        iStyle, cWidth, color = argv
        # Return a handle to the pen
        return self.get_handle()

    @apihook('GetTextCharsetInfo', argc=3)
    def GetTextCharsetInfo(self, emu, argv, ctx={}):
        """
        int GetTextCharsetInfo(
          HDC             hdc,
          LPFONTSIGNATURE lpSig,
          DWORD           dwFlags
        );
        """
        hdc, lpSig, dwFlags = argv
        # Return ANSI_CHARSET (0) as default charset
        # Could also return DEFAULT_CHARSET (1) on failure
        return 0  # ANSI_CHARSET

    @apihook('CreateFontIndirectW', argc=1)
    def CreateFontIndirectW(self, emu, argv, ctx={}):
        """
        HFONT CreateFontIndirectW(
          const LOGFONTW *lplf
        );
        """
        lplf, = argv
        # Return a handle to the font
        return self.get_handle()

    @apihook('CreateFontIndirectA', argc=1)
    def CreateFontIndirectA(self, emu, argv, ctx={}):
        """
        HFONT CreateFontIndirectA(
          const LOGFONTA *lplf
        );
        """
        lplf, = argv
        # Return a handle to the font
        return self.get_handle()

    @apihook('GetTextMetricsW', argc=2)
    def GetTextMetricsW(self, emu, argv, ctx={}):
        """
        BOOL GetTextMetricsW(
          HDC          hdc,
          LPTEXTMETRICW lptm
        );
        """
        hdc, lptm = argv
        # Fill TEXTMETRICW structure with default values
        # The structure is 60 bytes (on 32-bit) / 60 bytes (on 64-bit)
        if lptm:
            # Just zero out the structure - basic stub implementation
            self.mem_write(lptm, b'\x00' * 60)
            # Set tmHeight to a reasonable value (16 pixels)
            self.mem_write(lptm, (16).to_bytes(4, 'little'))
        return 1  # TRUE for success

    @apihook('GetTextMetricsA', argc=2)
    def GetTextMetricsA(self, emu, argv, ctx={}):
        """
        BOOL GetTextMetricsA(
          HDC          hdc,
          LPTEXTMETRICA lptm
        );
        """
        hdc, lptm = argv
        if lptm:
            self.mem_write(lptm, b'\x00' * 60)
            self.mem_write(lptm, (16).to_bytes(4, 'little'))
        return 1  # TRUE for success
