# PyWinBox

[![Type Checking](https://github.com/Kalmat/PyWinBox/actions/workflows/type-checking.yml/badge.svg)](https://github.com/Kalmat/PyWinBox/actions/workflows/type-checking.yml)
[![PyPI version](https://badge.fury.io/py/PyWinBox.svg)](https://badge.fury.io/py/PyWinBox)


Cross-Platform and multi-monitor module which allows to manage window areas (position and
size) and all their properties, as well as any rectangular area.

## Rectangular areas

You just need to instantiate the PyWinBox class, passing custom callbacks to be called when any property is 
queried (onQuery) or set (onSet).

    myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet)

For rectangular areas, it is necessary to pass custom (not default) callbacks which actually manage the box struct values, 
or the struct will be empty and useless.

## Window areas

To manage window areas, you need to also pass the window handle when instantiating the class, in the following formats:

- MS-Windows: integer (window id) or str (as returned by, e.g., PyQt's winId() method)
- Linux: integer (window id) or X-Window object
- macOS / foreign window: in case you want to manage a window from another application, you must pass target app and window names, as a tuple of strings (appName, windowTitle)
- macOS / own window: if you want to manage your own application window, you must pass NSWindow() object

(Search for cross-platform modules if you need a cross-platform handle. For instance, you can get this kind of handles
using PyWinCtl's getHandle(), getAppName() or title methods)

In this case, you can use the default methods to manage the window when its properties are queried or set: 

- default OnQuery: Will update the window position and size values when any property is queried
- default OnSet: Will move and/or resize the window when any property is set

To use default methods, just pass them as None, like this: 

    myBox = pywinbox.PyWinBox(onQuery=None, onSet=None, handle=windowHandle)

Of course, you can also define (and pass) your own custom functions if you need to perform other actions on these events.

In this case, if your custom functions do not properly retrieve or set the actual window position and size, the 
information contained in the PyWinBox class, and returned by all properties, will likely become obsolete. So, you can
use both in your custom callback:

    def customOnQuery():
        currBox = myBox.onQuery()  # This will retrieve the current window's box
        # ... do your stuff ...
        return currBox

    def customOnSet(newBox: Box):
        myBox.onSet(newBox)  # This will actually move/resize the window
        # ... do your stuff ...

    myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet, handle=windowHandle)


## Class Properties

    left, top, right, bottom

    size, width, height

    topleft, bottomleft, topright, bottomright

    midtop, midleft, midbottom, midright

    center, centerx, centery

    box (left, top, width, height)

    rect (left, top, right, bottom)


## Data Structs

These are useful data structs (named tuples, actually) you can use to better manage the values:

    Box:    left, top, width, height
    Rect:   left, top, right, bottom
    Size:   width, height
    Point:  x, y


## INSTALL <a name="install"></a>

To install this module on your system, you can use pip: 

    pip3 install pywinbox

or

    python3 -m pip install pywinbox

Alternatively, you can download the wheel file (.whl) available in the [Download page](https://pypi.org/project/PyWinBox/#files) and the [dist folder](https://github.com/Kalmat/PyWinBox/tree/master/dist), and run this (don't forget to replace 'x.x.xx' with proper version number):

    pip install PyWinBox-x.x.xx-py3-none-any.whl

You may want to add `--force-reinstall` option to be sure you are installing the right dependencies version.

Then, you can use it on your own projects just importing it:

    import pywinbox

## SUPPORT <a name="support"></a>

In case you have a problem, comments or suggestions, do not hesitate to [open issues](https://github.com/Kalmat/PyWinBox/issues) on the [project homepage](https://github.com/Kalmat/PyWinBox)

## USING THIS CODE <a name="using"></a>

If you want to use this code or contribute, you can either:

* Create a fork of the [repository](https://github.com/Kalmat/PyWinBox), or 
* [Download the repository](https://github.com/Kalmat/PyWinBox/archive/refs/heads/master.zip), uncompress, and open it on your IDE of choice (e.g. PyCharm)

Be sure you install all dependencies described on "docs/requirements.txt" by using pip

## TEST <a name="test"></a>

To test this module on your own system, cd to "tests" folder and run:

    python3 test_pywinbox.py

For macOS NSWindow, you can also test using:

    python3 test_MacNSBox.py
