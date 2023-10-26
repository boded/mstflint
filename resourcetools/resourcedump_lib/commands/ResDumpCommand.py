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
# ResDumpCommand.py
# Python implementation of the Class ResDumpCommand
# Generated by Enterprise Architect
# Created on:      14-Aug-2019 10:11:58 AM
# Original author: talve
#
#######################################################
from abc import ABC, abstractmethod

import ctypes
from resourcedump_lib.cresourcedump.CResourceDump import CResourceDump
from resourcedump_lib.cresourcedump.cresourcedump_types import c_device_attributes, c_dump_request, c_resource_dump_data

from segments.SegmentCreator import SegmentCreator


class ResDumpCommand(ABC):
    """This class is an interface for the resource dump commands and perform a
    strategy pattern of the execution by calling the internal methods.
      validate and get_data that will be implemented by each command.
    """
    def execute(self):
        """Command execution call:
           1. validate.
           2. retrieve_data.
        """
        self.validate()
        try:
            self.retrieve_data()
        except Exception as e:
            raise Exception("Failed {} - {}".format(type(self).__name__, e))

    @abstractmethod
    def retrieve_data(self):
        """get the needed data.
        """
        pass

    @abstractmethod
    def validate(self):
        """validate.
        """
        pass

    def get_raw_data(self):
        if self.raw_data is None:
            self.retrieve_data()
        return self.raw_data

    def get_segments(self, aggregate=False):
        if self.segments is None:
            self.segments = SegmentCreator().create(self.get_raw_data(), aggregate)
        return self.segments

    def __init__(self):
        self._sdk_dump_data = None
        self.raw_data = None
        self.segments = None

    def __del__(self):
        if self._sdk_dump_data:
            CResourceDump.c_destroy_resource_dump(self._sdk_dump_data.contents)

    def retrieve_data_from_sdk(self):
        device_name = bytes(self.device_name, "utf-8")
        rdma_name = bytes(self.mem, "utf-8")

        device_attrs = c_device_attributes(device_name, self.vHCAid, rdma_name)
        dump_request = c_dump_request(self.segment, self.index1, self.index2, self.numOfObj1, self.numOfObj2)

        # dump for display is done with native endianess for ease and efficiency of calculations
        self._sdk_dump_data = ctypes.pointer(c_resource_dump_data(None, None, 0, 0))
        if CResourceDump.c_create_resource_dump(device_attrs, dump_request, self._sdk_dump_data, self.depth) != 0:
            raise Exception(CResourceDump.c_get_resource_dump_error().decode("utf-8"))
        self.raw_data = bytes(self._sdk_dump_data.contents.data[0:self._sdk_dump_data.contents.size])
