.. Instin documentation master file, created by
   sphinx-quickstart on Mon Feb  1 09:05:37 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Instin's documentation!
==================================

Instin is a wireless instrumentation control system based on gateways, which are in charge
of receive the instrumentation commands from the host computer, send them to the instruments
and reply the requested information (if any) to the host. This webpage contains the installation
of the system and the description of each function of :code:`instin.py`, the Python package that
enables the use of this wireless system from Python. It is based on the `PyVISA <https://pyvisa.readthedocs.io/>`_ and
`socket <https://docs.python.org/3/library/socket.html>`_ Python packages.

For a complete description of this system you can read the following publications:

- D. Enériz, N. Medrano and B. Calvo, "Live Demonstration: A Low-Cost Wireless Instrumentation Control System," *2020 IEEE International Symposium on Circuits and Systems (ISCAS)*, Sevilla, 2020, pp. 1-1, doi: `10.1109/ISCAS45731.2020.9180681 <http://bit.ly/39CpxdE>`_.
- D. Enériz, N. Medrano, B. Calvo and J. Pérez-Bailón, "A Wireless Instrumentation Control System Based on Low-Cost Single Board Computers," *2020 IEEE International Instrumentation and Measurement Technology Conference (I2MTC)*, Dubrovnik, Croatia, 2020, pp. 1-5, doi: `10.1109/I2MTC43012.2020.9129142 <http://bit.ly/3oFe55c>`_.

If you find these useful, please consider their citation.

Additionally, all the code is available on `Github <https://bit.ly/39z3LHC>`_.

Table of contents
-----------------
.. toctree::
   :maxdepth: 2
   
   installation
   instin