# PyWinBox
[![CI](https://github.com/Kalmat/PyWinBox/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Kalmat/PyWinBox/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/PyWinBox.svg)](https://badge.fury.io/py/PyWinBox)
[![Documentation Status](https://readthedocs.org/projects/pywinbox/badge/?version=latest)](https://pywinbox.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://static.pepy.tech/badge/pywinbox/month)](https://pepy.tech/project/pywinbox)
[![Stars](https://img.shields.io/github/stars/Kalmat/PyWinBox?style=flat)](https://github.com/Kalmat/PyWinBox/stargazers)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue)](LICENSE.txt)

**Cross-platform Python module to manage window and rectangular screen areas — with full property access, live callbacks, and multi-monitor support.**

PyWinBox gives you a clean, unified interface to read and manipulate the position and size of any window — even one belonging to another application — or any arbitrary rectangle on screen. It is similar to [PyGame.Rect](https://www.pygame.org/docs/ref/rect.html): same familiar geometry API, minus the sprite stuff, plus real window control and callback hooks.

---

## What makes it different?

- **Control any window**, including windows from foreign applications
- **React to events** — custom callbacks fire whenever a property is read or written
- **Multi-monitor aware** — works correctly across complex display setups
- **Two geometry conventions** supported: `Rect` (left, top, right, bottom) and `Box` (left, top, width, height)
- **Convenient named tuples** — `Box`, `Rect`, `Size`, `Point` — for clean, readable code

> **Note on naming:** this module follows the `wintypes.RECT` convention, so `Rect` is `(left, top, right, bottom)` and `Box` is `(left, top, width, height)`.

---

## Table of Contents

1. [Two Use Cases](#two-classes-two-use-cases)
   - [control a window](#-control-a-window)
   - [control any rectangular area](#control-any-rectangular-area)
2. [Callback Rules](#callback-rules)
   - [Default Callbacks](#default-callbacks)
   - [Custom Callbacks](#custom-callbacks)
3. [Window Handle Formats](#window-handle-formats)
4. [Class Properties](#class-properties)
5. [Data Structs](#data-structs)
6. [Install](#install)
7. [Support](#support)
8. [Contributing](#contributing)
9. [Running the Tests](#running-the-tests)

---

## Two Use Cases

`PyWinBox` has two ways to be invoked. Which one you need depends on what you want to control.

---

### control a window

Use this way when you want to manage the position and size of an **existing window** — your own or one from another application.

**Required:** a window handle (see [Window Handle Formats](#window-handle-formats))  
**Callbacks:** optional — default ones are built in

```python
# Minimal usage: let PyWinBox handle everything automatically
myBox = pywinbox.PyWinBox(handle=windowHandle, onQuery=None, onSet=None)

# With your own callbacks for custom behavior
myBox = pywinbox.PyWinBox(handle=windowHandle, onQuery=customOnQuery, onSet=customOnSet)
```

When `onQuery=None` and `onSet=None`, the built-in defaults kick in: they automatically read the current window geometry when any property is queried, and move/resize the window when any property is set. No manual sync needed.

If you provide your own callbacks, make sure they follow the [Callback Rules](#callback-rules) below.

---

### control any rectangular area

Use this way when you want to track and manipulate **any rectangle on screen** — not tied to a specific window. This is useful for defining regions of interest, screen zones, or custom overlays.

**Required both callbacks** (they are mandatory here, since there is no window to fall back on)

Without valid callbacks, the struct will have no way to read or write its own state, so it will be empty and useless. Make sure your callbacks follow the [Callback Rules](#callback-rules) below.

Don't forget to set the screen area geometry. You can do this at any time, but do this at least once before start working with the area.

```python
myBox = pywinbox.PyWinBox(onQuery=customOnQuery, onSet=customOnSet)
myBox.size = (800, 600)
myBox.position = (50, 50)
```

---

## Callback Rules

Both classes use two callback hooks:

| Callback  | When it fires               | What it must do                                      |
|-----------|-----------------------------|------------------------------------------------------|
| `onQuery` | Any property is **read**    | Return the current geometry as a `Box` named tuple   |
| `onSet`   | Any property is **written** | Apply the new geometry (move/resize the area)        |

### Default Callbacks

Only available with window areas (requires a window handle). Pass `None` to use them:

| Callback          | Behavior                                                 |
|-------------------|----------------------------------------------------------|
| default `onQuery` | Reads the current window position and size from the OS   |
| default `onSet`   | Moves and/or resizes the window via the OS               |

### Custom Callbacks

You can supply your own functions to extend or replace the default behavior. If you do so, **your callbacks are fully responsible for reading and writing the geometry** — failing to do this correctly will cause PyWinBox's internal state to drift out of sync with reality.

To keep things in sync while still adding custom logic, you **MUST call** the built-in methods from within your own callbacks:

```python
def customOnQuery():
    currBox = myBox.onQuery()   # Reads the actual current geometry
    # ... your additional logic here ...
    return currBox              # Must return a Box named tuple

def customOnSet(newBox: Box):
    # ... your additional logic here ...
    myBox.onSet(newBox)         # Actually applies the new geometry to window or screen area
```

> **Key rule:** `onQuery` must always return a valid `Box` named tuple. `onSet` receives one as its argument and must apply it.

---

## Window Handle Formats

`PyWinBox` accepts window handles in different formats depending on the platform:

| Platform                   | Handle format                                                     |
|----------------------------|-------------------------------------------------------------------|
| **Windows**                | `int` (window id) or `str` (e.g. as returned by PyQt's `winId()`) |
| **Linux**                  | `int` (window id) or `X-Window` object                            |
| **macOS — foreign window** | `tuple` of strings: `(appName, windowTitle)`                      |
| **macOS — own window**     | `NSWindow` object                                                 |

Need a cross-platform way to get a handle? Check out PyWinCtl's [`getHandle()`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#gethandle), [`getAppName()`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#getappname) or [`title`](https://github.com/Kalmat/PyWinCtl/blob/master/docstrings.md#title).

---

## Class Properties

All properties are readable and writable. Reading triggers `onQuery`; writing triggers `onSet`.

| Property                                           | Description                      |
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

`PyWinBox` provides named tuples to make geometry values easy to pass around and destructure:

| Struct  | Fields                     |
|---------|----------------------------|
| `Box`   | `left, top, width, height` |
| `Rect`  | `left, top, right, bottom` |
| `Size`  | `width, height`            |
| `Point` | `x, y`                     |

---

## Install

```bash
python -m pip install pywinbox
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add pywinbox
```

Alternatively, download the `.whl` from [PyPI](https://pypi.org/project/PyWinBox/#files) or the [dist folder](https://github.com/Kalmat/PyWinBox/tree/master/dist) and install it manually (replace `x.x.xx` with the actual version):

```bash
python -m pip install PyWinBox-x.x.xx-py3-none-any.whl
```

Then import it in your project:

```python
import pywinbox
```

---

## Support

Found a bug? Have a question or suggestion? [Open an issue](https://github.com/Kalmat/PyWinBox/issues) on the project's GitHub page.

---

## Contributing

Want to use this code or contribute to it?

- Fork the [repository](https://github.com/Kalmat/PyWinBox), or
- [Download a ZIP](https://github.com/Kalmat/PyWinBox/archive/refs/heads/master.zip), unzip, and open it in your IDE

Install dev dependencies with:

```bash
uv sync
```

Or the traditional way:

```bash
python -m venv .venv
python -m pip install -e . --group=dev
```

---

## Running the Tests

Navigate to the `tests` folder and run:

```bash
uv run test_pywinbox.py
```

For macOS NSWindow testing:

```bash
uv run test_MacNSBox.py
```
