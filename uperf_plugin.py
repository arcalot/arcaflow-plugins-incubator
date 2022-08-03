#!/usr/bin/env python3

import sys
import typing
from dataclasses import dataclass
from typing import List
from arcaflow_plugin_sdk import plugin
import subprocess
import os


@dataclass
class UPerfParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    test_type: typing.Optional[str] = None # Not used yet
    num_threads: typing.Optional[int] = 1 # Not used yet
    protocol: typing.Optional[str] = "tcp"
    message_size: typing.Optional[int] = 64 # Not used yet.
    read_message_size: typing.Optional[int] = 64 # Not used yet.


@dataclass
class UPerfResults:
    """
    This is the output data structure for the success case.
    """
    pass


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
        print("OUTPUTS: ", outs, errs)
        # TODO: Process output to generate output.

    server_process.terminate() # Graceful termination request

    return "success", UPerfResults()
    # TODO: Handle errors and return error if one is encountered.
    #return "error", PodScenarioError(
    #    "Cannot kill pod %s in namespace %s, function not implemented" % (
    #        params.pod_name_pattern.pattern,
    #        params.namespace_pattern.pattern
    #    ))


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        run_uperf,
    )))
