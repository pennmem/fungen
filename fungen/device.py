import logging
from pyvisa import ResourceManager

logger = logging.getLogger(__name__)


class CommunicationsError(Exception):
    pass


class InvalidUnitsError(Exception):
    pass


def check_output(output):
    if output[1].value != 0:
        raise CommunicationsError("Got response: " + str(output[1]))
    else:
        return output


def check(func):
    """Decorator to check that a command executed properly."""
    def wrapper(*args, **kwargs):
        return check_output(func(*args, **kwargs))
    return wrapper


class functions:
    """Namespace containing the various types of function outputs."""
    sine = "SIN"
    square = "SQU"
    ramp = "RAMP"
    pulse = "PULS"
    triangle = "TRI"
    noise = "NOIS"
    prbs = "PRBS"
    arbitrary = "ARB"
    arb = arbitrary


class FunctionGenerator(object):
    """Interface to SCPI-compliant function generators.

    :param str address: NI VISA resource address
    :param int timeout: Timeout in ms (Default: ``None``).
    :param ResourceManager resource_manager: A pre-defined
        :class:`ResourceManager` or ``None`` to create a new one.
    :param bool close_on_exit: When True (the default), close the resource
        manager on exit.

    """
    def __init__(self, address, timeout=None, resource_manager=None,
                 close_on_exit=True):
        self.rm = resource_manager or ResourceManager()
        self.device = self.rm.open_resource(address)
        self.device.timeout = timeout
        self.close_on_exit = close_on_exit


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.device.close()
        if self.close_on_exit:
            self.rm.close()


    def write(self, command, echo=True):
        """Wraps the VISA write command."""
        if echo:
            print(command)
        return self.device.write(command)


    def query(self, command, echo=True):
        """Wraps the PyVISA ``query`` method."""
        if echo:
            print(command)
        return self.device.query(command)


    @property
    def id(self):
        """Property that queries the device for and returns its ID string."""
        return self.device.query("*IDN?")


    @property
    def output(self):
        """Property to get or set device output enabled state."""
        return self.device.query("OUTPUT%s?" % self.channel)


    @output.setter
    def output(self, value):
        on_or_off = "ON" if value else "OFF"
        self.device.write("OUTPut%s %s" %(self.channel, on_or_off))


    @property
    def function(self):
        """ Get the function of the specified channel """
        return self.devide.query("SOURce%s:FUNCtion?" % self.channel)


    @function.setter
    def function(self, function):
        """Set the function to be generated.

        :param str function:

        """
        return self.device.write("SOURce%s:FUNCtion %s" %(self.channel, function))

    @property
    def amplitude(self):
        """ Get the amplitude of the specified channel """ 
        return self.device.query("SOURce%s:VOLTage?" % self.channel)


    @amplitude.setter
    def amplitude(self, amplitude, units="VPP"):
        """Set the output waveform amplitude.

        :param float amplitude:
        :param str units: ``VPP``, ``VRMS``, or ``DBM`` (default: ``VPP``)

        """
        if units.upper() not in ("VPP", "VRMS", "DBM"):
            raise InvalidUnitsError(str(units))
        self.device.write("SOURce%s:VOLT:UNIT %s" % (self.channel, units))

        return self.device.write("SOURce%s:VOLTage %.3E" % (self.channel, amplitude))


    @property
    def offset(self):
        """ Get the offset value of the specified channel """
        return self.device.query("SOURce%s:VOLTage:OFFSET?" % self.channel)

    @offset.setter
    def offset(self, offset, units="VPP"):
        """Set the waveform offset.

        :param float offset:
        :param str units: ``VPP``, ``VRMS``, or ``DBM`` (default: ``VPP``)

        """
        if units.upper() not in ("VPP", "VRMS", "DBM"):
            raise InvalidUnitsError(str(units))
        self.device.write("SOURce%s:VOLTage:UNIT %s" % (self.channel, units))
        return self.device.write("SOURce%s:VOLTage:OFFSET %0.8f" % (self.channel, offset))


    @property
    def frequency(self):
        """ Get the value of the frequency of the current channel """
        return self.device.query("SOURce%s:FREQuency?" % self.channel)


    @frequency.setter
    def frequency(self, frequency):
        """Set the output waveform frequency.

        :param float frequency:

        """
        return self.device.write("SOURce%s:FREQuency %.8f" % (self.channel, frequency))


    @property
    def burst(self):
        """ Get the burst mode on/off of the current channel """
        return self.device.query("SOURce%s:BURSt:STATe?" % self.channel)

    
    @burst.setter
    def burst(self, value):
        """Set the a burst.

        :param bool value:

        """
        onoff = 1 if value else 0
        return self.device.write("SOURce%s:BURSt:STATe %.8f" % (self.channel, onoff))


    @property
    def ncycles(self):
        """ Get the ncycles of the current channel """
        return self.device.query("SOURce%s:BURSt:NCYCles?" % self.channel)


    @ncycles.setter
    def ncycles(self, ncycles):
        """ Set the Ncycles of the burst
        
        :param int ncycles or 'inf' or 'min' or 'max'
        """
        if ncycles == 'inf':
            ncycles = 'INFinity'
        elif ncycles == 'min':
            ncycles = 'MINimum'
        elif ncycles == 'max':
            ncycles = 'MAXimum'

        return self.device.write("SOURce%s:BURSt:NCYCles %s" % (self.channel, ncycles))


    @property
    def burst_period(self):
        """ Get the burst period of the current channel """
        return self.device.query("SOURce%s:BURSt:INTernal:PERiod?" % self.channel)


    @burst_period.setter
    def burst_period(self, period):
        """ Set the period of the burst
        
        :param float in s, 'min' or 'max'
        """

        if period == 'min':
            period = 'MINimum'
        elif period == 'max':
            period = 'MAXimum'

        return self.device.write("SOURce%s:BURSt:INTernal:PERiod %s" % (self.channel, period))


    @property
    def burst_mode(self):
        """ Get the burst mode of the current channel """
        return self.device.query("SOURce%s:BURSt:INTernal:MODE?" % self.channel)


    @burst_mode.setter
    def burst_mode(self, mode):
        """ Set the period of the burst
        
        :param float in s, 'triggered' or 'gated'
        """

        if mode == 'triggered':
            mode = 'TRIGgered'
        elif mode == 'gated':
            mode = 'GATed'
        else:
            raise Exception('%s is not a valid burst mode. Only triggered and gated')

        return self.device.write("SOURce%s:BURSt:MODE %s" % (self.channel, mode))


    @property
    def trigger_source(self):
        """ Get the trigger source value """
        return self.device.query("SOURce%s:TRIGger[1|2]:SOURce?" % self.channel)
    
    @trigger_source.setter
    def trigger_source(self, mode):
        """ Set the trigger to the specified source 
        :param 'immediate', 'external', 'timer', 'bus'
        """
        if mode == 'immediate':
            mode = 'IMMediate'
        elif mode == 'EXTernal':
            mode = 'EXTernal'
        elif mode == 'timer':
            mode = 'TIMer'
        elif mode == 'bus':
            mode = 'BUS'

        return self.device.write("TRIGger%s:SOURce %s" % (self.channel, mode))




if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    with FunctionGenerator("USB0::2391::9991::MY52303330::0::INSTR") as gen:
        gen.output = True
        gen.set_amplitude(2e-3)

        gen.set_function(functions.sine)
        time.sleep(0.5)

        gen.set_function(functions.square)
        time.sleep(0.5)

        gen.set_function(functions.triangle)
        time.sleep(0.5)

        gen.output = False
