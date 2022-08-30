#!/usr/bin/env python3


from os import system
import sys
import typing
import tempfile
import yaml
import json
import subprocess
import os
import enum
import dataclasses
from dataclasses import dataclass, field

from arcaflow_plugin_sdk import plugin
from arcaflow_plugin_sdk import schema
from arcaflow_plugin_sdk import annotations


class Stressors(enum.Enum):
    CPU = "cpu"
    VM = "vm"
    MATRIX = "matrix"
    MQ = "mq"


@dataclass
class CpuStressorParams:
    """
    The parameters for the CPU stressor
    """

    stressor: str
    cpu_count: int = field(
        metadata={
            "name": "CPU count",
            "description": "Number of CPU cores to be used (0 means all)",
        }
    )
    cpu_method: typing.Optional[str] = field(
        default="all",
        metadata={
            "name": "CPU stressor method",
            "description": "fine grained control of which cpu stressors to use (ackermann, cfloat etc.",
        },
    )

    def to_jobfile(self) -> str:
        result = "cpu {}\n".format(self.cpu_count)
        if self.cpu_method is not None:
            result = result + "cpu-method {}\n".format(self.cpu_method)
        return result


@dataclass
class VmStressorParams:
    """
    The parameters for the vm (virtual memory) stressor
    vm: number of virtual-memory stressors
    vm_bytes: amount of vm stressor memory
    """

    stressor: str
    vm: int = field(
        metadata={
            "name": "VM count",
            "description": "Number of VM stressors to be run (0 means 1 stressor per CPU",
        }
    )
    vm_bytes: str = field(
        metadata={
            "name": "VM memory",
            "description": "Amount of memory a single VM stressor will use",
        }
    )
    mmap: typing.Optional[str] = field(
        default=None,
        metadata={"name": "mmap", "description": "Number of stressors per CPU"},
    )
    mmap_bytes: typing.Optional[str] = field(
        default=None, metadata={"name": "Allocation of memory per stressor"}
    )

    def to_jobfile(self) -> str:
        vm = "vm {}\n".format(self.vm)
        vm_bytes = "vm-bytes {}\n".format(self.vm_bytes)
        result = vm + vm_bytes
        if self.mmap is not None:
            result = result + "mmap {}\n".format(self.mmap)
        if self.mmap_bytes is not None:
            result = result + "mmap-bytes {}\n".format(self.mmap_bytes)
        return result


@dataclass
class MatrixStressorParams:
    """
    This is the data structure that holds the results for the Matrix stressor.
    This stressor is a good way to exercise the CPU floating point operations
    as well as memory and processor data cache
    """

    stressor: str
    matrix: int = field(
        metadata={
            "name": "Matrix count",
            "description": "Number of Matrix stressors to be run (0 means 1 stressor per CPU",
        }
    )

    def to_jobfile(self) -> str:
        matrix = "matrix {}\n".format(self.matrix)
        result = matrix
        return result


@dataclass
class MqStressorParams:
    """
    This is the data structure that holds the results for the MQ stressor
    """

    stressor: str
    mq: int = field(
        metadata={
            "name": "MQ count",
            "description": "Number of MQ stressors to be run (0 means 1 stressor per CPU",
        }
    )

    def to_jobfile(self) -> str:
        mq = "mq {}\n".format(self.mq)
        result = mq
        return result


@dataclass
class StressNGParams:
    """
    The parameters in this schema will be passed through to the stressng
    command unchanged
    """

    timeout: str = field(
        metadata={"name": "Runtime", "description": "Time to run the benchmark test"}
    )
    cleanup: bool = field(
        metadata={"name": "Cleanup", "description": "Cleanup after the benchmark run"}
    )
    items: typing.List[
        typing.Annotated[
            typing.Union[
                typing.Annotated[
                    CpuStressorParams, annotations.discriminator_value("cpu")
                ],
                typing.Annotated[
                    VmStressorParams, annotations.discriminator_value("vm")
                ],
                typing.Annotated[
                    MatrixStressorParams, annotations.discriminator_value("matrix")
                ],
                typing.Annotated[
                    MqStressorParams, annotations.discriminator_value("mq")
                ],
            ],
            annotations.discriminator("stressor"),
        ]
    ]
    verbose: typing.Optional[bool] = field(
        default=None, metadata={"name": "verbose", "description": "verbose output"}
    )
    metrics_brief: typing.Optional[bool] = field(
        default=None,
        metadata={
            "name": "brief metrics",
            "description": "Brief version of the metrics output",
        },
    )

    def to_jobfile(self) -> str:
        result = "timeout {}\n".format(self.timeout)
        if self.verbose is not None:
            result = result + "verbose {}\n".format(self.verbose)
        if self.metrics_brief is not None:
            result = result + "metrics-brief {}\n".format(self.metrics_brief)
        return result


@dataclass
class WorkloadParams:
    """
    This is the data structure for the input parameters of the step
    defined below
    """

    StressNGParams: StressNGParams
    cleanup: typing.Optional[bool] = "True"


