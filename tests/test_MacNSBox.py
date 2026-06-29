#!/usr/bin/env python
# Lawrence Akka - https://sourceforge.net/p/pyobjc/mailman/pyobjc-dev/thread/0B4BC391-6491-445D-92D0-7B1CEF6F51BE%40me.com/#msg27726282

import os
import sys
import time
import traceback

import pywinbox

# We need to import the relevant object definitions from PyObjC
from AppKit import (
    NSApp, NSObject, NSApplication, NSMakeRect, NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable, NSBackingStoreBuffered)


# Cocoa prefers composition to inheritance. The members of an object's
# delegate will be called upon the happening of certain events. Once we define
# methods with particular names, they will be called automatically
class Delegate(NSObject):

    npw = None

    def applicationSupportsSecureRestorableState_(self, app) -> bool:
        return True

    def applicationDidFinishLaunching_(self, aNotification: None) -> None:
        '''Called automatically when the application has launched'''
        # PyObjC swallows exceptions raised inside delegate callbacks (only logging the type),
        # so the window would never close and the app would hang forever.
        # Catch everything, print the traceback, and force-exit nonzero so the test fails fast.
        # We can't use NSApp().terminate_() (it exits 0) nor sys.exit() (SystemExit isn't an
        # Exception subclass, so PyObjC swallows it too): os._exit() is the only reliable path.
        try:
            self._runChecks()
        except Exception:
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(1)

    def _runChecks(self) -> None:
        # Set it as the frontmost application
        NSApp().activateIgnoringOtherApps_(True)

        handle = None
        for win in NSApp().orderedWindows():
            handle = win
            print(win.title(), win.frame(), type(win.frame().origin))
        print()
        assert handle is not None

        myPyBox = pywinbox.WindowBox(handle=handle, onQuery=None, onSet=None)

        # macOS won't let a window's top edge rise above the menu bar, so any
        # target whose top edge exceeds the usable screen height gets clamped.
        # CI runners have a small headless display, so derive bottom targets
        # from the actual screen height instead of assuming a tall desktop.
        screenH = int(handle.screen().frame().size.height)
        print("SCREEN", handle.screen().frame())
        lowBottom = min(700, screenH - 100)

        timelap = 0.3

        print("MOVE left = 200", myPyBox.box, myPyBox.rect)
        myPyBox.left = 200
        time.sleep(timelap)
        assert myPyBox.left == 200

        print("MOVE right = 200", myPyBox.box, myPyBox.rect)
        myPyBox.right = 200
        time.sleep(timelap)
        assert myPyBox.right == 200

        print("MOVE top = 200", myPyBox.box, myPyBox.rect)
        myPyBox.top = 200
        time.sleep(timelap)
        assert myPyBox.top == 200

        print(f"MOVE bottom = {lowBottom}", myPyBox.box, myPyBox.rect)
        myPyBox.bottom = lowBottom
        time.sleep(timelap)
        assert myPyBox.bottom == lowBottom

        print("MOVE topleft = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.topleft = (300, 400)
        time.sleep(timelap)
        assert myPyBox.topleft == (300, 400)

        print("MOVE topright = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.topright = (300, 400)
        time.sleep(timelap)
        assert myPyBox.topright == (300, 400)

        print(f"MOVE bottomleft = (300, {lowBottom})", myPyBox.box, myPyBox.rect)
        myPyBox.bottomleft = (300, lowBottom)
        time.sleep(timelap)
        assert myPyBox.bottomleft == (300, lowBottom)

        print("MOVE bottomright = (1000, 200)", myPyBox.box, myPyBox.rect)
        myPyBox.bottomright = (1000, 200)
        time.sleep(timelap)
        assert myPyBox.bottomright == (1000, 200)

        print("MOVE midleft = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.midleft = (300, 400)
        time.sleep(timelap)
        assert myPyBox.midleft == (300, 400)

        print("MOVE midright = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.midright = (300, 400)
        time.sleep(timelap)
        assert myPyBox.midright == (300, 400)

        print("MOVE midtop = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.midtop = (300, 400)
        time.sleep(timelap)
        assert myPyBox.midtop == (300, 400)

        print(f"MOVE midbottom = (300, {lowBottom})", myPyBox.box, myPyBox.rect)
        myPyBox.midbottom = (300, lowBottom)
        time.sleep(timelap)
        assert myPyBox.midbottom == (300, lowBottom)

        print("MOVE center = (300, 400)", myPyBox.box, myPyBox.rect)
        myPyBox.center = (300, 400)
        time.sleep(timelap)
        assert myPyBox.center == (300, 400)

        print("MOVE centerx = 1000", myPyBox.box, myPyBox.rect)
        myPyBox.centerx = 1000
        time.sleep(timelap)
        assert myPyBox.centerx == 1000

        print("MOVE centery = 300", myPyBox.box, myPyBox.rect)
        myPyBox.centery = 300
        time.sleep(timelap)
        assert myPyBox.centery == 300

        print("RESIZE width = 600", myPyBox.size)
        myPyBox.width = 600
        time.sleep(timelap)
        assert myPyBox.width == 600

        print("RESIZE height = 400", myPyBox.size)
        myPyBox.height = 400
        time.sleep(timelap)
        assert myPyBox.height == 400

        print("RESIZE size = (810, 610)", myPyBox.size)
        myPyBox.size = (810, 610)
        time.sleep(timelap)
        assert myPyBox.size == (810, 610)

        # Test closing
        print("CLOSE")
        win.close()

    def windowWillClose_(self, aNotification: None) -> None:
        '''Called automatically when the window is closed'''
        print("Window has been closed")
        # Terminate the application
        NSApp().terminate_(self)

    def windowDidBecomeKey_(self, aNotification: None) -> None:
        print("Now I'm ACTIVE")


def demo() -> None:
    # Create a new application instance ...
    a = NSApplication.sharedApplication()
    # ... and create its delegate.  Note the use of the
    # Objective C constructors below, because Delegate
    # is a subclass of an Objective C class, NSObject
    delegate: Delegate = Delegate.alloc().init()
    # Tell the application which delegate object to use.
    a.setDelegate_(delegate)

    # Now we can start to create the window ...
    frame = NSMakeRect(400, 400, 250, 128)
    # (Don't worry about these parameters for the moment. They just specify
    # the type of window, its size and position etc)
    mask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable
    w = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(frame, mask, NSBackingStoreBuffered, False)

    # ... tell it which delegate object to use (here it happens
    # to be the same delegate as the application is using)...
    w.setDelegate_(delegate)
    # ... and set some properties. Unicode strings are preferred.
    w.setTitle_('Hello, World!')
    # All set. Now we can show the window ...
    w.orderFrontRegardless()

    # ... and start the application
    # On success the window closes -> windowWillClose_ -> terminate_ (exits 0).
    # On failure _runChecks' handler calls os._exit(1). Either way control does not
    # return here, so there's nothing to do after a.run().
    a.run()
    #AppHelper.runEventLoop()


if __name__ == '__main__':
    demo()
