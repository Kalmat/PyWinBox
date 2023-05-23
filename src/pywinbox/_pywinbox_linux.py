#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys

assert sys.platform == "linux"

from typing import Union, Optional

from pywinbox._xlibcontainer import defaultDisplay, defaultRootWindow, XWindow
from pywinbox import Box


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
        if not isinstance(parent, XWindow):
            break
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        if parent.id == 0:
            break
        win = parent
    return Box(x, y, w, h)


def _moveResizeWindow(handle: XWindow, newBox: Box):
    newLeft = max(0, newBox.left)  # Xlib won't accept negative positions
    newTop = max(0, newBox.top)
    defaultRootWindow.setMoveResize(winId=handle.id, x=newLeft, y=newTop, width=newBox.width, height=newBox.height, userAction=True)
    # handle.configure(x=newLeft, y=newTop, width=newBox.width, height=newBox.height)
