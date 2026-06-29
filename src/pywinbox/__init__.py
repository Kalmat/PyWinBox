#!/usr/bin/python
from importlib.metadata import version as _importlib_version

__all__ = [
    "version",
    "Box", "Rect", "Point", "Size",
    "PyWinBox", "WindowBox", "ScreenBox",
    "pointInBox", "collidepoint", "collidebox", "contains", "clip", "union"
]

__version__ = _importlib_version("pywinctl")


def version(numberOnly: bool = True) -> str:
    """Returns the current version of PyWinBox module, in the form ''x.x.xx'' as string"""
    return ("" if numberOnly else "PyWinBox-")+__version__


from ._main import (Box, Rect, Point, Size,
                    PyWinBox, WindowBox, ScreenBox,
                    pointInBox, collidepoint, collidebox, contains, clip, union)
