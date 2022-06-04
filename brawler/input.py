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

from Xlib import X
from Xlib.XK import keysym_to_string
from Xlib.ext import record
from Xlib.display import Display
from Xlib.protocol import rq

from brawler.logging import log


class duplicator:
    def __init__(self, clients, keys):
        self.clients = clients
        self.keys = keys
        self.disp = Display()
        self.root = self.disp.screen().root
        self.ctx = self.disp.record_create_context(
            0,
            [record.AllClients],
            [
                {
                    "core_requests": (0, 0),
                    "core_replies": (0, 0),
                    "ext_requests": (0, 0, 0, 0),
                    "ext_replies": (0, 0, 0, 0),
                    "delivered_events": (0, 0),
                    "device_events": (X.KeyReleaseMask, X.ButtonReleaseMask),
                    "errors": (0, 0),
                    "client_started": False,
                    "client_died": False,
                }
            ],
        )
        self.disp.record_enable_context(self.ctx, self.duplicate)
        self.disp.record_free_context(self.ctx)

    def listen(self):
        # start listening for next key event
        event = self.root.display.next_event()

    def decode_keycode(self, keycode):
        # try to decode the keycode to a string
        key_string = keysym_to_string(self.disp.keycode_to_keysym(keycode, 2))
        # if we happen to look for a specific keycode replace the key string
        if keycode == 36:
            key_string = "Enter"
        elif keycode == 65:
            key_string = "space"
        return key_string

    def duplicate(self, reply):
        # duplicate the key input to all clients
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data, self.disp.display, None, None
            )
            if event.type == X.KeyPress:
                key_string = self.decode_keycode(event.detail)
                log.debug("Pressed key: {}, code: {}".format(key_string, event.detail))
                if key_string in self.keys:
                    # Only sent the duplicated keys to the toons, so we need to exclude 0
                    for c in self.clients[1:]:
                        c.send_key(key_string)
