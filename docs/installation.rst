Installation
============

Previous requirements
---------------------

There are some hardware requirements that are needed to use Instin:

- **A WiFi network**. Is a WiFi-based system so it needs WiFi to work. Also you may consider that you will have to configure this WiFi network on the Raspberry-based gateways and, if the WiFi is protected with some certification more sophisticated than WPA2, as `eduroam <https://www.eduroam.org/>`_, you will find yourself in a burdensome process. If this happens to you, we recommend to use a household router to create a dedicated WiFi network.
- At least one **WiFi-enabled Raspberry Pi SBC**. The gateways are Raspberry Pi SBC and they need to have a WiFi antenna. It should work on any of the WiFi-enabled Raspberry Pi SBCs but it has been only tested on the Raspberry Pi Zero W and the Raspberry Pi 3B.
- **A USB hub** (*Only necessary on the Raspberry Pi Zero W*). The Raspberry Pi Zero W only has a mircoUSB port, but the instrumentation has been traditionally controlled using USB-B-to-USB-A cables, so one (at least) USB type A port is desirable. We solve this using the `Zero4U USB hub <http://www.uugear.com/product/zero4u/>`_, specifically designed for the RPi Zero boards.

Gateway configuration
---------------------

Basic configuration
```````````````````

The gateway is based on a Raspberry Pi Zero W, since it has a very small form-factor and
it has the enough features to have a good performance running the Instin system. In the
next steps, we are assuming you got a **fresh install** of Raspbian on a Raspberry Pi and it is connected to the same WiFi network that the host PC is. Also, an access to the Raspberry terminal is required.
It could be either by the Desktop or using SSH.

.. note::
   If you don't know hot to install the OS on a Raspberry Pi you should check the `Raspberry documentation <https://www.raspberrypi.org/documentation/installation/>`_. Also there are some there are some pages dedicated to the `Wireless Connectivity <https://www.raspberrypi.org/documentation/configuration/wireless/>`_

The fist thing to do is to install :code:`pyvisa` and :code:`pyvisa-py` packages. This can be done using pip::

   $ pip3 install pyvisa
   $ pip3 install pyvisa-py

Then the :code:`autorun.py` file must be sent to the Raspberry-based gateways. In order to have it locatable, we recommend to place it on the Desktop folder. If you are using SSH you could send it through a FTP service, as `Filezilia <https://filezilla-project.org/>`_. Also it can be downloaded running this lines::
   
   $ cd /home/pi/Desktop
   $ wget https://raw.githubusercontent.com/eneriz-daniel/instin/main/autorun.py

Additionally, in order to make the gateway ready each time it boots, we can configure a `cron job <https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html>`_ to launch :code:`autorun.py` when the Raspberry reboots. To do this we can create a crontab file for the Superuser::

   $ sudo crontab -e

.. warning::
   This will ask you for the Raspberry password, as it is a Superuser action. We use this rol since it seems to be necessary to run some PyVISA functions.

.. note::
   If it is the first time using crontab since the install, this will ask you to choose the text editor. We recommend you to use :code:`nano`::
         
      no crontab for root - using an empty one

      Select an editor.  To change later, run 'select-editor'.
      1. /bin/nano        <---- easiest
      2. /usr/bin/vim.tiny
      3. /bin/ed

      Choose 1-3 [1]: 1

Now the commands to be run at the reboot must be placed at the end of the file. Just add the last line::

   # For example, you can run a backup of all your user accounts
   # at 5 a.m every week with:
   # 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
   @reboot cd /home/pi/Desktop && sudo python3 autorun.py

.. note::
   To save and exit from nano press :code:`Ctrl+X`, :code:`Y`to say yes when saving changes and then :code:`Enter` to exit.

Finally reboot your the gateway using::

   $ sudo reboot

After the reboot it should be ready to receive orders from :code:`instin`.

