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

import os
import time
import signal
import threading
from brawler.process import (
    execute,
    shell,
)
from brawler.window import (
    windowmove,
    windowsize,
    get_window,
    get_child_window,
    send_key,
    undecorate,
    get_window_pid,
)
from brawler.screen import calculate_offset, get_primary_resolution
from brawler.input import duplicator
from brawler import config as global_config
from brawler.logging import log


def wait_for(func, step=5, timeout=30):
    i = 0
    while i < timeout:
        result = func()
        if result is not None:
            break
        else:
            time.sleep(step)
            i += step
    return result


class brawler_config:
    def __init__(self, config, args):
        # Set global config
        if loglevel in config:
            global_config.LOGLEVEL = config["loglevel"]

        # read config options
        self.screen_resolution_x, self.screen_resolution_y = get_primary_resolution()
        self.screen_resolution_offset = calculate_offset()
        self.executable = config["executable"]
        self.accounts = config["accounts"]
        self.wine_bin = config["wine_bin"]
        self.wine_prefix_base = config["wine_prefix_base"]
        self.keys_allowed = config["keys_allowed"]

        # set args
        self.toon_count = args.toons
        self.dual_monitor = args.dual_monitor

        # calculate master and toon resolutions
        # TODO configureable split
        self.master_resolution_y = self.screen_resolution_y - 28
        self.master_resolution_x = (
            self.master_resolution_y / 3 * 4
            if not args.dual_monitor
            else self.screen_resolution_x
        )
        self.toon_resolution_y = (
            self.screen_resolution_y / self.toon_count
            if not args.dual_monitor
            else (self.screen_resolution_y / (self.toon_count / 2))
        )
        self.toon_resolution_x = (
            self.screen_resolution_x - self.master_resolution_x
            if not args.dual_monitor
            else self.screen_resolution_x / (self.toon_count / 2)
        )


class brawler_client:
    def __init__(
        self, id, resolution_x, resolution_y, wine_bin, wineprefix_base, executable
    ):
        self.id = id
        self.name = "client_{}".format(self.id)
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.wine_bin = wine_bin
        self.wineprefix_base = wineprefix_base
        self.executable = executable
        # Copy the current environment and modify it, so all other vars are honored
        self.environment = os.environ.copy()
        self.environment["WINEPREFIX"] = os.path.join(self.wineprefix_base, self.name)
        self.virtual_desktop = None
        self.window = None
        self.ime = '"Default IME": ("{}" "{}")'.format(
            os.path.basename(self.executable).lower(),
            os.path.basename(self.executable).lower(),
        )

    def open(self):
        # Open executable with default Wine
        # TODO: configureable wine executable
        log.info("{}: initializing".format(self.name))
        self.proc = shell(
            "{} explorer /desktop={},{}x{} {} &>/dev/null &".format(
                self.wine_bin,
                self.name,
                int(self.resolution_x),
                int(self.resolution_y),
                self.executable,
            ),
            env=self.environment,
        )

    def windowsize(self):
        log.info(
            "{}: resize {}x{}".format(self.name, self.resolution_x, self.resolution_y)
        )
        windowsize(self.virtual_desktop, self.resolution_x, self.resolution_y)

    def wait_for_virtual_desktop(self):
        return wait_for(self.get_virtual_desktop)

    def wait_for_window(self):
        return wait_for(self.get_window)

    def windowmove(self, x, y):
        log.info("{}: move window to {},{}".format(self.name, x, y))
        windowmove(self.virtual_desktop, x, y)

    def get_virtual_desktop(self):
        self.virtual_desktop = get_window(self.name)
        return self.virtual_desktop

    def get_window(self):
        if self.virtual_desktop is not None:
            ime = get_child_window(self.virtual_desktop, self.ime)
            if ime is not None:
                self.window = ime
        return self.window

    def login(self, user, password):
        log.info("{}: login".format(self.name))
        # wait for the window to be found so we can start the login
        # TODO: this method is still buggy and still needs to be improved
        self.wait_for_window()
        self.get_window()
        # wait a few seconds longer so we definetly have a window
        time.sleep(2)
        # Send Username and password via key inputs and login
        for u in user:
            send_key(self.window, u)
        send_key(self.window, "Tab")
        for p in password:
            send_key(self.window, p)
        send_key(self.window, "Enter")

    def send_key(self, key):
        log.info("{}: sending string {}".format(self.name, key))
        send_key(self.window, key)

    def undecorate(self):
        if not self.virtual_desktop:
            self.get_virtual_desktop()
        undecorate(self.virtual_desktop)

    def get_pid(self):
        pid = get_window_pid(self.window)
        return pid

    def destroy(self):
        pid = self.get_pid()
        log.debug("{}: killing pid {}".format(self.name, pid))
        os.kill(pid, signal.SIGTERM)


class brawler_controller:
    def __init__(self, config):
        self.config = config
        self.clients = []
        self.duplicator = None
        self.is_listening = False

    def launch_client(self, id, res_x, res_y, wine_bin, winepfx_base, exe):
        client = brawler_client(id, res_x, res_y, wine_bin, winepfx_base, exe)
        client.open()
        client.wait_for_virtual_desktop()
        # TODO: check child procs and try to kill them
        client.undecorate()
        time.sleep(2)
        client.windowsize()
        self.clients.append(client)
        return client

    def launch_clients(self):
        # configure and launch master instance
        master = self.launch_client(
            0,
            self.config.master_resolution_x,
            self.config.master_resolution_y,
            self.config.wine_bin,
            self.config.wine_prefix_base,
            self.config.executable,
        )
        master.windowmove(self.config.screen_resolution_offset, 0)

        # configure and launch toons
        x_pos = (
            self.config.screen_resolution_offset + self.config.master_resolution_x
            if not self.config.dual_monitor
            else 0
        )
        y_pos = 0
        for s in range(0, self.config.toon_count):
            toon = self.launch_client(
                s + 1,
                self.config.toon_resolution_x,
                self.config.toon_resolution_y,
                self.config.wine_bin,
                self.config.wine_prefix_base,
                self.config.executable,
            )
            toon.windowmove(x_pos, y_pos)

            if self.config.dual_monitor:
                y_pos += self.config.toon_resolution_y
                if s + 1 == self.config.toon_count / 2:
                    y_pos = 0
                    x_pos += self.config.toon_resolution_x
            else:
                y_pos = (s + 1) * self.config.toon_resolution_y

    def login(self):
        if len(self.clients) > 0:
            if self.config.accounts["master"]:
                self.clients[0].login(
                    self.config.accounts["master"]["user"],
                    self.config.accounts["master"]["password"],
                )
                i = 0
            if len(self.config.accounts["toons"]) > 0:
                for c in self.clients[1:]:
                    if self.config.accounts["toons"][i]:
                        log.info("{}: account found".format(self.clients[i].name))
                        c.login(
                            self.config.accounts["toons"][i]["user"],
                            self.config.accounts["toons"][i]["password"],
                        )
                        i += 1
                    else:
                        break
            else:
                log.error("no clients found")

    def __listen(self):
        log.debug("start listening for key input")
        while self.is_listening:
            self.duplicator.listen()

    def listen(self):
        # listen for key events and start a duplicator if needed

        if self.duplicator == None:
            log.debug("initialize key duplicator")
            self.duplicator = duplicator(self.clients, self.config.keys_allowed)

        self.is_listening = True
        t = threading.Thread(target=self.__listen, args=[])
        t.start()

    def destroy(self):
        if self.is_listening:
            self.debug("shutting down duplicator")
            self.is_listening = False

        log.debug("destroying clients")
        for c in self.clients:
            c.destroy()
