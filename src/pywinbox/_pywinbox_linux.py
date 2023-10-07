#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
assert sys.platform == "linux"

from typing import Union, Optional

from Xlib.xobject.drawable import Window as XWindow
from ._main import Box
from ewmhlib import EwmhWindow


def _getHandle(handle: Union[int, XWindow]) -> Optional[EwmhWindow]:

    newHandle = None
    if isinstance(handle, int):
        newHandle = EwmhWindow(handle)
    elif isinstance(handle, XWindow):
        newHandle = EwmhWindow(handle.id)
    return newHandle


def _getWindowBox(handle: EwmhWindow) -> Box:
    # https://stackoverflow.com/questions/12775136/get-window-position-and-size-in-python-with-xlib
    geom = handle.xWindow.get_geometry()
    pos = handle.root.translate_coords(handle.id, 0, 0)

    # check if application uses special title bar (a.k.a. GTK HeaderBar)
    # see: https://docs.gtk.org/gtk4/class.HeaderBar.html
    # if it has HeaderBar (e.g., gedit):
    #   top left will be top left including extra space (shadows?)
    #   in that case, we subtract gtk extents to the right box
    # if it doesn't (e.g., gvim):
    #   top left will be top left of client window (i.e., excluding the title bar)
    #   in that case, we add the title bar to get the right box

    _net_extents = handle._getNetFrameExtents()
    _gtk_extents = handle._getGtkFrameExtents()
    if _net_extents and len(_net_extents) >= 4:
        # this means it has no GTK HeaderBar
        x = pos.x - int(_net_extents[0])
        y = pos.y - int(_net_extents[2])
        w = geom.width + int(_net_extents[0]) + int(_net_extents[1])
        h = geom.height + int(_net_extents[2]) + int(_net_extents[3])
    elif _gtk_extents and len(_gtk_extents) >= 4:
        # this means there is a GTK HeaderBar
        _gtk_extents = handle._getGtkFrameExtents()
        x = pos.x + int(_gtk_extents[0])
        y = pos.y + int(_gtk_extents[2])
        w = geom.width - int(_gtk_extents[0]) - int(_gtk_extents[1])
        h = geom.height - int(_gtk_extents[2]) - int(_gtk_extents[3])
    else:
        # something else: best guess is to trust pos and geom from above
        # NOTE: if you have this case and are not getting the expected result,
        #   please open an issue: https://github.com/Kalmat/PyWinBox/issues/new
        x = pos.x
        y = pos.y
        w = geom.width
        h = geom.height
    return Box(x, y, w, h)


def _moveResizeWindow(handle: EwmhWindow, newBox: Box):
    newLeft = max(0, newBox.left)  # Xlib won't accept negative positions
    newTop = max(0, newBox.top)
    handle.setMoveResize(x=newLeft, y=newTop, width=newBox.width, height=newBox.height, userAction=True)
    # handle.configure(x=newLeft, y=newTop, width=newBox.width, height=newBox.height)

