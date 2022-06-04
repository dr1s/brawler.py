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

import time
import subprocess
from shlex import quote

from brawler import config
from brawler.logging import log


def execute(cmd):
    result = None

    try:
        out = subprocess.check_output(cmd, encoding="UTF-8", shell=True)
    except subprocess.CalledProcessError as error:
        log.error("error while executing {}: {}".format(cmd, error))
    else:
        out = out.split()
        result = out if len(out) > 0 else None
        log.debug("command executed successfully: {}".format(result))
    return result


def shell(cmd, env=None):
    proc = None

    try:
        proc = subprocess.Popen(cmd, env=env, shell=True)
    except subprocess.CalledProcessErrorProcess as error:
        log.error("error while spawning shell: {}".format(error))
    else:
        log.debug("shell executed successfully: {}".format(proc.pid))

    return proc
