fungen
======

Communicate with SCPI function generators with Python and [PyVISA][].

Currently supported devices:

* Agilent 33500B

[PyVISA]: https://pyvisa.readthedocs.io/en/stable/index.html

Generating arbitrary waveforms
------------------------------

Install requirements::

    conda install -c conda-forge -y --file=requirements.txt

Create a waveform as a numpy array then load it into a `fungen.arb.Waveform`
object and upload to the device:

```python
import numpy as np
from fungen.arb import Waveform
from fungen.device import FunctionGenerator

data = np.random.random((100,))
sample_rate = 100.
waveform = Waveform(data, sample_rate)

with FunctionGenerator("USB0::2391::9991::MY52303330::0::INSTR") as dev:
    dev.write("data:vol:clear")
    waveform.write_to_device(dev)
```
