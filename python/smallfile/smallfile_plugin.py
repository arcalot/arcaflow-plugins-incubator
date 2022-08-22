#!/usr/bin/env python3

import re
import sys
import typing
import tempfile
import yaml
import json
import subprocess
import os
import shutil
import csv
from arcaflow_plugin_sdk import plugin

from smallfile_schema import WorkloadParams, WorkloadResults, WorkloadError, smallfile_schema, output_params_schema, output_results_schema, output_rsptimes_schema


# The following is a decorator (starting with @). We add this in front of our function to define the metadata for our step.
@plugin.step(
    id="workload",
    name="smallfile workload",
    description="Run the smallfile workload with the given parameters",
    outputs={"success": WorkloadResults, "error": WorkloadError},
)
def smallfile_run(params: WorkloadParams) -> typing.Tuple[str, typing.Union[WorkloadResults, WorkloadError]]:
    """
    The function  is the implementation for the step. It needs the decorator above to make it into a  step. The type
    hints for the params are required.

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """

    smallfile_dir = "/plugin/smallfile"
    smallfile_yaml_file = tempfile.mkstemp()
    smallfile_out_file = tempfile.mkstemp()

    # Copy all parameters from SmallfileParams directly for the smallfile CLI to use via YAML
    print("==>> Importing workload parameters ...")
    smallfile_params = smallfile_schema.serialize(params.smallfile_params)
    with open(smallfile_yaml_file[1], 'w') as file:
        file.write(yaml.dump(smallfile_params))

    smallfile_cmd = [
        "{}/smallfile_cli.py".format(smallfile_dir),
        "--yaml-input-file",
        smallfile_yaml_file[1],
        "--output-json",
        smallfile_out_file[1],
        "--response-times",
        "y",
    ]

    # Run smallfile workload
    print("==>> Running smallfile workload ...")
    try:
        print(subprocess.check_output(smallfile_cmd,
              cwd=smallfile_dir, text=True, stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as error:
        temp_cleanup(smallfile_yaml_file, smallfile_dir)
        return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0], error.returncode, error.output))

    with open(smallfile_out_file[1], 'r') as output:
        smallfile_results = output.read()

    smallfile_json = json.loads(smallfile_results)

    # Post-process output for response times
    print("==>> Collecting response times ...")
    elapsed_time = float(smallfile_json["results"]["elapsed"])
    start_time = smallfile_json["results"]["startTime"]
    rsptime_dir = os.path.join(smallfile_params["top"], "network_shared")
    smallfile_process_cmd = [
        "{}/smallfile_rsptimes_stats.py".format(smallfile_dir),
        "--time-interval",
        str(max(int(elapsed_time / 120.0), 1)),
        "--start-time",
        str(int(start_time)),
        rsptime_dir,
    ]

    try:
        print(subprocess.check_output(smallfile_process_cmd,
              cwd=smallfile_dir, text=True, stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as error:
        temp_cleanup(smallfile_out_file, smallfile_dir)
        return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0], error.returncode, error.output))

    rsptimes_schema_to_results_map = {
        "host_thread": "host:thread",
        "samples": " samples",
        "min": " min",
        "max": " max",
        "mean": " mean",
        "pctdev": " %dev",
        "pctile50": " 50%ile",
        "pctile90": " 90%ile",
        "pctile95": " 95%ile",
        "pctile99": " 99%ile"
    }

    smallfile_rsptimes = []
    try:
        with open("{}/stats-rsptimes.csv".format(rsptime_dir), newline='') as csvfile:
            rsptimes_csv = csv.DictReader(csvfile)
            for row in rsptimes_csv:
                if not re.match("per-", row["host:thread"]) and not re.match("cluster-", row["host:thread"]) and not re.match("time-", row["host:thread"]):
                    schema_row = dict(rsptimes_schema_to_results_map)
                    for skey, svalue in schema_row.items():
                        for key, value in row.items():
                            if svalue == key:
                                schema_row[skey] = str(value)
                                break
                    smallfile_rsptimes.append(schema_row)
    except IOError as error:
        temp_cleanup(smallfile_out_file, smallfile_dir)
        return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0], error.returncode, error.output))

    # Cleanup after run, if enabled
    if params.cleanup:
        print("==>> Cleaning up operation files ...")
        cleanup_yaml = smallfile_schema.serialize(params.smallfile_params)
        cleanup_yaml["operation"] = "cleanup"
        smallfile_cleanup_yaml = tempfile.mkstemp()
        smallfile_cleanup_cmd = [
            "{}/smallfile_cli.py".format(smallfile_dir),
            "--yaml-input-file",
            smallfile_cleanup_yaml[1],
        ]
        with open(smallfile_cleanup_yaml[1], 'w') as file:
            file.write(yaml.dump(cleanup_yaml))
        try:
            print(subprocess.check_output(smallfile_cleanup_cmd,
                  cwd=smallfile_dir, text=True, stderr=subprocess.STDOUT))
        except subprocess.CalledProcessError as error:
            temp_cleanup(smallfile_yaml_file, smallfile_dir)
            temp_cleanup(smallfile_cleanup_yaml)
            return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0], error.returncode, error.output))
        temp_cleanup(smallfile_cleanup_yaml)

    temp_cleanup(smallfile_yaml_file, smallfile_dir)
    temp_cleanup(smallfile_out_file)

    print("==>> Workload run complete!")
    return "success", WorkloadResults(output_params_schema.unserialize(smallfile_json["params"]), output_results_schema.unserialize(smallfile_json["results"]), output_rsptimes_schema.unserialize(smallfile_rsptimes))


def temp_cleanup(file=[], directory=""):
    # Cleanup our temp files
    print("==>> Cleaning up temporary files ...")
    if file:
        os.close(file[0])
        os.remove(file[1])
    if directory:
        shutil.rmtree(directory)


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        smallfile_run,
    )))
