#!/usr/bin/env python3.9

from iperf_schema import *
import sys
import typing
import xml.etree.ElementTree as ET
from typing import List
from arcaflow_plugin_sdk import plugin
import subprocess
import os
import re

# Constants

profile_path = os.getcwd() + '/profile.xml'

def write_profile(profile: Profile):
    tree = ET.Element("profile")
    tree.set("name", profile.name)
    for group in profile.groups:
        group_element = ET.Element("group")
        if group.nthreads != None:
            group_element.set("nthreads", str(group.nthreads))
        elif group.nprocs != None:
            group_element.set("nprocs", str(group.nprocs))

        for transaction in group.transactions:
            transaction_element = ET.Element("transaction")
            if transaction.iterations != None:
                transaction_element.set("iterations", str(transaction.iterations))
            elif transaction.duration != None:
                transaction_element.set("duration", str(transaction.duration))
            elif transaction.rate != None:
                transaction_element.set("rate", str(transaction.rate))

            for flowop in transaction.flowops:
                flowop_element = ET.Element("flowop")
                flowop_element.set("type", flowop.type)
                options = flowop.get_options()
                if len(options) > 0:
                    flowop_element.set("options", " ".join(options))
                transaction_element.append(flowop_element)

            group_element.append(transaction_element)

        tree.append(group_element)

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

def start_client(params: Profile):
    # If you need to pass vars into profiles, use env and copy the current environment.
    # TODO: Generate various types of profiles instead of using a sample profile.
    return subprocess.Popen(['uperf', '-vaR', '-i', '1', '-m', profile_path ],
        stdout=subprocess.PIPE, cwd=os.getcwd())

def process_output(output: bytes) -> typing.Tuple[str, typing.Union[IPerfResults, IPerfError]]:
    decoded_output = output.decode("utf-8")
    profile_run_search = re.search(r"running profile:(.+) \.\.\.", decoded_output)
    if (profile_run_search == None):
        return "error", IPerfError("Failed to parse output: could not find profile name.\nOutput: " + decoded_output)

    profile_run = profile_run_search.group(1)

    # The map of transaction to map of timestamp to data.
    timeseries_data = {}

    # There are multiple values for the name field. What we care about depends on the workload.
    timeseries_data_search = re.findall(rf"timestamp_ms:([\d\.]+) name:Txn(\d+) nr_bytes:(\d+) nr_ops:(\d+)", decoded_output)
    transaction_last_timestamp = {}
    for datapoint in timeseries_data_search:
        # For now, multiplying by 1000 to get unique times as integers.
        time = int(float(datapoint[0])*1000)
        transaction_index = int(datapoint[1])
        bytes = int(datapoint[2])
        ops = int(datapoint[3])

        # Discard zero first values.
        if ops != 0 or (transaction_index in transaction_last_timestamp):
            # Keep non-first zero values, but set ns_per_op to 0
            ns_per_op = int(1000*(time - transaction_last_timestamp[transaction_index]) / ops) if ops != 0 else 0
            # Create inner dict if new transaction result found.
            if not transaction_index in timeseries_data:
                timeseries_data[transaction_index] = {}
            # Save to the correct transaction
            timeseries_data[transaction_index][time] = IPerfRawData(bytes, ops, ns_per_op)
        # Save last transaction timestamp for use in calculating time per operation.
        transaction_last_timestamp[transaction_index] = time


    if len(timeseries_data_search) == 0:
        return "error", IPerfError("No results found.\nOutput: " + decoded_output)

    return "success", IPerfResults(profile_name=profile_run, timeseries_data=timeseries_data)


@plugin.step(
    id="iperf_server",
    name="IPerf Server",
    description="Runs the passive IPerf server to allow benchmarks between the client and this server",
    outputs={"success": IPerfServerResults, "error": IPerfServerError},
)
def run_iperf_server(params: IPerfServerParams) -> typing.Tuple[str,
        typing.Union[IPerfServerResults, IPerfServerError]]:
    # Start the passive server
    try:
        result = subprocess.run(['uperf', '-s'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=params.run_duration)
        # It should not end itself, so getting here means there was an error.
        return "error", IPerfServerError(result.returncode, result.stdout.decode("utf-8") +
            result.stderr.decode("utf-8"))
    except subprocess.TimeoutExpired:
        # Worked as intended. It doesn't end itself, so it finished when it timed out.
        return "success", IPerfServerResults()


# The following is a decorator (starting with @). We add this in front of our function to define the metadata for our
# step.
@plugin.step(
    id="iperf",
    name="IPerf Run",
    description="Runs iperf locally",
    outputs={"success": IPerfResults, "error": IPerfError},
)
def run_iperf(params: Profile) -> typing.Tuple[str, typing.Union[IPerfResults, IPerfError]]:
    """
    Runs a iperf benchmark locally

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """
    clean_profile()
    write_profile(params)

    with start_client(params) as master_process:
        outs, errs = master_process.communicate()

    clean_profile()

    if errs != None and len(errs) > 0:
        return "error", IPerfError(outs + "\n" + errs.decode("utf-8"))
    if outs.find(b"aborted") != -1 or outs.find(b"WARNING: Errors detected during run") != -1:
        return "error", IPerfError("Errors found in run. Output:\n" + outs.decode("utf-8"))

    # Debug output
    print(outs.decode("utf-8"))

    return process_output(outs)


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        run_iperf_server,
        run_iperf,
    )))
