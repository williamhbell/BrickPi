import time
from BrickPi import *
from RpiScratchIO.Devices import GenericDevice

#=====================================

# For the chip of the same name
class BrickPiScratch(GenericDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):

    # Call the base class constructor
    super(BrickPiScratch, self).__init__(deviceName_,scratchIO_,connections_)

    # Add the channels to Scratch
    for i in xrange(4):
      self.inputChannels += [ i ]       # Sensors
      self.outputChannels += [ i+10 ]   # Motors 
      self.inputChannels += [ i+20 ]    # Encoders

    # Active sensors, motors and motor encoders
    self.activeChannels = {}
    for i in self.inputChannels:
      self.activeChannels[i] = False
    for i in self.outputChannels:
      self.activeChannels[i] = False

    # BrickPi port ids
    self.__portIdsSensors = [ PORT_1, PORT_2, PORT_3, PORT_4 ]
    self.__portIdsMotors = [ PORT_A, PORT_B, PORT_C, PORT_D ]

    # Read the list of attached sensors
    self.__haveSensors = False
    self.__parseConfigFile() 

    # Open serial port connection
    ret_val = BrickPiSetup()
    if ret_val != 0:
      print "ERROR: could not open serial port link to the BrickPi.  Check the serial port configuration and hardware."
      assert 0 # Need to fix this cleanly

    # Setup the sensors, if requested
    if self.__haveSensors:
      ret_val = BrickPiSetupSensors()
      if ret_val != 0:
        print "ERROR: coult not send sensor types to the BrickPi."
        assert 0 # Need to fix this cleanly

  #-----------------------------

  def __parseConfigFile(self):

    # The sensor names are the name as the variables in BrickPi, but without the "TYPE_SENSOR_" prefix
    allowedSensors = []
    allowedSensors += ["TOUCH","ULTRASONIC_CONT","ULTRASONIC_SS","RCX_LIGHT","COLOR_FULL"]
    allowedSensors += ["COLOR_RED","COLOR_GREEN","COLOR_BLUE","COLOR_NONE","I2C","I2C_9V"]

    print "====== BrickPi ========================"
    print "Port (Ch#) ---------- Sensor name" 
    # Read the configuration file, to find which sensors are connected
    # to which ports.  By default, all motors are enabled and no
    # sensors are enabled.
    if self.scratchIO.config.has_section("BrickPi"):
      for portName, sensorName in self.scratchIO.config.items("BrickPi"):

        if len(portName) != 2:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Three bit number : sensor, motor, motor encoder
        connectionType = 0

        # Use the variables in BrickPi
        channelOffet = -999
        portIds = []
        if portName[0] == "S":
          try:
            portNumber = int(portName[1])
          except ValueError:
            print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
            continue

          portIds = self.__portIdsSensors
          connectionType += 1          
        elif portName[0] == "M":
          portNumber = ord(portName[1])-ord('A')+1 # To match sensors
          portIds = self.__portIdsMotors
          connectionType += 2
        else:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue 
        
        if portNumber < 0 or portNumber > len(portIds):
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Get the port id for this port name
        portId = portIds[portNumber-1]
 
        # If this is a sensor, check if the sensor is a valid sensor name.
        if connectionType & 1 == 1:
          foundName = False
          for allowedSensor in allowedSensors:
            if allowedSensor.lower() == sensorName.lower():
              foundName = True
              break

          if not foundName:
            print("WARNING: \"%s\" is not a valid sensor name. Valid sensor names are %s." % sensorName, allowedSensors)
            continue

          exec "sensorValue = TYPE_SENSOR_%s" % sensorName

          # Add this sensor
          BrickPi.SensorType[portId] = sensorValue

          # Activate this channel
          self.__activateAndPrint(portName,portNumber-1,sensorName)          
          
        
        # If this a motor, then enable the motor and check if the encoder should be enabled 
        elif connectionType & 2 == 2:
          BrickPi.MotorEnable[portId] = 1
          self.__activateAndPrint(portName,portNumber-1+10,"ON")

        else:
          print("WARNING: unknown connection type!")
          continue
 
    print "======================================="

  #-----------------------------

  def __activateAndPrint(self,portName,channelNumber,sensorName):
    self.activeChannels[channelNumber] = True
    # If it is a motor, enable the encoder channel too.
    if channelNumber >= 10:
      self.activeChannels[channelNumber+10] = True
    print("%4s (%3d) ---------- %s " % (portName,channelNumber,sensorName))

    # Make sure the values are flushed to the BrickPi
    if not self.__haveSensors:
      self.__haveSensors = True

  #-----------------------------

  def write(self,channelNumber,value):

    # Check if the channel is active or not
    if not self.activeChannels[channelNumber]:
      print("WARNING: channel %d of %s is disabled" % (channelNumber,self.deviceName))
      return None

    # Convert to integer and catch the type error
    try:
      intValue = int(value)
    except ValueError:
      print("WARNING: %s is not an integer." % value)
      return None

    # Prevent the value from going out of range.
    if intValue < -255:
      intValue = -255
    elif intValue > 255:
      intValue = 255

    # This should be safe, since the channelNumber is beforehand
    portId = self.__portIdsMotors[channelNumber-10]

    print "%d %d" % (portId,intValue)

    # Set the motor speed value
    BrickPi.MotorSpeed[portId] = intValue

    # Ask BrickPi to update the sensor and motor values
    if BrickPiUpdateValues() != 0:
      print("WARNING: %s is unable to set motor values" % self.deviceName)
      return None

    # Set the scratch sensor value for this motor
    self.updateSensor(channelNumber,intValue)

  #-----------------------------

  def read(self,channelNumber):

    # Check if the channel is active or not
    if not self.activeChannels[channelNumber]:
      print("WARNING: channel %d of %s is disabled" % (channelNumber,self.deviceName))
      return None

    # Ask BrickPi to update the sensor and motor values
    if BrickPiUpdateValues() != 0:
      print("WARNING: %s is unable to retrieve sensor values" % self.deviceName)
      return None

    if channelNumber < 10:
      # This should be safe, since the channelNumber is beforehand
      portId = self.__portIdsSensors[channelNumber]
      value = BrickPi.Sensor[portId]
    else:
      # This should be safe, since the channelNumber is beforehand
      portId = self.__portIdsMotors[channelNumber-20]
      value = BrickPi.Encoder[portId]/2   # print the encoder degrees 
   
    # Send the value back to Scratch
    self.updateSensor(channelNumber, value)

#=====================================