@dataclass
class SystemInfoOutput:
    """
    This is the data structure that holds the generic info for the
    tested system
    """

    stress_ng_version: str = dataclasses.field(
        metadata={
            "id": "stress-ng-version",
            "name": "stress_ng_version",
            "description": "version of the stressng tool used",
        }
    )
    run_by: str = dataclasses.field(
        metadata={
            "id": "run-by",
            "name": "run_by",
            "description": "username of the person who ran the test",
        }
    )
    date: str = dataclasses.field(
        metadata={
            "id": "date-yyyy-mm-dd",
            "name": "data",
            "description": "date on which the test was run",
        }
    )
    time: str = dataclasses.field(
        metadata={
            "id": "time-hh-mm-ss",
            "name": "time",
            "description": "time at which the test was run",
        }
    )
    epoch: int = dataclasses.field(
        metadata={
            "id": "epoch-secs",
            "name": "epoch",
            "description": "epoch at which the test was run",
        }
    )
    hostname: str = field(
        metadata={"name": "hostname", "description": "host on which the test was run"}
    )
    sysname: str = field(metadata={"name": "system name", "description": "System name"})
    nodename: str = field(
        metadata={
            "name": "nodename",
            "description": "name of the node on which the test was run",
        }
    )
    release: str = field(
        metadata={
            "name": "release",
            "description": "kernel release on which the test was run",
        }
    )
    version: str = field(
        metadata={"name": "version", "description": "version on which the test was run"}
    )
    machine: str = field(
        metadata={
            "name": "machine",
            "description": "machine type on which the test was run",
        }
    )
    uptime: int = field(
        metadata={
            "name": "uptime",
            "description": "uptime of the machine the test was run on",
        }
    )
    totalram: int = field(
        metadata={
            "name": "totalram",
            "description": "total amount of RAM the test machine had",
        }
    )
    freeram: int = field(
        metadata={
            "name": "freeram",
            "description": "amount of free RAM the test machine had",
        }
    )
    sharedram: int = field(
        metadata={
            "name": "sharedram",
            "description": "amount of shared RAM the test machine had",
        }
    )
    bufferram: int = field(
        metadata={
            "name": "bufferram",
            "description": "amount of buffer RAM the test machine had",
        }
    )
    totalswap: int = field(
        metadata={
            "name": "totalswap",
            "description": "total amount of swap the test machine had",
        }
    )
    freeswap: int = field(
        metadata={
            "name": "bufferram",
            "description": "amount of free swap the test machine had",
        }
    )
    pagesize: int = field(
        metadata={
            "name": "pagesize",
            "description": "memory page size the test machine used",
        }
    )
    cpus: int = field(
        metadata={
            "name": "cpus",
            "description": "number of CPU cores the test machine had",
        }
    )
    cpus_online: int = dataclasses.field(
        metadata={
            "id": "cpus-online",
            "name": "cpus_online",
            "description": "number of online CPUs the test machine had",
        }
    )
    ticks_per_second: int = dataclasses.field(
        metadata={
            "id": "ticks-per-second",
            "name": "ticks_per_second",
            "description": "ticks per second used on the test machine",
        }
    )


system_info_output_schema = plugin.build_object_schema(SystemInfoOutput)


@dataclass
class VMOutput:
    """
    This is the data structure that holds the results for the VM stressor
    """

    stressor: str
    bogo_ops: int = dataclasses.field(metadata={"id": "bogo-ops"})
    bogo_ops_per_second_usr_sys_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-usr-sys-time"}
    )
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"}
    )
    wall_clock_time: float = dataclasses.field(metadata={"id": "wall-clock-time"})
    user_time: float = dataclasses.field(metadata={"id": "user-time"})
    system_time: float = dataclasses.field(metadata={"id": "system-time"})
    cpu_usage_per_instance: float = dataclasses.field(
        metadata={"id": "cpu-usage-per-instance"}
    )


vm_output_schema = plugin.build_object_schema(VMOutput)


@dataclass
class CPUOutput:
    """
    This is the data structure that holds the results for the CPU stressor
    """

    stressor: str
    bogo_ops: int = dataclasses.field(metadata={"id": "bogo-ops"})
    bogo_ops_per_second_usr_sys_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-usr-sys-time"}
    )
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"}
    )
    wall_clock_time: float = dataclasses.field(metadata={"id": "wall-clock-time"})
    user_time: float = dataclasses.field(metadata={"id": "user-time"})
    system_time: float = dataclasses.field(metadata={"id": "system-time"})
    cpu_usage_per_instance: float = dataclasses.field(
        metadata={"id": "cpu-usage-per-instance"}
    )


cpu_output_schema = plugin.build_object_schema(CPUOutput)


@dataclass
class MatrixOutput:
    """
    This is the data structure that holds the results for the Matrix stressor
    """

    stressor: str
    bogo_ops: int = dataclasses.field(metadata={"id": "bogo-ops"})
    bogo_ops_per_second_usr_sys_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-usr-sys-time"}
    )
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"}
    )
    wall_clock_time: float = dataclasses.field(metadata={"id": "wall-clock-time"})
    user_time: float = dataclasses.field(metadata={"id": "user-time"})
    system_time: float = dataclasses.field(metadata={"id": "system-time"})
    cpu_usage_per_instance: float = dataclasses.field(
        metadata={"id": "cpu-usage-per-instance"}
    )


