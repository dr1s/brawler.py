# Copyright (c) 2022 Daniel Schmitz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from shlex import quote
from brawler.process import execute
from brawler.logging import log


def get_window(name):
    log.debug("searching for window: {}".format(name))
    result = execute("xdotool search --name {}".format(quote(name)))
    if result is not None:
        result = result[0]
        log.debug("window found: {}".format(result))

    return result


def get_child_window(parent, name):
    log.debug("trying to find child window for {} {}".format(parent, name))
    result = execute(
        "xwininfo -children -id {} | grep {}".format(quote(parent), quote(name))
    )

    if result is not None:
        result = result[0]
        log.debug("window for parent {} found: {}".format(parent, result))
    return result


def windowsize(window, resolution_x, resolution_y):
    log.debug("changing window size: {}x{}".format(resolution_x, resolution_y))
    execute(
        "xdotool windowsize {} {} {}".format(
            quote(window), int(resolution_x), int(resolution_y)
        )
    )


def windowmove(window, position_x, position_y):
    log.debug("moving window to position: {} {}".format(position_x, position_y))
    execute(
        "xdotool windowmove {} {} {}".format(
            quote(window), int(position_x), int(position_y)
        )
    )


def undecorate(window):
    log.debug("trying to undecorate window {}".format(window))
    execute(
        "xprop -id {} -f _MOTIF_WM_HINTS 32c -set _MOTIF_WM_HINTS '0x2, 0x0, 0x0, 0x0, 0x0'".format(
            quote(window)
        )
    )


def send_key(window, key):
    log.debug("send key {} to window: {}".format(key, window))
    execute("xdotool key --window {} {}".format(quote(window), key))


def get_window_pid(window):
    log.debug("trying to find pid for window {}".format(window))
    result = execute("xprop -id {} _NET_WM_PID".format(window))
    if len(result) > 2:
        return int(result[2])
