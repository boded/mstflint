# Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. ALL RIGHTS RESERVED.
#
# This software is available to you under a choice of one of two
# licenses.  You may choose to be licensed under the terms of the GNU
# General Public License (GPL) Version 2, available from the file
# COPYING in the main directory of this source tree, or the
# OpenIB.org BSD license below:
#
#     Redistribution and use in source and binary forms, with or
#     without modification, are permitted provided that the following
#     conditions are met:
#
#      - Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      - Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials
#        provided with the distribution.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#######################################################
#
# ErrorSegment.py
# Python implementation of the Class ErrorSegment
# Generated by Enterprise Architect
# Created on:      14-Aug-2019 10:11:57 AM
# Original author: talve
#
#######################################################
from segments.Segment import Segment
from segments.SegmentFactory import SegmentFactory
from resourceparse_lib.utils.common_functions import reverse_string_endian
from resourcedump_lib.utils import constants

import struct
import sys


class ErrorSegment(Segment):
    """this class is responsible for holding error segment data.
    """

    message_name = "Error message"
    _segment_type_id = constants.RESOURCE_DUMP_SEGMENT_TYPE_ERROR

    error_struct = struct.Struct('HHII32s')

    def __init__(self, data):
        """initialize the class by setting the class data.
        """
        super().__init__(data)

    def get_messages(self):
        start = self.segment_header_struct.size
        if len(self.raw_data) > start:
            syndrome_id, error_message = self.unpack_error()
            self.add_message("{}{} = {}".format(self.message_name, " ({})".format(syndrome_id) if syndrome_id else "", error_message))

        return self._messages

    def unpack_error(self):
        fields = self.error_struct.unpack_from(self.raw_data, self.segment_header_struct.size)
        if sys.byteorder == 'big':
            syndrome_id = fields[1]
            error_message = fields[4]
        else:
            syndrome_id = fields[0]
            error_message = reverse_string_endian(fields[4])
        # syndrome_id, error_message = fields[1], fields[4]
        error_message = error_message.decode('utf-8')
        return syndrome_id, error_message


SegmentFactory.register(constants.RESOURCE_DUMP_SEGMENT_TYPE_ERROR, ErrorSegment)
