#!/usr/bin/env python3.9

import sys
import typing
from dataclasses import dataclass
import xml_dataclasses
from xml_dataclasses import xml_dataclass
import xml.etree.ElementTree as ET
from typing import List
from arcaflow_plugin_sdk import plugin
import subprocess
import os
import re
import enum

# Constants

profile_path = os.getcwd() + '/profile.xml'

# Profile data class components

@xml_dataclass
@dataclass
class ProfileFlowOp():
    type: str
    options: typing.Optional[str] = None
    __ns__: typing.Optional[str] = None


@xml_dataclass
@dataclass
class ProfileTransaction():
    flowop: List[ProfileFlowOp]
    iterations: typing.Optional[str] = None
    duration: typing.Optional[str] = None
    rate: typing.Optional[str] = None
    __ns__: typing.Optional[str] = None


@xml_dataclass
@dataclass
class ProfileGroup():
    nthreads: str
    transaction: List[ProfileTransaction]
    __ns__: typing.Optional[str] = None


@xml_dataclass
@dataclass
class Profile():
    name: str
    group: List[ProfileGroup]
    __ns__: typing.Optional[str] = None

# Params and results

@dataclass
class UPerfServerParams():
    # How long to run the server
    run_duration: int = 60

@dataclass
class UPerfServerError():
    error_code: int
    error: str

@dataclass
class UPerfServerResults():
    pass

@dataclass
class IProtocol(enum.Enum):
    TCP = "tcp"
    UDP = "udp"

@dataclass
class UPerfParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    server_addr: str
    profile: Profile
    protocol: IProtocol = IProtocol.TCP
    run_duration_ms: int = 5000

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

def write_profile(params: UPerfParams):
    tree = xml_dataclasses.dump(params.profile, "profile", None)
    # This project requires indented/formatted XML.
    ET.indent(tree)
    ET.ElementTree(tree) \
        .write(profile_path, encoding='us-ascii', xml_declaration=True)
    # It requires a newline at end of file
    with open(profile_path, "a") as profile_xml_file:
        profile_xml_file.write("\n")

def clean_profile():
    if os.path.exists(profile_path):
        os.remove(profile_path)

def start_client(params: UPerfParams):
    process_env = os.environ.copy()
    # Pass variables into profile.
    process_env["h"] = params.server_addr
    process_env["proto"] = params.protocol.value
    process_env["dur"] = str(params.run_duration_ms) + "ms"
    # TODO: Generate various types of profiles instead of using a sample profile.
    # Note: uperf calls this 'master'
    return subprocess.Popen(['uperf', '-vaR', '-i', '1', '-m', profile_path ],
        stdout=subprocess.PIPE, env=process_env, cwd=os.getcwd())

def process_output(output: bytes) -> typing.Tuple[str, typing.Union[UPerfResults, UPerfError]]:
    decoded_output = output.decode("utf-8")
    profile_run_search = re.search(r"running profile:(.+) \.\.\.", decoded_output)
    if (profile_run_search == None):
        return "error", UPerfError("Failed to parse output: could not find profile name.\nOutput: " + decoded_output)

    profile_run = profile_run_search.group(1)

    timeseries_data = {}

    # There are multiple values for the name field. What we care about depends on the workload.
    tx_name = "Txn2" # TODO: Account for other possible desired values.
    timeseries_data_search = re.findall(rf"timestamp_ms:([\d\.]+) name:{tx_name} nr_bytes:(\d+) nr_ops:(\d+)", decoded_output)
    for datapoint in timeseries_data_search:
        # For now, multiplying by 1000 to get unique times as integers.
        timeseries_data[int(float(datapoint[0])*1000)] = UPerfRawData(int(datapoint[1]), int(datapoint[2]))

    if (len(timeseries_data_search) == 0):
        return "error", UPerfError("No results found.\nOutput: " + decoded_output)

    return "success", UPerfResults(profile_name=profile_run, raw=timeseries_data)


@plugin.step(
    id="uperf_server",
    name="UPerf Server",
    description="Runs the passive UPerf server to allow benchmarks between the client and this server",
    outputs={"success": UPerfServerResults, "error": UPerfServerError},
)
def run_uperf_server(params: UPerfServerParams) -> typing.Tuple[str,
        typing.Union[UPerfServerResults, UPerfServerError]]:
    # Start the passive server
    # Note: Uperf calls it 'slave'
    try:
        result = subprocess.run(['uperf', '-s'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=params.run_duration)
        # It should not end itself, so getting here means there was an error.
        return "error", UPerfServerError(result.returncode, result.stdout.decode("utf-8") +
            result.stderr.decode("utf-8"))
    except subprocess.TimeoutExpired:
        # Worked as intended. It doesn't end itself, so it finished when it timed out.
        return "success", UPerfServerResults()


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
    clean_profile()
    write_profile(params)

    with start_client(params) as master_process:
        outs, errs = master_process.communicate()
    clean_profile()

    if errs != None and len(errs) > 0:
        return "error", UPerfError(outs + "\n" + errs.decode("utf-8"))
    if outs.find(b"aborted") != -1:
        return "error", UPerfError("Errors found in run. Output:\n" + outs.decode("utf-8"))

    # Debug output
    print(outs.decode("utf-8"))

    return process_output(outs)


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        run_uperf_server,
        run_uperf,
    )))
