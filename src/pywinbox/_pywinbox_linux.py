#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

assert sys.platform == "linux"

from typing import Union, Optional

from ewmhlib import EwmhWindow
from Xlib.xobject.drawable import Window as XWindow
from pywinbox import Box


def _getHandle(handle: Union[int, XWindow]) -> Optional[EwmhWindow]:
    newHandle = None
    if isinstance(handle, int):
        newHandle = EwmhWindow(handle)
    elif isinstance(handle, XWindow):
        newHandle = EwmhWindow(handle.id)
    return newHandle


def _getWindowBox(handle: EwmhWindow) -> Box:
    win = handle.xWindow
    geom = win.get_geometry()
    x = geom.x
    y = geom.y
    w = geom.width
    h = geom.height
    while True:
        parent = win.query_tree().parent
        if not parent or not isinstance(parent, XWindow):
            break
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        if parent.id == 0:
            break
        win = parent
    # Thanks to roym899 (https://github.com/roym899) for his HELP!!!!
    _net_extents = handle._getNetFrameExtents()
    if _net_extents and len(_net_extents) >= 4:
        x = x - _net_extents[0]
        y = y - _net_extents[2]
        w = w + _net_extents[0] + _net_extents[1]
        h = h + _net_extents[2] + _net_extents[3]
    return Box(x, y, w, h)


def _moveResizeWindow(handle: EwmhWindow, newBox: Box):
    newLeft = max(0, newBox.left)  # Xlib won't accept negative positions
    newTop = max(0, newBox.top)
    handle.rootWindow.root.setMoveResize(winId=handle.id, x=newLeft, y=newTop, width=newBox.width, height=newBox.height, userAction=True)
    # handle.configure(x=newLeft, y=newTop, width=newBox.width, height=newBox.height)
