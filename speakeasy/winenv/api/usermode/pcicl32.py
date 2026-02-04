# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

import speakeasy.winenv.arch as _arch

from .. import api


class Pcicl32(api.ApiHandler):

    name = 'pcicl32'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(Pcicl32, self).__init__(emu)
        super(Pcicl32, self).__get_hook_attrs__(self)

    @apihook('_NSMClient32@8', argc=2, conv=_arch.CALL_CONV_STDCALL)
    def NSMClient32(self, emu, argv, ctx={}):
        """
        int _NSMClient32(
            int arg1,
            int arg2
        );
        """
        return 0
