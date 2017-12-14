import numpy as np
from fungen.arb import Waveform
from fungen.device import FunctionGenerator

data = np.random.random((100,))
sample_rate = 100.
waveform = Waveform(data, sample_rate)

with FunctionGenerator("USB0::2391::9991::MY52303330::0::INSTR") as dev:
    dev.write("data:vol:clear")
    waveform.write_to_device(dev)
