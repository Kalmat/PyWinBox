#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

assert sys.platform == "linux"

from typing import Union, Optional

from pywinbox._xlibcontainer import defaultDisplay, defaultRootWindow, XWindow, EwmhWindow
from pywinbox import Box

_ewmhWin: Optional[EwmhWindow] = None
_net_extents: list[int] = []


def _getHandle(handle: Union[int, XWindow]) -> Optional[XWindow]:
    newHandle = None
    if isinstance(handle, int):
        newHandle = defaultDisplay.create_resource_object('window', handle)
    elif isinstance(handle, XWindow):
        newHandle = handle
    return newHandle


def _getWindowBox(handle: XWindow) -> Box:
    win = handle
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
    global _ewmhWin
    global _net_extents
    if _ewmhWin is None:
        _ewmhWin = EwmhWindow(handle.id)
        _net_extents = _ewmhWin._getNetFrameExtents()
    if len(_net_extents) >= 4:
        x = x - _net_extents[0]
        y = y - _net_extents[2]
        w = w + _net_extents[0] + _net_extents[1]
        h = h + _net_extents[2] + _net_extents[3]
    return Box(x, y, w, h)


def _moveResizeWindow(handle: XWindow, newBox: Box):
    newLeft = max(0, newBox.left)  # Xlib won't accept negative positions
    newTop = max(0, newBox.top)
    defaultRootWindow.setMoveResize(winId=handle.id, x=newLeft, y=newTop, width=newBox.width, height=newBox.height, userAction=True)
    # handle.configure(x=newLeft, y=newTop, width=newBox.width, height=newBox.height)
