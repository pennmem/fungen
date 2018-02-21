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
        self.channel = 1
        # logger.info(self.id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.device.close()
        if self.close_on_exit:
            self.rm.close()

    @property
    def id(self):
        """Property that queries the device for and returns its ID string."""
        return self.device.ask("*IDN?")

    @property
    def output(self):
        """Property to get or set device output enabled state."""
        return self.device.ask("OUTPUT?")

    @output.setter
    def output(self, value):
        on_or_off = "ON" if value else "OFF"
        self.device.write("OUTPUT%s %s" %(self.channel, on_or_off))

    def write(self, command, echo=True):
        """Wraps the VISA write command."""
        if echo:
            print(command)
        return self.device.write(command)

    def ask(self, command, echo=True):
        """Wraps the PyVISA ``ask`` method."""
        if echo:
            print(command)
        return self.device.ask(command)

    @check
    def set_function(self, function):
        """Set the function to be generated.

        :param str function:

        """
        return self.device.write("FUNCtion%s %s" %(self.channel, function))

    @check
    def set_amplitude(self, amplitude, units="VPP"):
        """Set the output waveform amplitude.

        :param float amplitude:
        :param str units: ``VPP``, ``VRMS``, or ``DBM`` (default: ``VPP``)

        """
        if units.upper() not in ("VPP", "VRMS", "DBM"):
            raise InvalidUnitsError(str(units))
        self.device.write("VOLTAGE:UNIT %s" % units)
        return self.device.write("VOLTAGE %.3E" % amplitude)

    @check
    def set_offset(self, offset, units="VPP"):
        """Set the waveform offset.

        :param float offset:
        :param str units: ``VPP``, ``VRMS``, or ``DBM`` (default: ``VPP``)

        """
        if units.upper() not in ("VPP", "VRMS", "DBM"):
            raise InvalidUnitsError(str(units))
        self.device.write("VOLTAGE:UNIT %s" % units)
        return self.device.write("VOLTAGE:OFFSET %0.8f")

    @check
    def set_frequency(self, frequency):
        """Set the output waveform frequency.

        :param float frequency:

        """
        return self.device.write("FREQUENCY %.8f" % frequency)


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
