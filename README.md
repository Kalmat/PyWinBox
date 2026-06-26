# PyWinBox
[![CI](https://github.com/Kalmat/PyWinBox/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Kalmat/PyWinBox/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/PyWinBox.svg)](https://badge.fury.io/py/PyWinBox)
[![Documentation Status](https://readthedocs.org/projects/pywinbox/badge/?version=latest)](https://pywinbox.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://static.pepy.tech/badge/pywinbox/month)](https://pepy.tech/project/pywinbox)
[![Stars](https://img.shields.io/github/stars/Kalmat/PyWinBox?style=flat)](https://github.com/Kalmat/PyWinBox/stargazers)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue)](LICENSE.txt)

Cross-Platform module which allows to manage window areas (position and size) and all their properties, as well as any rectangular area on screen.

PyWinBox is similar to [PyGame.Rect](https://www.pygame.org/docs/ref/rect.html) object, but extended with some useful features:

- Supports window areas, even if the window belongs to a foreign application
- Invokes custom callbacks whenever any area property is queried or changed
- Works in multi-monitor setups
- Manages both Rect and Box structs
- Provides convenient named-tuple structs to ease handling geometry properties and their attributes

---

1. [Rectangular Areas](#rectangular-areas)
2. [Window Areas](#window-areas)
   1. [Window Handle Formats](#window-handle-formats)
   2. [Default Callbacks](#default-callbacks)
   3. [Custom Callbacks](#custom-callbacks)
3. [Class Properties](#class-properties)
4. [Data Structs](#data-structs)
5. [Install](#install)
6. [Support](#support)
7. [Using this code](#using-this-code)
8. [Test](#test)

## Rectangular Areas

You just need to instantiate the `PyWinBox` class, passing custom callbacks to be called when any property is
queried (`onQuery`) or set (`onSet`).

```python
myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet)
```

For rectangular areas, it is necessary to pass custom (not default) callbacks which actually manage the box struct
values, or the struct will be empty and/or useless.

## Window Areas

To manage window areas, you need to also pass the window handle when instantiating the class.

### Window Handle Formats

| Platform | Handle format |
|---|---|
| **MS-Windows** | `int` (window id) or `str` (as returned by e.g. PyQt's `winId()` method) |
| **Linux** | `int` (window id) or `X-Window` object |
| **macOS / foreign window** | `tuple` of strings `(appName, windowTitle)` — to manage a window from another application |
| **macOS / own window** | `NSWindow` object — to manage your own application window |

> Search for cross-platform modules if you need a cross-platform handle. For instance, you can obtain handles using
> PyWinCtl's [`getHandle()`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#gethandle),
> [`getAppName()`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#getappname) or
> [`title`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#title) methods.

### Default Callbacks

When a window handle is provided, you can use the built-in default methods by passing `None`:

| Callback             | Behavior                                                                 |
|----------------------|--------------------------------------------------------------------------|
| **default onQuery**  | Updates the window position and size values when any property is queried |
| **default onSet**    | Moves and/or resizes the window when any property is set                 |

```python
myBox = pywinbox.PyWinBox(onQuery=None, onSet=None, handle=windowHandle)
```

### Custom Callbacks

You can define and pass your own callback functions if you need to perform additional actions on these events.

> **Important:** If your custom functions do not properly retrieve or set the actual window position and size,
> the information contained in the PyWinBox class — and returned by all properties — will likely become obsolete.

You can call the built-in methods from within your custom callbacks to keep the struct in sync:

```python
def customOnQuery():
    currBox = myBox.onQuery()  # Retrieves the current window's box
    # ... do your stuff ...
    return currBox

def customOnSet(newBox: Box):
    myBox.onSet(newBox)  # Actually moves/resizes the window
    # ... do your stuff ...

myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet, handle=windowHandle)
```

---

## Class Properties

All position and size properties are readable and writable. Setting any property will trigger the `onSet` callback;
reading any property will trigger the `onQuery` callback.

| Properties                                         | Description                      |
|----------------------------------------------------|----------------------------------|
| `left`, `top`, `right`, `bottom`                   | Individual edge coordinates      |
| `width`, `height`                                  | Dimensions                       |
| `size`                                             | `(width, height)`                |
| `topleft`, `topright`, `bottomleft`, `bottomright` | Corner coordinates as `(x, y)`   |
| `midtop`, `midleft`, `midbottom`, `midright`       | Mid-edge coordinates as `(x, y)` |
| `center`                                           | Center point as `(x, y)`         |
| `centerx`, `centery`                               | Individual center coordinates    |
| `box`                                              | `(left, top, width, height)`     |
| `rect`                                             | `(left, top, right, bottom)`     |

---

## Data Structs

These named tuples provide a convenient way to manage and pass geometry values throughout your code:

| Struct  | Fields                     |
|---------|----------------------------|
| `Box`   | `left, top, width, height` |
| `Rect`  | `left, top, right, bottom` |
| `Size`  | `width, height`            |
| `Point` | `x, y`                     |

---

## Install

To install this module on your system, you can use pip:

```
python -m pip install pywinbox
```

or using uv:

```
uv add pywinbox
```

Alternatively, you can download the wheel file (.whl) available in the [Download page](https://pypi.org/project/PyWinBox/#files) and the [dist folder](https://github.com/Kalmat/PyWinBox/tree/master/dist), and run this (don't forget to replace 'x.x.xx' with the proper version number):

```
python -m pip install PyWinBox-x.x.xx-py3-none-any.whl
```

You may want to add `--force-reinstall` to be sure you are installing the right dependencies version.

Then, you can use it on your own projects just importing it:

```python
import pywinbox
```

---

## Support

In case you have a problem, comments or suggestions, do not hesitate to [open issues](https://github.com/Kalmat/PyWinBox/issues) on the [project homepage](https://github.com/Kalmat/PyWinBox).


## Using this code

If you want to use this code or contribute, you can either:

- Create a fork of the [repository](https://github.com/Kalmat/PyWinBox), or
- [Download the repository](https://github.com/Kalmat/PyWinBox/archive/refs/heads/master.zip), uncompress, and open it on your IDE of choice (e.g. PyCharm)

Be sure you install all dev dependencies by running:

```
uv sync
```

or

```
python -m venv .venv
python -m pip install -e . --group=dev
```

## Test

To test this module on your own system, cd to the `tests` folder and run:

```
uv run test_pywinbox.py
```

For macOS NSWindow, you can also test using:

```
uv run test_MacNSBox.py
```
