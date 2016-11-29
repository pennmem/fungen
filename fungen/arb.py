"""Arbitrary waveform generation."""

from __future__ import division
import numpy as np
from functools import partial


class Waveform(object):
    """Base arbitrary waveform class.

    :param list data: A list of points to convert to a waveform in units of
        volts.
    :param float sample_rate: Rate in Hz of waveform.

    """
    def __init__(self, data, sample_rate):
        data = np.array(data)
        assert len(data.shape) == 1

        self.sample_rate = sample_rate
        self.amplitude = max(abs(data))
        self.data = data / self.amplitude

    def write_file(self, filename):
        """Override to write to a file in the appropriate format."""

    def write_to_device(self, dev, name="func", toggle_output=True, echo=False):
        """Override to write to the VISA device.

        :param FunctionGenerator dev:
        :param str name: Name to give the waveform (default: ``"func"``).
        :param bool toggle_output: When True, first turn the output off before
            making changes, then turn it back on when complete. If False, the
            output state won't be changed.

        """
        write = partial(dev.write, echo=echo)

        if toggle_output:
            write("OUTPUT OFF")

        write("data:arb %s, %s" % (name, ",".join([str(x) for x in self.data])))
        write("func:arb %s" % name)
        write("func:arb:srate " + str(self.sample_rate))
        write("voltage:amplitude %s V" % str(self.amplitude))

        if toggle_output:
            write("OUTPUT ON")


if __name__ == "__main__":
    from .device import FunctionGenerator
    import matplotlib.pyplot as plt

    num = 50

    data = [x**2 for x in range(num)]
    data.extend([0]*num)
    data = np.array(data)/max(data) * 300e-3
    plt.ion()
    plt.plot(data)
    plt.show()

    # data += np.random.choice((1, -1), data.shape) * np.random.random(data.shape)
    waveform = Waveform(data, 100e3)
    for point in waveform.data:
        print(point)

    with FunctionGenerator("USB0::2391::9991::MY52303330::0::INSTR") as dev:
        if True:
            dev.write("data:vol:clear")
            waveform.write_to_device(dev)
