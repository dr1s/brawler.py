#!/usr/bin/env python3
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
import yaml
import signal
import argparse
from brawler.api import brawler_config, brawler_controller
from brawler.logging import log

ctrl = None


def handler(sig, frame):
    if ctrl:
        log.debug("destroying windows")
        ctrl.destroy()
    exit()


def main():
    parser = argparse.ArgumentParser(description="Simple multiboxer on Linux/X.org")
    parser.add_argument("-t", "--toons", help="amount of toons", type=int)
    parser.add_argument(
        "-d",
        "--dual-monitor",
        help="enable dual monitor mode",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-c", "--config", help="yaml config file", type=str, default="config.yml"
    )
    parser.add_argument(
        "-l",
        "--login",
        help="use login information and log in",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        conf_file = yaml.safe_load(stream)

    signal.signal(signal.SIGINT, handler)
    config = brawler_config(conf_file, args)
    ctrl = brawler_controller(config)
    try:
        ctrl.launch_clients()
        if args.login:
            ctrl.login()
        else:
            w_input = input("Waiting for login. Do you want to continue?")
        ctrl.listen()
    except Exception as e:
        log.error(e)
        ctrl.destroy()


if __name__ == "__main__":
    main()
