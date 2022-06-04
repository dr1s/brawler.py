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

from screeninfo import get_monitors

from brawler.logging import log

monitors = get_monitors()


def calculate_offset():
    log.debug("calculating screen offset, if there are multiple monitors")
    offset = 0
    if len(monitors) > 1:
        for m in monitors:
            if m.x > 0 and m.is_primary:
                offset = m.x
                log.debug("offset found: {}".format(offset))
    return offset


def get_primary_resolution():
    res_x = 0
    res_y = 0

    for m in monitors:
        if m.is_primary:
            res_x = m.width
            res_y = m.height

    log.debug("screen size: {}x{}".format(res_x, res_y))
    return res_x, res_y
