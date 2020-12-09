#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains a set of useful traceback elements based on python's
:mod:`traceback` system."""

from builtins import str
import sys
import traceback
import threading


def _get_thread(ident=None):
    if ident is None:
        return threading.current_thread()
    for th in threading.enumerate():
        if th.ident == ident:
            return th


def _get_frames():
    return sys._current_frames()


def format_frame_stacks(frames=None, limit=None):
    if frames is None:
        frames = _get_frames()
    frame_stacks = extract_frame_stacks(frames=frames, limit=limit)
    ret = []

    for ident, (frame, frame_stack) in list(frame_stacks.items()):
        curr_th, th = _get_thread(), _get_thread(ident)
        if th is None:
            th_name = "<Unknown>"
            curr = ""
        else:
            th_name = th.name
            if curr_th.ident == th.ident:
                th_str = "(Current) "
            else:
                curr = ""
        ret.append("  Thread " + curr + th_name + " (" + str(ident) + ") in\n")
        format_stack = traceback.format_list(frame_stack)
        for i, line in enumerate(format_stack):
            line = "  " + line.replace("\n  ", "\n    ")
            ret.append(line)
    return ret


def extract_frame_stacks(frames=None, limit=None):
    if frames is None:
        frames = _get_frames()
    ret = {}
    for ident, frame in list(frames.items()):
        frame_stack = traceback.extract_stack(frame, limit=limit)
        ret[ident] = frame, frame_stack
    return ret
