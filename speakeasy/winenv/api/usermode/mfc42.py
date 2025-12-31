# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

from .. import api


class MFC42(api.ApiHandler):
    """
    Implements exported functions from mfc42.dll
    MFC42 exports many functions by ordinal number rather than name.
    These are stub implementations to allow emulation to continue.
    
    MFC is primarily a GUI framework and most functions are not critical
    for malware emulation. We return dummy handles/success values.
    """

    name = 'mfc42'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):
        super(MFC42, self).__init__(emu)
        self.funcs = {}
        self.data = {}
        self.handle = 0x4000
        super(MFC42, self).__get_hook_attrs__(self)

    def get_handle(self):
        self.handle += 4
        return self.handle

    # ============================================================
    # Common MFC Ordinals - Stub Implementations
    # Most return a dummy handle (non-zero) to prevent NULL errors
    # ============================================================

    # CWinApp related
    @apihook('ordinal_1168', argc=0)  # CWinApp::InitInstance
    def ordinal_1168(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_1169', argc=0)  # CWinApp::ExitInstance
    def ordinal_1169(self, emu, argv, ctx={}):
        return 0

    @apihook('ordinal_1170', argc=0)  # CWinApp::Run
    def ordinal_1170(self, emu, argv, ctx={}):
        return 0

    # CString related (very common)
    @apihook('ordinal_800', argc=0)
    def ordinal_800(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_801', argc=0)
    def ordinal_801(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_802', argc=0)
    def ordinal_802(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_820', argc=0)
    def ordinal_820(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_821', argc=0)
    def ordinal_821(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_822', argc=0)
    def ordinal_822(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_823', argc=0)
    def ordinal_823(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_824', argc=0)
    def ordinal_824(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_825', argc=0)
    def ordinal_825(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_826', argc=0)
    def ordinal_826(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_827', argc=0)
    def ordinal_827(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_828', argc=0)
    def ordinal_828(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_829', argc=0)
    def ordinal_829(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_830', argc=0)
    def ordinal_830(self, emu, argv, ctx={}):
        return self.get_handle()

    # CWnd related
    @apihook('ordinal_2514', argc=0)  # CWnd::Create
    def ordinal_2514(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_2515', argc=0)
    def ordinal_2515(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_2516', argc=0)
    def ordinal_2516(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2517', argc=0)
    def ordinal_2517(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2518', argc=0)
    def ordinal_2518(self, emu, argv, ctx={}):
        return self.get_handle()

    # CObject related
    @apihook('ordinal_311', argc=0)
    def ordinal_311(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_312', argc=0)
    def ordinal_312(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_313', argc=0)
    def ordinal_313(self, emu, argv, ctx={}):
        return self.get_handle()

    # AfxWinMain and AfxWinInit
    @apihook('ordinal_1578', argc=0)  # AfxWinMain
    def ordinal_1578(self, emu, argv, ctx={}):
        return 0

    @apihook('ordinal_1579', argc=0)  # AfxWinInit
    def ordinal_1579(self, emu, argv, ctx={}):
        return 1

    # CRuntimeClass related
    @apihook('ordinal_442', argc=0)
    def ordinal_442(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_443', argc=0)
    def ordinal_443(self, emu, argv, ctx={}):
        return self.get_handle()

    # Memory/allocation related
    @apihook('ordinal_100', argc=0)
    def ordinal_100(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_101', argc=0)
    def ordinal_101(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_102', argc=0)
    def ordinal_102(self, emu, argv, ctx={}):
        return 1

    # Range of common ordinals (500-600 range)
    @apihook('ordinal_540', argc=0)
    def ordinal_540(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_541', argc=0)
    def ordinal_541(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_542', argc=0)
    def ordinal_542(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_543', argc=0)
    def ordinal_543(self, emu, argv, ctx={}):
        return self.get_handle()

    # CFile related
    @apihook('ordinal_1200', argc=0)
    def ordinal_1200(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1201', argc=0)
    def ordinal_1201(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_1202', argc=0)
    def ordinal_1202(self, emu, argv, ctx={}):
        return 1

    # CArchive related
    @apihook('ordinal_1300', argc=0)
    def ordinal_1300(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1301', argc=0)
    def ordinal_1301(self, emu, argv, ctx={}):
        return self.get_handle()

    # Dialog related
    @apihook('ordinal_2000', argc=0)
    def ordinal_2000(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_2001', argc=0)
    def ordinal_2001(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_2002', argc=0)
    def ordinal_2002(self, emu, argv, ctx={}):
        return self.get_handle()

    # Exception handling
    @apihook('ordinal_3000', argc=0)
    def ordinal_3000(self, emu, argv, ctx={}):
        return 0

    @apihook('ordinal_3001', argc=0)
    def ordinal_3001(self, emu, argv, ctx={}):
        return 0

    # More CString operations (858-900 range - very common)
    @apihook('ordinal_858', argc=0)
    def ordinal_858(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_859', argc=0)
    def ordinal_859(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_860', argc=0)
    def ordinal_860(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_861', argc=0)
    def ordinal_861(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_862', argc=0)
    def ordinal_862(self, emu, argv, ctx={}):
        return self.get_handle()

    # Additional commonly used ordinals
    @apihook('ordinal_350', argc=0)
    def ordinal_350(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_351', argc=0)
    def ordinal_351(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_352', argc=0)
    def ordinal_352(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_400', argc=0)
    def ordinal_400(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_401', argc=0)
    def ordinal_401(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_402', argc=0)
    def ordinal_402(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_403', argc=0)
    def ordinal_403(self, emu, argv, ctx={}):
        return self.get_handle()

    # Afx global functions (1500-1600 range)
    @apihook('ordinal_1500', argc=0)
    def ordinal_1500(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1501', argc=0)
    def ordinal_1501(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1502', argc=0)
    def ordinal_1502(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1503', argc=0)
    def ordinal_1503(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1504', argc=0)
    def ordinal_1504(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_1505', argc=0)
    def ordinal_1505(self, emu, argv, ctx={}):
        return 1

    @apihook('ordinal_1506', argc=0)
    def ordinal_1506(self, emu, argv, ctx={}):
        return 1

    # CDC related (drawing context)
    @apihook('ordinal_2600', argc=0)
    def ordinal_2600(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2601', argc=0)
    def ordinal_2601(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2602', argc=0)
    def ordinal_2602(self, emu, argv, ctx={}):
        return 1

    # CMenu related
    @apihook('ordinal_2700', argc=0)
    def ordinal_2700(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2701', argc=0)
    def ordinal_2701(self, emu, argv, ctx={}):
        return 1

    # Additional low ordinals (might be more common)
    @apihook('ordinal_1', argc=0)
    def ordinal_1(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_2', argc=0)
    def ordinal_2(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_3', argc=0)
    def ordinal_3(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_4', argc=0)
    def ordinal_4(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_5', argc=0)
    def ordinal_5(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_6', argc=0)
    def ordinal_6(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_7', argc=0)
    def ordinal_7(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_8', argc=0)
    def ordinal_8(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_9', argc=0)
    def ordinal_9(self, emu, argv, ctx={}):
        return self.get_handle()

    @apihook('ordinal_10', argc=0)
    def ordinal_10(self, emu, argv, ctx={}):
        return self.get_handle()
