# aietrace : a Python parser for AIE trace files

This python package contains a utility for parsing events from AIE trace files.
It can be used to generate files in a format consumable by perfetto allowing events to be visualised and inspected inspected.

### installation

Run the following in this directory to install the utility.
```
python3 -m pip install .
```

### usage

After installation the `aietrace` utility should be availabe from your command line, you can test this by typing.
```
$ aietrace --help
usage: aietrace [-h] --input INPUT [--events EVENTS [EVENTS ...]] [--json JSON] [--debug]

Parses the logtrace of an application

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         The name of the file containing the trace information
  --events EVENTS [EVENTS ...]
                        A list mapping event labels to slots events are in slot order e.g.
                        --events INSTR_VECTOR KERNEL_START KERNEL_DONE PORT_RUNNING_0
                        PORT_RUNNING_1 LOCK_STALL LOCK_ACQUIRE LOCK_RELEASE
  --json JSON           The prefetto compatible json file that gets generated
  --debug               Print extra debug information while parsing
```

To parse a trace file and generate perfetto compatible json run:

```
aietrace --input <raw trace file>.txt --json <perfetto file>.json
```

To visualise the output drag and drop the output json file into [https://ui.perfetto.dev/](https://ui.perfetto.dev/).

It is also possible to give names to the event slots that are being used. To do this use the events argument in the tool. (TODO: parse the MLIR source to extract this)

The debug flag will dump intermediate parsing results of the raw trace data such as the frames.

### running tests
There is a small suite of tests for aietrace, to run them type the following in this directory:
```
python3 -m pytest ./
```
