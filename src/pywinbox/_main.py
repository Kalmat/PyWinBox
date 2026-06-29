#!/usr/bin/python
from __future__ import annotations

import sys
import warnings
from collections.abc import Callable
from typing import NamedTuple

import pywinbox


class Box(NamedTuple):
    """Container class to handle Box struct (left, top, width, height)"""
    left: int
    top: int
    width: int
    height: int


class Rect(NamedTuple):
    """Container class to handle Rect struct (left, top, right, bottom)"""
    left: int
    top: int
    right: int
    bottom: int


class Point(NamedTuple):
    """Container class to handle Point struct (x, y)"""
    x: int
    y: int


class Size(NamedTuple):
    """Container class to handle Size struct (right, bottom)"""
    width: int
    height: int


def pointInBox(x: int, y: int, box: Box |tuple[int, int, int, int]) -> bool:
    """
    Check if a point defined by ``(x, y)`` is within the box described by ``(left, top, width, height)``.

    :param x: x coordinate of point
    :param y: y coordinate of point
    :param box: Box struct (left, top, width, height) or tuple of integers
    :return: ``True`` if the ``(x, y)`` point is within the box described by ``(left, top, width, height)``
    """
    x1, y1, w1, h1 = box if isinstance(box, tuple) else (box.left, box.top, box.width, box.height)
    return x1 <= x <= x1 + w1 and y1 <= y <= y1 + h1
collidepoint = pointInBox  # collidepoint is an alias for pointInBox


def collidebox(box1: Box | tuple[int, int, int, int], box2: Box | tuple[int, int, int, int]) -> bool:
    """
    Check if two Box objects are colliding with each other.
    
    :param box1: first Box struct (left, top, width, height)
    :param box2: second Box struct (left, top, width, height)
    :return: ``True`` if the two Box objects are colliding
    """
    x1, y1, w1, h1 = box1 if isinstance(box1, tuple) else (box1.left, box1.top, box1.width, box1.height)
    x2, y2, w2, h2 = box2 if isinstance(box2, tuple) else (box2.left, box2.top, box2.width, box2.height)
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def contains(box1: Box | tuple[int, int, int, int], box2: Box | tuple[int, int, int, int]) -> bool:
    """
    Check if box1 is entirely inside box2.

    :param box1: first Box struct (left, top, width, height)
    :param box2: second Box struct (left, top, width, height)
    :return: ``True`` if box1 is entirely inside box2
    """
    x1, y1, w1, h1 = box1 if isinstance(box1, tuple) else (box1.left, box1.top, box1.width, box1.height)
    x2, y2, w2, h2 = box2 if isinstance(box2, tuple) else (box2.left, box2.top, box2.width, box2.height)
    return x1 >= x2 and x1 + w1 <= x2 + w2 and y1 >= y2 and y1 + h1 <= y2 + h2


def clip(box1: Box | tuple[int, int, int, int], box2: Box | tuple[int, int, int, int]) -> Box | None:
    """
    Return the intersection between two Box objects, if any.

    :param box1: first Box struct (left, top, width, height)
    :param box2: second Box struct (left, top, width, height)
    :return: intersection Box struct (left, top, width, height) or None if there is no intersection
    """
    if collidebox(box1, box2):
        x1, y1, w1, h1 = box1 if isinstance(box1, tuple) else (box1.left, box1.top, box1.width, box1.height)
        x2, y2, w2, h2 = box2 if isinstance(box2, tuple) else (box2.left, box2.top, box2.width, box2.height)
        return Box(max(x1, x2), max(y1, y2), max(x1, x2) + min(w1, w2), max(y1, y2) + min(h1, h2))
    else:
        return None


def union(box1: Box | tuple[int, int, int, int], box2: Box | tuple[int, int, int, int]) -> Box | None:
    """
    Return the bounding box (minimal area which contains both) of two Box objects.

    :param box1: first Box struct (left, top, width, height)
    :param box2: second Box struct (left, top, width, height)
    :return: union Box struct (left, top, width, height) or None if not valid union area exists
    """
    if not isinstance(box1, Box):
        box1 = Box(*box1)
    if not isinstance(box2, Box):
        box2 = Box(*box2)

    def onQuery1() -> Box:
        return box1

    def onQuery2() -> Box:
        return box2

    def onSet(box :Box) -> None:
        pass

    # creating a ScreenBox object to take advantage of multi-monitor features
    myBox1 = pywinbox.ScreenBox(box1, onQuery1, onSet)
    myBox2 = pywinbox.ScreenBox(box2, onQuery2, onSet)

    new_x = min(box1.left, box2.left)
    new_y = min(box1.top, box2.top)
    new_w = max(myBox1.right, myBox2.right) - new_x
    new_h = max(myBox1.bottom, myBox2.bottom) - new_y

    # Return new Box; if dimensions are <= 0, rectangles do not overlap or touch validly
    if new_w > 0 and new_h > 0:
        return Box(new_x, new_y, new_w, new_h)
    else:
        # Return None if no valid union exists
        return None


