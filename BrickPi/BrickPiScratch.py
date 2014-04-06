from BrickPi import *
from RpiScratchIO.Devices import GenericDevice

#=====================================

# For the chip of the same name
class BrickPiScratch(GenericDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):

    # Call the base class constructor
    super(BrickPiScratch, self).__init__(deviceName_,scratchIO_,connections_)

    # Read the list of attached sensors
    self.__haveSensors = False
    self.__parseConfigFile() 

    # Open serial port connection
    ret_val = BrickPiSetup()
    if ret_val != 0:
      print "ERROR: could not open serial port link to the BrickPi.  Check the serial port configuration and hardware."
      assert 0 # Need to fix this cleanly

    # Setup the sensors, if requested
    if self.haveSensors:
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

    # Read the configuration file, to find which sensors are connected
    # to which ports.  By default, all motors are enabled and no
    # sensors are enabled.
    if self.scratchIO.config.has_section("BrickPi"):
      for portName, sensorName in self.config.items("BrickPi"):

        if len(portName) != 2:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        try:
          portNumber = int(portName[1])
        except ValueError:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Use the variables in BrickPi
        portIds = []
        channelOffet = 0
        if portName[0] == "S":
          portIds += [ PORT_1, PORT_2, PORT_3, PORT_4]           
        elif portName[0] == "M":
          portIds += [ PORT_A, PORT_B, PORT_C, PORT_D]
          channelOffset = 10
        else:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue 
        
        if portNumber > len(portIds):
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Get the port id for this port name
        portId = portIds[portNumber]
 
        # Check if the sensor is a valid sensor name.
        foundName = False
        for sensorName in allowedSensors:
          if sensorName.lower() == sensorName.lower():
            foundName = True
            break

        if not foundName:
          print("WARNING: \"%s\" is not a valid sensor name. Valid sensor names are %s." % sensorName, allowedSensors)
          continue

        sensorValue = exec("TYPE_SENSOR_%s" % sensorName)

        # Add this sensor
        BrickPi.SensorType[portId] = sensorValue

        # Make sure the values are flushed to the BrickPi
        if not self.haveSensors:
          self.haveSensors = True

        # Add this channel as an available input channel
        channelNumber = portNumber+channelOffset
        if channelOffset < 10:
          self.inputChannels += [ channelNumber ]
        else:
          self.outputChannels += [ channelNumber ]
          self.inputChannels += [ channelNumber+10 ] # Motor encoder

  #-----------------------------

  def write(self,channelNumber,value):

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

    # Set the motor speed value
    BrickPi.MotorSpeed[PORT_A] = intValue

    # Ask BrickPi to update the sensor and motor values
    if BrickPiUpdateValues() != 0:
      print("WARNING: X failed")
      return None

    # Set the scratch sensor value for this motor

  #-----------------------------

  def read(self,channelNumber):
    # Read the sensor or motor encoder.

    # Ask BrickPi to update the sensor and motor values
    if BrickPiUpdateValues() != 0:
      print("WARNING: X failed")
      return None

    # Value from sensor
    BrickPi.Sensor[PORT_1]

    BrickPi.Encoder[PORT_A] %720 ) /2   # print the encoder degrees 
    # Note: One encoder value counts for 0.5 degrees. So 360 degrees = 720 enc. Hence, to get degress = (enc%720)/2
   
    # Update scratch with the value

#=====================================