Advance configuration
`````````````````````

The lines above contain the minimal steps to make :code:`autorun.py` run on the gateways, but some extra steps are necessary to have a better experience with instin. Although if you want to use just one gateway you can pass directly to the host PC configuration.

Multiple port
'''''''''''''

This enables various ports in the same gateway. This can be handy when more than one gateways used. In this we are setting for ports to be open, but this can be scaled to any number.

For this we are downloading the files in the `various-autoruns folder <https://github.com/eneriz-daniel/instin/tree/master/various-autoruns>`_ of the Github repository::

   $ cd /home/pi/Desktop
   $ for i in {1..4}; do wget "https://raw.githubusercontent.com/eneriz-daniel/instin/master/various-autoruns/autorun_$i.py"; done

Additionally, if the basic :code:`autorun.py` file has been downloaded previously, must be deleted::

   $ rm autorun.py

Finally, the crontab file must be also edited in order to launch this new files. Remeber you can access to there with the :code:`sudo crontab -e` and it should contain this::

   # For example, you can run a backup of all your user accounts
   # at 5 a.m every week with:
   # 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
   @reboot cd /home/pi/Desktop && sudo python3 autorun_1.py
   @reboot cd /home/pi/Desktop && sudo python3 autorun_2.py
   @reboot cd /home/pi/Desktop && sudo python3 autorun_3.py
   @reboot cd /home/pi/Desktop && sudo python3 autorun_4.py

Static IP
'''''''''
The gateways' IPs are needed in the :code:`instin` functions, so they must be found, for example using an IP Scanner. A better solution is to use static IPs on the Raspberry-based gateways. For this it is necessary to edit the :code:`/etc/dhcpcd.conf` with the details of your network.

.. note::
   This is the explanation to set the static IP on one Raspberry, if your using more than one, ensure to set different IPs. Otherwise there will be connection problems.

The first thing to do is to find your network details, for this you can use::

   $ ifconfig wlan0

This will answer you something like::

   wlan0  Link encap:Ethernet  HWaddr 58:a2:c2:93:27:36  
          inet addr:192.168.1.64  Bcast:192.168.2.255  Mask:255.255.255.0
          inet6 addr: fe80::6aa3:c4ff:fe93:4746/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:436968 errors:0 dropped:0 overruns:0 frame:0
          TX packets:364103 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:115886055 (110.5 MiB)  TX bytes:83286188 (79.4 MiB)

Where it is shown that your IP is :code:`192.168.1.64` and your mask :code:`255.255.255.0`. Also the router IP is needed, this can be queried by::

   $ netstat -nr

Which answer could be::

   Destination    Gateway      Genmask
   0.0.0.0        192.168.1.1  0.0.0.0
   192.168.1.0    0.0.0.0      255.255.255.0

So the router IP is :code:`192.168.1.1`. Once you have the Raspberry IP, the mask and the router IP, you have you edit the following file::

   $ sudo nano /etc/dhcpcd.conf

And introduce something like this on the top

.. warning::
   Ensure to use your use your correct IPs both router's and Raspberry's if not you can lose the Raspberry connection if working through SSH.

::

   interface wlan0
   static ip_address=192.168.1.15/24
   static routers=192.168.1.1
   static domain_name_servers=8.8.8.8 8.8.4.4

Where :code:`192.168.1.15` is the desired static IP

.. note::
   This example assumes that your subnet mask is Class C, i.e., :code:`255.255.255.0`, that is marked as :code:`/24` in the :code:`/etc/dhcpcd.conf` new lines. If yours is :code:`255.255.0.0` you should use :code:`/16` and if it is :code:`255.0.0.0` the correct is :code:`/8`. Check this `video <https://www.youtube.com/watch?v=D1eD60_jhKI>`_ for a better explanation.

Host PC configuration
---------------------

The configuration of the Host PC is simpler. It is only necessary to make :code:`instin.py` accessible to the program you are going to code the measurement orders. An easy solution is to save it in the same directory, but a better one is to copy the :code:`instin.py` file in a directory added to the :code:`PYTHONPATH`. To get show the directories added to the :code:`PYTHONPATH` is possible to use the following Python code:

   >>> import sys
   >>> sys.path

Then you can copy :code:`instin.py` to any directory shown after :code:`sys.path`, allowing its importation from any Python program.
