#!/usr/bin/python

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import TypedDict

import pywinbox
import pywinctl as pwc


class GetWindowKwargs(TypedDict):
    title: str
    condition: int


def test_basic() -> None:
    if sys.platform == "win32":
        process = "notepad"
        get_window_kwargs: GetWindowKwargs = {
            "title": "Notepad|Bloc de notas",
            "condition": pwc.Re.MATCH,
        }
    elif sys.platform == "linux":
        process = "gedit"
        get_window_kwargs: GetWindowKwargs = {
            "title": "gedit",
            "condition": pwc.Re.ENDSWITH,
        }
    elif sys.platform == "darwin":
        if not pwc.checkPermissions(activate=True):
            exit()
        process = ["open", "-a", "TextEdit", __file__]
        get_window_kwargs: GetWindowKwargs = {
            "title": os.path.basename(__file__),
            "condition": pwc.Re.IS,
        }
    else:
        raise NotImplementedError(
            "PyWinBox currently does not support this platform. "
            + "If you have useful knowledge, please contribute! https://github.com/Kalmat/PyWinBox"
        )

    subprocess.Popen(process)

    testWindows: list[pwc.Window] = []
    deadline = time.time() + 15
    while not testWindows and time.time() < deadline:
        time.sleep(0.5)
        testWindows = pwc.getWindowsWithTitle(**get_window_kwargs)
    assert len(testWindows) == 1

    npw = testWindows[0]
    wait = True
    timelap = 0.5

    # Test maximize/minimize/restore.
    if npw.isMaximized:  # Make sure it starts un-maximized
        npw.restore(wait=wait)
    assert not npw.isMaximized
    
    npw.size = (600, 400)

    if sys.platform == "darwin":
        myPyBox = pywinbox.WindowBox(handle=(npw.getAppName(), npw.title or ""), onQuery=None, onSet=None)
    else:
        myPyBox = pywinbox.WindowBox(handle=npw.getHandle(), onQuery=None, onSet=None)

    print("INIT", npw.box, npw.rect)

    myPyBox.left = 250
    time.sleep(timelap)
    print("LEFT", npw.box, npw.rect)
    assert npw.left == 250

    myPyBox.right = 950
    time.sleep(timelap)
    print("RIGHT", npw.box, npw.rect)
    assert npw.right == 950

    myPyBox.top = 150
    time.sleep(timelap)
    print("TOP", npw.box, npw.rect)
    assert npw.top == 150

    myPyBox.bottom = 775
    time.sleep(timelap)
    print("BOTTOM", npw.box, npw.rect)
    assert npw.bottom == 775

    myPyBox.topleft = (155, 350)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.topleft == (155, 350)

    myPyBox.topright = (1000, 300)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.topright == (1000, 300)

    myPyBox.bottomleft = (300, 975)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.bottomleft == (300, 975)

    myPyBox.bottomright = (1000, 900)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.bottomright == (1000, 900)

    myPyBox.midleft = (300, 400)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.midleft == (300, 400)

    myPyBox.midright = (1050, 600)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.midright == (1050, 600)

    myPyBox.midtop = (500, 350)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.midtop == (500, 350)

    myPyBox.midbottom = (500, 800)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.midbottom == (500, 800)

    myPyBox.center = (500, 350)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.center == (500, 350)

    myPyBox.centerx = 1000
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.centerx == 1000

    myPyBox.centery = 600
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.centery == 600

    myPyBox.width = 700
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.width == 700

    myPyBox.height = 400
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.height == 400

    myPyBox.size = (551, 401)
    time.sleep(timelap)
    print(npw.box, npw.rect)
    assert npw.size == (551, 401)

    # Test closing
    npw.close()


def main() -> None:
    test_basic()


if __name__ == '__main__':
    main()
