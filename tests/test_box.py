#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
import sys
import time

import pybox
import pywinctl  # type: ignore[import]


def test_basic():

    npw = None

    if sys.platform == "win32":
        subprocess.Popen('notepad')
        time.sleep(0.5)

        npw = pywinctl.getActiveWindow()

    elif sys.platform == "linux":
        subprocess.Popen('gedit')
        time.sleep(5)

        npw = pywinctl.getActiveWindow()

    elif sys.platform == "darwin":
        if not pywinctl.checkPermissions(activate=True):
            exit()
        subprocess.Popen(['touch', 'test.py'])
        time.sleep(2)
        subprocess.Popen(['open', '-a', 'TextEdit', 'test.py'])
        time.sleep(5)

        windows = pywinctl.getWindowsWithTitle('test.py')
        if windows:
            npw = windows[0]

    if npw is not None:

        wait = True
        timelap = 0.5

        # Test maximize/minimize/restore.
        if npw.isMaximized:  # Make sure it starts un-maximized
            npw.restore(wait=wait)
        assert not npw.isMaximized

        handle = npw.getHandle()
        if sys.platform == "darwin" and pywinctl.version() < "0.1":
            handle = (npw.getAppName(), npw.title)

        myPyBox = pybox.PyBox(onQuery=pybox.defaultOnQuery, onSet=pybox.defaultOnSet, handle=handle)

        myPyBox.left = 250
        time.sleep(timelap)
        assert npw.left == 250

        myPyBox.right = 950
        time.sleep(timelap)
        assert npw.right == 950

        myPyBox.top = 150
        time.sleep(timelap)
        assert npw.top == 150

        myPyBox.bottom = 775
        time.sleep(timelap)
        assert npw.bottom == 775

        myPyBox.topleft = (155, 350)
        time.sleep(timelap)
        assert npw.topleft == (155, 350)

        myPyBox.topright = (1000, 300)
        time.sleep(timelap)
        assert npw.topright == (1000, 300)

        myPyBox.bottomleft = (300, 975)
        time.sleep(timelap)
        assert npw.bottomleft == (300, 975)

        myPyBox.bottomright = (1000, 900)
        time.sleep(timelap)
        assert npw.bottomright == (1000, 900)

        myPyBox.midleft = (300, 400)
        time.sleep(timelap)
        assert npw.midleft == (300, 400)

        myPyBox.midright = (1050, 600)
        time.sleep(timelap)
        assert npw.midright == (1050, 600)

        myPyBox.midtop = (500, 350)
        time.sleep(timelap)
        assert npw.midtop == (500, 350)

        myPyBox.midbottom = (500, 800)
        time.sleep(timelap)
        assert npw.midbottom == (500, 800)

        myPyBox.center = (500, 350)
        time.sleep(timelap)
        assert npw.center == (500, 350)

        myPyBox.centerx = 1000
        time.sleep(timelap)
        assert npw.centerx == 1000

        myPyBox.centery = 600
        time.sleep(timelap)
        assert npw.centery == 600

        myPyBox.width = 700
        time.sleep(timelap)
        assert npw.width == 700

        myPyBox.height = 500
        time.sleep(timelap)
        assert npw.height == 500

        myPyBox.size = (801, 601)
        time.sleep(timelap)
        assert npw.size == (801, 601)

        # Test closing
        npw.close()


def main():
    test_basic()


if __name__ == '__main__':
    main()
