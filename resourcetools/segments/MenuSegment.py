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
# MenuSegment.py
# Python implementation of the Class MenuSegment
# Generated by Enterprise Architect
# Created on:      14-Aug-2019 10:11:57 AM
# Original author: talve
#
#######################################################
from segments.Segment import Segment
from segments.MenuRecord import MenuRecord
from segments.SegmentFactory import SegmentFactory
from resourcedump_lib.utils import constants as cs
from resourcedump_lib.utils.Exceptions import DumpNotSupported

import struct
import sys


class MenuSegment(Segment):
    """This class is responsible for holding menu segment data.
    """

    RECORD_BITS_SIZE = 416
    RECORD_DWORDS_SIZE = 13

    _segment_type_id = cs.RESOURCE_DUMP_SEGMENT_TYPE_MENU

    menu_sub_header_struct = struct.Struct('HH')

    def __init__(self, data):
        """Initialize the class by setting the class data.
        """

        super().__init__(data)
        self.type = cs.RESOURCE_DUMP_SEGMENT_TYPE_MENU
        self.size, _ = self.unpack_segment_header()
        self.num_of_records = self.unpack_num_of_records()

        self.records = []
        for i in range(self.num_of_records):
            rec = MenuRecord(data[(8 + i * self.RECORD_DWORDS_SIZE * 4): (8 + (i + 1) * self.RECORD_DWORDS_SIZE * 4)])
            self.records.append(rec)

    def unpack_num_of_records(self):
        short_1, short_2 = self.menu_sub_header_struct.unpack_from(self.raw_data, 4)
        return short_2 if sys.byteorder == "big" else short_1

    def get_records(self):
        """get all the menu segment records.
        """
        return self.records

    def get_printable_records(self):
        """get all the menu segment records in a printable format.
        """
        recs = []
        for rec in self.records:
            recs.append(rec.convert_record_obj_to_printable_list())
        return recs

    def get_segment_type_by_segment_name(self, segment_type):
        """get the menu segment type by a given segment name.
           if not found, method will return the given segment type
        """
        for rec in self.records:
            if rec.segment_name == segment_type:
                segment_type = rec.segment_type
        return segment_type

    def verify_support(self, **kwargs):
        """check if the arguments matches with the menu data.
        """
        dump_type = kwargs["segment"]
        index1 = kwargs["index1"]
        index2 = kwargs["index2"]
        num_of_objs_1 = kwargs["numOfObj1"]
        num_of_objs_2 = kwargs["numOfObj2"]
        match_rec = None

        # Check whether dump type supported
        for rec in self.records:
            if rec.segment_type == dump_type or rec.segment_name == dump_type:
                match_rec = rec
                break

        if not match_rec:
            raise DumpNotSupported("Dump type: {0} is not supported".format(dump_type))

        # Check index1 attribute
        if not index1 and index1 != 0 and match_rec.must_have_index1:
            raise DumpNotSupported(
                "Dump type: {0} must have index1 attribute, and it wasn't provided".format(dump_type))

        if not index2 and index2 != 0 and match_rec.must_have_index2:
            raise DumpNotSupported(
                "Dump type: {0} must have index2 attribute, and it wasn't provided".format(dump_type))

        if index1 and not match_rec.supports_index1:
            raise DumpNotSupported(
                "Dump type: {0} does not support index1 attribute, and it was provided".format(dump_type))

        if index2 and not match_rec.supports_index2:
            raise DumpNotSupported(
                "Dump type: {0} does not support index2 attribute, and it was provided".format(dump_type))

        if not num_of_objs_1 and match_rec.must_have_num_of_obj1:
            raise DumpNotSupported(
                "Dump type: {0} must have numOfObj1 attribute, and it wasn't provided".format(dump_type))

        if not num_of_objs_2 and match_rec.must_have_num_of_obj2:
            raise DumpNotSupported(
                "Dump type: {0} must have numOfObj2 attribute, and it wasn't provided".format(dump_type))

        if num_of_objs_1 and not match_rec.supports_num_of_obj1:
            raise DumpNotSupported(
                "Dump type: {0} does not support numOfObj1 attribute, and it was provided".format(dump_type))

        if num_of_objs_2 and not match_rec.supports_num_of_obj2:
            raise DumpNotSupported(
                "Dump type: {0} does not support numOfObj2 attribute, and it was provided".format(dump_type))

        if num_of_objs_1 == cs.NUM_OF_OBJ_ALL and not match_rec.supports_all_num_of_obj1:
            raise DumpNotSupported(
                "Dump type: {0} does not support 'all' as numOfObj1 attribute".format(dump_type))

        if num_of_objs_2 == cs.NUM_OF_OBJ_ALL and not match_rec.supports_all_num_of_obj2:
            raise DumpNotSupported(
                "Dump type: {0} does not support 'all' as numOfObj2 attribute".format(dump_type))

        if num_of_objs_1 == cs.NUM_OF_OBJ_ACTIVE and not match_rec.supports_active_num_of_obj1:
            raise DumpNotSupported(
                "Dump type: {0} does not support 'active' as numOfObj1 attribute".format(dump_type))

        if num_of_objs_2 == cs.NUM_OF_OBJ_ACTIVE and not match_rec.supports_active_num_of_obj2:
            raise DumpNotSupported(
                "Dump type: {0} does not support 'active' as numOfObj2 attribute".format(dump_type))


SegmentFactory.register(cs.RESOURCE_DUMP_SEGMENT_TYPE_MENU, MenuSegment)
