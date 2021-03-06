#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 meromorph.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#


import numpy
from gnuradio import gr

class xmlrpc_introspective_server(gr.basic_block):
    """
    docstring for block xmlrpc_introspective_server
    """
    def __init__(self, host, port):
        gr.basic_block.__init__(self,
            name="xmlrpc_introspective_server",
            in_sig=[],
            out_sig=[])

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        consume(0,0)
        return 0
