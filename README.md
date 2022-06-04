# brawler.py
Simple multiboxing on Linux/X.org

## Setup
### Prerequisites

* xdotool
* xhwinfo
* xprop
* python / pip

#### Arch

    pacman -S xorg-xhwinfo xdotool xorg-xprop python python-pip

### Install

    pip install --upgrade https://github.com/dr1s/brawler.py.git

    or

    git clone https://github.com/dr1s/brawler.py.git
    cd brawler.py
    python setup.py install


## Configuration

See [example_config.yml](example_config.yml)


## Usage

    usage: brawler [-h] [-t TOONS] [-d] [-c CONFIG]

    Simple multiboxer on Linux/X.org

    optional arguments:
    -h, --help            show this help message and exit
    -t TOONS, --toons TOONS
                        amount of toons
    -d, --dual-monitor    enable dual monitor mode
    -c CONFIG, --config CONFIG
                        yaml config file
