#!/usr/bin/env python
# encoding: utf-8

# Lawrence Akka - https://sourceforge.net/p/pyobjc/mailman/pyobjc-dev/thread/0B4BC391-6491-445D-92D0-7B1CEF6F51BE%40me.com/#msg27726282

# We need to import the relevant object definitions from PyObjC

import sys

import pybox

assert sys.platform == "darwin"

import time

from AppKit import (
    NSApp, NSObject, NSApplication, NSMakeRect, NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable, NSBackingStoreBuffered)

import pywinctl  # type ignore[import]


# Cocoa prefers composition to inheritance. The members of an object's
# delegate will be called upon the happening of certain events. Once we define
# methods with particular names, they will be called automatically
class Delegate(NSObject):

    npw = None
    demoMode = False

    def getDemoMode(self):
        return self.demoMode

    def setDemoMode(self):
        self.demoMode = True

    def unsetDemoMode(self):
        self.demoMode = False

    def applicationDidFinishLaunching_(self, aNotification: None):
        '''Called automatically when the application has launched'''
        # Set it as the frontmost application
        NSApp().activateIgnoringOtherApps_(True)
        for win in NSApp().orderedWindows():
            print(win.title(), win.frame(), type(win.frame().origin))

        if self.demoMode:

            win = pywinctl.getActiveWindow(NSApp())

            if win:
                print("ACTIVE WINDOW:", win.title)

                myPyBox = pybox.PyBox(onQuery=pybox.defaultOnQuery, onSet=pybox.defaultOnSet, handle=win.getHandle())

            else:
                print("NO ACTIVE WINDOW FOUND")
                return

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

            print("MOVE bottom = 800", myPyBox.box, myPyBox.rect)
            myPyBox.bottom = 800
            time.sleep(timelap)
            assert myPyBox.bottom == 800

            print("MOVE topleft = (300, 400)", myPyBox.box, myPyBox.rect)
            myPyBox.topleft = (300, 400)
            time.sleep(timelap)
            assert myPyBox.topleft == (300, 400)

            print("MOVE topright = (300, 400)", myPyBox.box, myPyBox.rect)
            myPyBox.topright = (300, 400)
            time.sleep(timelap)
            assert myPyBox.topright == (300, 400)

            print("MOVE bottomleft = (300, 700)", myPyBox.box, myPyBox.rect)
            myPyBox.bottomleft = (300, 700)
            time.sleep(timelap)
            assert myPyBox.bottomleft == (300, 700)

            print("MOVE bottomright = (300, 900)", myPyBox.box, myPyBox.rect)
            myPyBox.bottomright = (300, 900)
            time.sleep(timelap)
            assert myPyBox.bottomright == (300, 900)

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

            print("MOVE midbottom = (300, 700)", myPyBox.box, myPyBox.rect)
            myPyBox.midbottom = (300, 700)
            time.sleep(timelap)
            assert myPyBox.midbottom == (300, 700)

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
            myPyBox.close()

    def windowWillClose_(self, aNotification: None):
        '''Called automatically when the window is closed'''
        print("Window has been closed")
        # Terminate the application
        NSApp().terminate_(self)

    def windowDidBecomeKey_(self, aNotification: None):
        print("Now I'm ACTIVE")


def demo():
    # Create a new application instance ...
    a = NSApplication.sharedApplication()
    # ... and create its delegate.  Note the use of the
    # Objective C constructors below, because Delegate
    # is a subclass of an Objective C class, NSObject
    delegate = Delegate.alloc().init()
    delegate.setDemoMode()
    # Tell the application which delegate object to use.
    a.setDelegate_(delegate)

    # Now we can start to create the window ...
    frame = NSMakeRect(400, 400, 250, 100)
    # (Don't worry about these parameters for the moment. They just specify
    # the type of window, its size and position etc)
    mask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable
    w = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(frame, mask, NSBackingStoreBuffered, False)

    # ... tell it which delegate object to use (here it happens
    # to be the same delegate as the application is using)...
    w.setDelegate_(delegate)
    # ... and set some properties. Unicode strings are preferred.
    w.setTitle_(u'Hello, World!')
    # All set. Now we can show the window ...
    w.orderFrontRegardless()

    # ... and start the application
    a.run()
    #AppHelper.runEventLoop()


if __name__ == '__main__':
    demo()