matrix_output_schema = plugin.build_object_schema(MatrixOutput)


@dataclass
class MQOutput:
    """
    This is the data structure that holds the results for the MQ stressor
    """

    stressor: str
    bogo_ops: int = dataclasses.field(metadata={"id": "bogo-ops"})
    bogo_ops_per_second_usr_sys_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-usr-sys-time"}
    )
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"}
    )
    wall_clock_time: float = dataclasses.field(metadata={"id": "wall-clock-time"})
    user_time: float = dataclasses.field(metadata={"id": "user-time"})
    system_time: float = dataclasses.field(metadata={"id": "system-time"})
    cpu_usage_per_instance: float = dataclasses.field(
        metadata={"id": "cpu-usage-per-instance"}
    )


mq_output_schema = plugin.build_object_schema(MQOutput)


@dataclass
class WorkloadResults:
    """
    This is the output data structure for the success case
    """

    systeminfo: SystemInfoOutput
    vminfo: typing.Optional[VMOutput] = None
    cpuinfo: typing.Optional[CPUOutput] = None
    matrixinfo: typing.Optional[MatrixOutput] = None
    mqinfo: typing.Optional[MQOutput] = None


@dataclass
class WorkloadError:
    """
    This is the output data structure for the failure case
    """

    error: str


# The following is a decorator (starting with @). We add this in front of our function to define the medadata for our step.
@plugin.step(
    id="workload",
    name="stress-ng workload",
    description="Run the stress-ng workload with the given parameters",
    outputs={"success": WorkloadResults, "error": WorkloadError},
)
def stressng_run(
    params: WorkloadParams,
) -> typing.Tuple[str, typing.Union[WorkloadResults, WorkloadError],]:
    """
    This function is implementing the step. It needs the decorator to turn it into a step. The type hints for the params are required.
    """

    print("==>> Generating temporary jobfile...")
    # generic parameters are in the StressNGParams class (e.g. the timeout)
    result = params.StressNGParams.to_jobfile()
    # now we need to iterate of the list of items
    for item in params.StressNGParams.items:
        result = result + item.to_jobfile()

    stressng_jobfile = tempfile.mkstemp()
    stressng_outfile = tempfile.mkstemp()

    # write the temporary jobfile
    try:
        with open(stressng_jobfile[1], "w") as jobfile:
            try:
                jobfile.write(result)
            except IOError as error:
                return "error", WorkloadError(
                    f"{error} while trying to write {stressng_jobfile[1]}"
                )
    except EnvironmentError as error:
        return "error", WorkloadError(
            f"{error} while trying to open {stressng_jobfile[1]}"
        )

    stressng_command = [
        "/usr/bin/stress-ng",
        "-j",
        stressng_jobfile[1],
        "--metrics",
        "-Y",
        stressng_outfile[1],
    ]

    print("==>> Running stress-ng with the temporary jobfile...")
    try:
        print(
            subprocess.check_output(
                stressng_command, cwd="/tmp", text=True, stderr=subprocess.STDOUT
            )
        )
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError(
            f"{error.cmd[0]} failed with return code {error.returncode}:\n{error.output}"
        )

    try:
        with open(stressng_outfile[1], "r") as output:
            try:
                stressng_yaml = yaml.safe_load(output)
            except yaml.YAMLError as error:
                print(e)
                return "error", WorkloadError(f"{error} in {stressng_outfile[1]}")
    except EnvironmentError as error:
        return "error", WorkloadError(
            f"{error} while trying to open {stressng_outfile[1]}"
        )

    system_info = stressng_yaml["system-info"]
    metrics = stressng_yaml["metrics"]

    # allocate all stressor information with None in case they don't get called
    cpuinfo_un = None
    vminfo_un = None
    matrixinfo_un = None
    mqinfo_un = None

    system_un = system_info_output_schema.unserialize(system_info)
    for metric in metrics:
        if metric["stressor"] == "cpu":
            cpuinfo_un = cpu_output_schema.unserialize(metric)
        if metric["stressor"] == "vm":
            vminfo_un = vm_output_schema.unserialize(metric)
        if metric["stressor"] == "matrix":
            matrixinfo_un = matrix_output_schema.unserialize(metric)
        if metric["stressor"] == "mq":
            mqinfo_un = mq_output_schema.unserialize(metric)

    print("==>> Workload run complete!")
    os.close(stressng_jobfile[0])
    os.close(stressng_outfile[0])

    # TODO: if cleanup is set to true, remove the temporary files
    if params.StressNGParams.cleanup == True:
        print("==>> Cleaning up operation files...")
        os.remove(stressng_jobfile[1])

    return "success", WorkloadResults(
        system_un, vminfo_un, cpuinfo_un, matrixinfo_un, mqinfo_un
    )


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                stressng_run,
            )
        )
    )