class BaseClass:

    def __init__(self,
                 handle = None,
                 box :Box | None = None,
                 onQuery :Callable[[], Box] | None = None, onSet :Callable[[Box], None] | None = None) -> None:

        self._handle = handle
        self._box :Box = box or Box(0, 0, 0, 0)
        self._onQuery: Callable[[], Box] = onQuery or self.onQuery
        self._onSet: Callable[[Box], None] = onSet or self.onSet
        self._clamp: Box | None = None

    def onQuery(self) -> Box:
        """
        Default method to retrieve current window position and size values when a property is queried.
        It requires to pass valid window handle when instantiating the main class (WindowBox/ScreenBox)

        :return: window Box struct (x, y, width, height)
        """
        if self._handle is not None:
            self._box = _getWindowBox(self._handle)
        return self._box

    def _clamp_box(self, box :Box, boundary :Box):
        """
        Clamps a Box entirely inside a boundary.
        Both box and boundary are Box structures (x, y, width, height).

        Priority: size is preserved if possible; position is adjusted to fit.
        If the box is larger than the boundary in any dimension, it is clamped
        to the boundary size (size takes priority over position, buy only when it fits).

        Returns the adjusted Box (x, y, width, height).
        """
        rx, ry, rw, rh = box.left, box.top, box.width, box.height
        bx, by, bw, bh = boundary.left, boundary.top, boundary.width, boundary.height

        # Clamp size to boundary dimensions (can't be larger than boundary)
        new_w = min(rw, bw)
        new_h = min(rh, bh)

        # Adjust position so the rect fits within the boundary
        # First, ensure x/y are not before the boundary origin
        new_x = max(rx, bx)
        new_y = max(ry, by)

        # Then, ensure the rect doesn't exceed the boundary's right/bottom edge
        new_x = min(new_x, bx + bw - new_w)
        new_y = min(new_y, by + bh - new_h)

        return Box(new_x, new_y, new_w, new_h)

    def onSet(self, newBox: Box):
        """
        Default method to actually place / resize the window when a property is changed.
        It requires to pass valid window handle when instantiating the main class (WindowBox/ScreenBox)

        :param newBox: target position and or size in Box struct format (x, y, width, height)
        """
        if self._handle is not None:
            if self._clamp is not None:
                newBox = self._clamp_box(newBox, self._clamp)
            _moveResizeWindow(self._handle, newBox)

    def __repr__(self) -> str:
        """Return a string of the constructor function call to create this Box object."""
        return "%s(left=%s, top=%s, width=%s, height=%s)" % (
            self.__class__.__name__,
            self._box.left,
            self._box.top,
            self._box.width,
            self._box.height,
        )

    def __str__(self) -> str:
        """Return a string representation of this Box object."""
        return "(%s, %s, %s, %s)" % (
            self._box.left,
            self._box.top,
            self._box.width,
            self._box.height,
        )

    @property
    def left(self) -> int:
        self._box = self._onQuery()
        return self._box.left

    @left.setter
    def left(self, value: int):
        self._box = self._onQuery()
        self._box = Box(value, self._box.top, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def right(self) -> int:
        self._box = self._onQuery()
        return self._box.left + self._box.width

    @right.setter
    def right(self, value: int):
        self._box = self._onQuery()
        self._box = Box(value - self._box.width, self._box.top, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def top(self) -> int:
        self._box = self._onQuery()
        return self._box.top

    @top.setter
    def top(self, value: int):
        self._box = self._onQuery()
        self._box = Box(self._box.left, value, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def bottom(self) -> int:
        self._box = self._onQuery()
        return self._box.top + self._box.height

    @bottom.setter
    def bottom(self, value: int):
        self._box = self._onQuery()
        self._box = Box(self._box.left, value - self._box.height, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def width(self) -> int:
        self._box = self._onQuery()
        return self._box.width

    @width.setter
    def width(self, value: int):
        self._box = self._onQuery()
        self._box = Box(self._box.left, self._box.top, value, self._box.height)
        self._onSet(self._box)

    @property
    def height(self) -> int:
        self._box = self._onQuery()
        return self._box.height

    @height.setter
    def height(self, value: int):
        self._box = self._onQuery()
        self._box = Box(self._box.left, self._box.top, self._box.width, value)
        self._onSet(self._box)

    @property
    def position(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left, self._box.top)

    @position.setter
    def position(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x, val.y, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def size(self) -> Size:
        self._box = self._onQuery()
        return Size(self._box.width, self._box.height)

    @size.setter
    def size(self, value: Size | tuple[int, int]):
        val: Size = Size(*value)
        self._box = self._onQuery()
        self._box = Box(self._box.left, self._box.top, val.width, val.height)
        self._onSet(self._box)

    @property
    def box(self) -> Box:
        self._box = self._onQuery()
        return self._box

    @box.setter
    def box(self, value: Box | tuple[int, int, int, int]):
        val: Box = Box(*value)
        self._box = val
        self._onSet(self._box)

    @property
    def rect(self) -> Rect:
        self._box = self._onQuery()
        return Rect(self._box.left, self._box.top, self._box.left + self._box.width,
                    self._box.top + self._box.height)

    @rect.setter
    def rect(self, value: Rect | tuple[int, int, int, int]):
        val: Rect = Rect(*value)
        self._box = Box(val.left, val.top, abs(val.right - val.left), abs(val.bottom - val.top))
        self._onSet(self._box)

    @property
    def topleft(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left, self._box.top)

    @topleft.setter
    def topleft(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x, val.y, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def bottomleft(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left, self._box.top + self._box.height)

    @bottomleft.setter
    def bottomleft(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x, val.y - self._box.height, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def topright(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + self._box.width, self._box.top)

    @topright.setter
    def topright(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - self._box.width, val.y, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def bottomright(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + self._box.width, self._box.top + self._box.height)

    @bottomright.setter
    def bottomright(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - self._box.width, val.y - self._box.height, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def midtop(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + (self._box.width // 2), self._box.top)

    @midtop.setter
    def midtop(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - (self._box.width // 2), val.y, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def midbottom(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + (self._box.width // 2), self._box.top + self._box.height)

    @midbottom.setter
    def midbottom(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - (self._box.width // 2), val.y - self._box.height, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def midleft(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left, self._box.top + (self._box.height // 2))

    @midleft.setter
    def midleft(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x, val.y - (self._box.height // 2), self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def midright(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + self._box.width, self._box.top + (self._box.height // 2))

    @midright.setter
    def midright(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - self._box.width, val.y - (self._box.height // 2), self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def center(self) -> Point:
        self._box = self._onQuery()
        return Point(self._box.left + (self._box.width // 2), self._box.top + (self._box.height // 2))

    @center.setter
    def center(self, value: Point | tuple[int, int]):
        val: Point = Point(*value)
        self._box = self._onQuery()
        self._box = Box(val.x - (self._box.width // 2), val.y - (self._box.height // 2), self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def centerx(self) -> int:
        self._box = self._onQuery()
        return self._box.left + (self._box.width // 2)

    @centerx.setter
    def centerx(self, value: int):
        self._box = self._onQuery()
        self._box = Box(value - (self._box.width // 2), self._box.top, self._box.width, self._box.height)
        self._onSet(self._box)

    @property
    def centery(self) -> int:
        self._box = self._onQuery()
        return self._box.top + (self._box.height // 2)

    @centery.setter
    def centery(self, value: int):
        self._box = self._onQuery()
        self._box = Box(self._box.left, value - (self._box.height // 2), self._box.width, self._box.height)
        self._onSet(self._box)

    def collidepoint(self, x: int, y: int) -> bool:
        """
        Check if a point defined by ``(x, y)`` is within the window/area box

        :param x: x coordinate of point
        :param y: y coordinate of point
        :return: ``True`` if the ``(x, y)`` point is within the box described by ``(left, top, width, height)``
        """
        self._box = self._onQuery()
        return collidepoint(x, y, self._box)

    def collidebox(self, box: Box | tuple[int, int, int, int]) -> bool:
        """
        Check if the window/area box is colliding with another Box area described by ``(left, top, width, height)``.

        :param box: Box struct (left, top, width, height)
        :return: ``True`` if the two Box objects are colliding
        """
        self._box = self._onQuery()
        return collidebox(self._box, box)

    def contains(self, box: Box | tuple[int, int, int, int]) -> bool:
        """
        Check if another box described by ``(left, top, width, height)``, is entirely inside this window/area box.

        :param box: Box struct (left, top, width, height)
        :return: ``True`` if box1 is entirely inside box2
        """
        self._box = self._onQuery()
        return contains(self._box, box)

    def clip(self, box: Box | tuple[int, int, int, int]) -> Box | None:
        """
        Return the intersection between this window/area and another Box, if any.

        :param box: Box struct (left, top, width, height)
        :return: intersection Box struct (left, top, width, height) or None if there is no intersection
        """
        self._box = self._onQuery()
        return clip(self._box, box)

    def union(self, box: Box | tuple[int, int, int, int]) -> Box | None:
        """
        Return the bounding box (minimal area which contains both) of this window/area and another Box.

        :param box: Box struct (left, top, width, height)
        :return: union Box struct (left, top, width, height) or None if not valid union area exists
        """
        self._box = self._onQuery()
        return union(self._box, box)

    def move(self, dx: int, dy: int) -> Box:
        """
        Relative movement of window/area by given delta values (dx, dy).

        :param dx: delta x value
        :param dy: delta y value
        :return: resultant Box struct (left, top, width, height)
        """
        self._box = self._onQuery()
        self._box.position = (self._box.position[0] + dx, self._box.position[1] + dy)
        return self._box

    def inflate(self, dw: float, dh: float) -> Box:
        """
        Resize window/area by given delta values (dw, dh).

        dw and dh are decimal fraction numbers which represent the percentage to apply to current
        window/area size. For instance:
            - 1.5 = 150% = increase current size by a 50%
            - 0.8 = 80% = decrease current size by a 20% or set size as 80% of current size

        :param dw: delta width value as float
        :param dh: delta height value as float
        :return: resultant Box struct (left, top, width, height)
        """
        self._box = self._onQuery()
        self._box.size = (int(self._box.size[0] * dw), int(self._box.size[1] * dh))
        return self._box

    def clamp(self, boundary: Box | tuple[int, int, int, int]) -> None:
        """
        Define boundaries as Box structure to keep window/area inside.

        :param boundary: Boundaries structure (left, top, width, height)
        """
        if not isinstance(boundary, Box):
            boundary = Box(*boundary)
        self._clamp = boundary
        self.fit(self._clamp)

    def isclamped(self) -> bool:
        """
        Check if clamp boundaries are defined and active.

        :return: ``True`` if clamp boundaries are defined and active
        """
        return self._clamp is not None

    def unclamp(self) -> None:
        """
        Remove the clamp boundaries, letting window/area free to move and resize again.
        """
        self._clamp = None

    def fit(self, box: Box | tuple[int, int, int, int]) -> None:
        """
        Re-scale window/area so it fits into box structure.
        """
        if not isinstance(box, Box):
            box = Box(*box)
        self._box = self._onQuery()
        self._box = self._clamp_box(self._box, box)
        self._onSet(self._box)


class PyWinBox(BaseClass):

    def __init__(self,
                 onQuery: Callable[[], Box] | None = None, onSet: Callable[[Box], None] | None = None,
                 handle = None) -> None:
        """
        THIS CLASS IS FOR RETRO-COMPATIBILITY ONLY. Use WindowBox (window area) or ScreenBox (rectangular area) instead.

        Class to access all area/window box properties.

        ## Rectangular areas

        You just need to instantiate the PyWinBox class, passing custom callbacks to be called when any property is
        queried (onQuery) or set (onSet).

            myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet)

        ## Window areas

        To manage window areas, you need to also pass the window handle when instantiating the class, in the following formats:

        - MS-Windows: integer (window id) or str (as returned by, e.g., PyQt's winId() method)
        - Linux: integer (window id) or X-Window object
        - macOS / foreign window: in case you want to manage a window from another application, you must pass target app and window names, as a tuple of strings (appName, windowTitle)
        - macOS / own window: if you want to manage your own application window, you must pass NSWindow() object

        (Search for cross-platform modules if you need a cross-platform handle. For instance, you can get this kind of handles
        using PyWinCtl's getHandle(), getAppName() or title methods)

        In this case, you can use the default, built-in methods to manage the window when its properties are queried or set
        (passing them as None):

        - default OnQuery: Will update the window position and size values when any property is queried
        - default OnSet: Will move and/or resize the window when any property is set

            myBox = pywinbox.PyWinBox(onQuery=None, onSet=None, handle=windowHandle)

        Of course, you can also define (and pass) your own custom functions if you need to perform other actions on these events.

            myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet, handle=windowHandle))

        In this case, if your custom functions do not properly retrieve or set the actual window position and size, the
        information contained in the PyWinBox class, and returned by all properties, will likely become obsolete.

        It can raise ValueError if no parameters or not valid window handle are passed
        """
        warnings.warn('PyWinBox class is deprecated. Use WindowBox (window area) or ScreenBox (rectangular area) instead',
                      DeprecationWarning, stacklevel=2)
        try:
            newHandle = _getHandle(handle) if handle is not None else None
        except Exception:
            newHandle = None
        if newHandle is None and (onSet is None or onQuery is None):
            raise ValueError
        BaseClass.__init__(self, handle=newHandle, onQuery=onQuery, onSet=onSet)


class WindowBox(BaseClass):

    def __init__(self,
                 handle,
                 onQuery: Callable[[], Box] | None = None, onSet: Callable[[Box], None] | None = None) -> None:
        """
        Class to access all window box properties.

        To manage window areas, you need to also pass the window handle when instantiating the class, in the following formats:

        - MS-Windows: integer (window id) or str (as returned by, e.g., PyQt's winId() method)
        - Linux: integer (window id) or X-Window object
        - macOS / foreign window: in case you want to manage a window from another application, you must pass target app and window names, as a tuple of strings (appName, windowTitle)
        - macOS / own window: if you want to manage your own application window, you must pass NSWindow() object

        (Search for cross-platform modules if you need a cross-platform handle. For instance, you can get this kind of handles
        using PyWinCtl's getHandle(), getAppName() or title methods)

        In this case, you can use the default, built-in methods to manage the window when its properties are queried or set
        (passing them as None):

        - default OnQuery: Will update the window position and size values when any property is queried
        - default OnSet: Will move and/or resize the window when any property is set

            myBox = pywinbox.WindowBox(onQuery=None, onSet=None, handle=windowHandle)

        Of course, you can also define (and pass) your own custom functions if you need to perform other actions on these events.

            myBox = pywinbox.WindowBox(onQuery=customOnQuery, onSet=customOnSet, handle=windowHandle)

        In this case, if your custom functions do not properly retrieve or set the actual window position and size, the
        information contained in the WindowBox class, and returned by all properties, will likely become obsolete.

        It can raise ValueError if not valid window handle is passed
        """
        try:
            newHandle = _getHandle(handle)
        except Exception:
            newHandle = None
        if newHandle is None:
            raise ValueError
        BaseClass.__init__(self, handle=newHandle, onQuery=onQuery, onSet=onSet)


class ScreenBox(BaseClass):

    def __init__(self,
                 box: Box | tuple[int, int, int, int],
                 onQuery: Callable[[], Box], onSet: Callable[[Box], None]) -> None:
        """
        Class to access all area box properties.

        You just need to instantiate the ScreenBox class, passing box coordinates and custom callbacks to be invoked
        when any property is queried (onQuery) or set (onSet).

            myBox = pywinbox.ScreenBox((0, 0, 800, 600), customOnQuery, customOnSet)

        It can raise ValueError if wrong parameters are passed.
        """
        if ((not isinstance(box, Box) and (not isinstance(box, tuple) or (isinstance(box, tuple) and len(box) != 4)))
                or not callable(onQuery) or not callable(onSet)):
            raise ValueError
        if not isinstance(box, Box):
            box = Box(*box)
        BaseClass.__init__(self, box=box, onQuery=onQuery, onSet=onSet)


if sys.platform == "darwin":
    from ._pywinbox_macos import (_getHandle, _getWindowBox, _moveResizeWindow)

elif sys.platform == "win32":
    from ._pywinbox_win import (_getHandle, _getWindowBox, _moveResizeWindow)

elif sys.platform == "linux":
    from ._pywinbox_linux import (_getHandle, _getWindowBox, _moveResizeWindow)

else:
    raise NotImplementedError('PyWinBox currently does not support this platform. If you think you can help, please contribute! https://github.com/Kalmat/PyWinBox')
