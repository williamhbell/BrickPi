=======
BrickPi
=======

BrickPi is a package that provides access to the BrickPi Raspberry Pi extension board.  
The BrickPi extension board is a microprocessor board that allows the Raspberry Pi to 
communicate with LEGO Mindstorms motors and sensors.  The package provides Python and 
Scratch access to the BrickPi.


Scratch interface
=================

The Scratch interface is via a Device class and the RpiScratchIO package.


RpiScratchIO configuration file
-------------------------------

The Scratch interface uses scratchpy via RpiScratchIO.  Sensors should be added by 
declaring them in the configuration file::

    [DeviceTypes]
    LEGO = import BrickPi; from BrickPi.BrickPiScratch import BrickPiScratch; BrickPiScratch()

    [DeviceConnections]
    LEGO = UART0

    [BrickPi]
    S1 = ULTRASONIC_CONT
    MA =
    MB =

In this example, one ultrasonic sensor and two motors are attached to the BrickPi.  
Motors can be added to the MC or MD ports by declaring them in the same manner.  Sensors 
can be added by addting the sensor name after S2-S4.  The available sensor names are::

    TOUCH
    ULTRASONIC_CONT
    ULTRASONIC_SS
    RCX_LIGHT
    COLOR_FULL
    COLOR_RED
    COLOR_GREEN
    COLOR_BLUE
    COLOR_NONE
    I2C
    I2C_9V

When instantiated, the BrickPiScratch class starts a separate thread to update values 
between the BrickPi and the Raspberry Pi at a rate of 10Hz.  Values can then be read 
from the Raspberry Pi on demand or within the data acquisition loop.  To configure the 
automatic readout to Scratch during the data acquisition loop, the readout period can be 
stated in the configuration file::

    LEGO = import BrickPi; from BrickPi.BrickPiScratch import BrickPiScratch; BrickPiScratch(5)

where this line should replace the constructor line in the previous example and the number 
5 is the readout period.  This means that the sensor or motor encoder values will be 
updated in Scratch once for every five readout loops.  Since the readout loop runs at 
10Hz, this implies that the sensors in Scratch are updated at a rate of 2Hz.  For a 
simple Scratch program running on the Raspberry Pi, 2Hz is the maximum that Scratch can 
deal with.

The sensors or motor encoders can be added to the automatic readout loop by using 
the channel number (explained later) or S (for all sensors) or M (for all motor 
encoders) or All (for both sensors and motor encoders).  The period and sensors can also 
be added from Scratch, buy using the config command (explained later).  To prevent the 
automatic update of sensors or motor encoders when Scratch starts, set the readout 
period to 0::

    LEGO = import BrickPi; from BrickPi.BrickPiScratch import BrickPiScratch; BrickPiScratch(0,"S")

where the active sensor channels have all been added in this case too.

Access from Scratch
-------------------

Start Scratch from the command line or the menu.  Then enable the remote sensor 
connections by right clicking on the "sensor value" text that can be found under the 
"Sensing" tool palette.  A dialog box should appear to say that the remote sensor 
connections have been enabled.  At this point, Scratch becomes a server.  Do not run 
more than one Scratch window on the same machine, otherwise only the first one will be 
accessible from the Python API.  When Scratch has been started, type::

    RpiScratchIO configFile.cfg

where "configFile.cfg" should be replaced with the name of the configuration file that 
was created in the previous step.  If the name of the configuration file is omitted, 
then RpiScatchIO will try to use RpiScrathIO.cfg instead.

When RpiScratchIO starts, it loads the BrickPiScratch Python class.  This updates 
Scratch with several new sensors.  Using the example configuration files given above, 
the variables are::

    LEGO:0
    LEGO:1
    LEGO:2
    LEGO:3
    LEGO:10
    LEGO:11
    LEGO:12
    LEGO:13
    LEGO:20
    LEGO:21
    LEGO:22
    LEGO:23

where these correspond to the sensor ports S1-S4 (0-3), motor ports MA-MD (10-13) and 
motor encoder ports (20-23).  The motor sensors (10-13) contain the value that was 
written to the motors.  Values can be read into the sensor values on demand by sending a 
Scratch broadcast message of the form::

    LEGO:read:0

where 0 is the channel number (S1 in this case).  The value will then appear in the 
corresponding sensor approximately 0.2 of a second later.

Values can be written to the motors by sending a Scratch broadcast request of the form::

    LEGO:write:10,200 

where 10 is the channel number (MA in this case) and 200 is the motor speed value.

Scatch can be used to enable the automatic updating of enabled sensor values by broadcasting::

    LEGO:config:update,s

where the list of channels or wild card options (s for all sensors, m for all motor 
encoders or a list of channels separated by spaces), should follow update.  The rate of 
the update can be set from Scatch by broadcasting::

    LEOG:config:period,5

where 5 implies 2Hz and 10 implies 1Hz etc..  To disable the automatic readout, the 
period should be set to 0.



-----------------

* The DeviceConnections section must be after the DeviceTypes section.

* The device connections define the physical wiring of the components
  or the connection between file names within Scratch and physicial
  file names on disk.

* The device name on the left of the equals sign must be declared in the
  DeviceTypes before it is used here.

* The text to the right of the equals can be a single BCM pin reference,
  a list of BCM pin references separated by commas or buses.  Valid bus
  names are I2C0, I2C1, SPI0, SPI1, UART0.

Starting Scratch
================

* Scratch must be started before the ScratchIO object is instantiated.

* Remote sensors must be enabled by selecting the **Sensors** tool palette.
  Then right click on **sensor value**. Then select 
  *enable remote sensor connections*.

