#!/usr/bin/env python3

import sys
import typing
from dataclasses import dataclass
from typing import List
from arcaflow_plugin_sdk import plugin
import subprocess
import os
import re

@dataclass
class UPerfParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    test_type: typing.Optional[str] = None # Not used yet
    num_threads: typing.Optional[int] = 1 # Not used yet
    protocol: typing.Optional[str] = "tcp"# TODO: Use Enum Here
    message_size: typing.Optional[int] = 64 # Not used yet.
    read_message_size: typing.Optional[int] = 64 # Not used yet.

@dataclass
class UPerfRawData:
    nr_bytes: int
    nr_ops: int

@dataclass
class UPerfResults:
    """
    This is the output data structure for the success case.
    """
    profile_name: str
    # TODO: Switch to timestamp once supported.
    raw: typing.Dict[int, UPerfRawData] # Timestamp to data


@dataclass
class UPerfError:
    """
    This is the output data structure in the error  case.
    """
    error: str


def start_server():
    # Note: Uperf calls it 'slave'
    return subprocess.Popen(['uperf', '-s']) 

def start_client(protocol):
    process_env = os.environ.copy()
    # Pass variables into profile.
    process_env["h"] = "127.0.0.1"
    process_env["proto"] = protocol
    process_env["dur"] = "10s"
    # TODO: Generate various types of profiles instead of using a sample profile.
    # Note: uperf calls this 'master'
    return subprocess.Popen(['uperf', '-vaR', '-i', '1', '-m', os.getcwd() + '/profiles/sample.xml'],
        stdout=subprocess.PIPE, env=process_env)

# TODO: Make running server its own step. And make it run on a timer.

def process_output(output: bytes) -> typing.Tuple[str, typing.Union[UPerfResults, UPerfError]]:
    decoded_output = output.decode("utf-8")
    profile_run_search = re.search(r"running profile:(.+) \.\.\.", decoded_output)
    if (profile_run_search == None):
        return "error", UPerfError("Could not find profile name")

    profile_run = profile_run_search.group(1)

    timeseries_data = {}

    # There are multiple values for the name field. What we care about depends on the workload.
    tx_name = "Txn2" # TODO: Account for other possible desired values.
    timeseries_data_search = re.findall(rf"timestamp_ms:([\d\.]+) name:{tx_name} nr_bytes:(\d+) nr_ops:(\d+)", decoded_output)
    for datapoint in timeseries_data_search:
        # For now, multiplying by 1000 to get unique times as integers.
        timeseries_data[int(float(datapoint[0])*1000)] = UPerfRawData(int(datapoint[1]), int(datapoint[2]))

    return "success", UPerfResults(profile_name=profile_run, raw=timeseries_data)

# The following is a decorator (starting with @). We add this in front of our function to define the metadata for our
# step.
@plugin.step(
    id="uperf",
    name="UPerf Run",
    description="Runs uperf locally",
    outputs={"success": UPerfResults, "error": UPerfError},
)
def run_uperf(params: UPerfParams) -> typing.Tuple[str, typing.Union[UPerfResults, UPerfError]]:
    """
    Runs a uperf benchmark locally

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """
    # Launch slave first
    server_process = start_server()

    with start_client(params.protocol) as master_process:
        outs, errs = master_process.communicate()

    server_process.terminate() # Graceful termination request
    if errs != None and len(errs) > 0:
        return "error", UPerfError(errs.decode("utf-8"))

    return process_output(outs)


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        run_uperf,
    )))
