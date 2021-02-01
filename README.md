[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Instin: Wireless instrumentation control system

![Scheme](/img/scheme.png)

`instin` is a wireless instrumentation control system based on gateways, which are in charge to receive the instrumentation commands from the host computer, send them to the instruments and reply the requested information (if any) to the host.

This repo contains the [`instin.py`](instin.py) file, the library to use the system in the host computer, [`autorun.py`](autorun.py) the program to be run on the gateway and [two IPython demo notebooks](demos).

All the details of the installation process and the documentation of the `instin.py` functions is available in [instin.readthedocs.io](https://instin.readthedocs.io/).
