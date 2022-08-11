#!/usr/bin/env python3


from os import system
import sys
import typing
import tempfile
import yaml
import json
import subprocess
import os
import enumn
import dataclasses
from dataclasses import dataclass

from arcaflow_plugin_sdk import plugin
from arcaflow_plugin_sdk import schema
from arcaflow_plugin_sdk import annotations


class Stressors(enum.Enum):
    CPU = "cpu"
    VM = "vm"
    MATRIX = "matrix"
    MQ = "mq"


@dataclass
class cpuStressorParams:
    """
    The parameters for the CPU stressor
    """
    stressor: str
    cpu_count: int
    cpu_method: typing.Optional[str] = "all"

    def to_jobfile(self) -> str:
        result = "cpu {}\n".format(self.cpu_count)
        if self.cpu_method is not None:
            result = result + "cpu-method {}\n".format(self.cpu_method)
        return result


@dataclass
class vmStressorParams:
    """
    The parameters for the vm (virtual memory) stressor
    vm: number of virtual-memory stressors
    vm_bytes: amount of vm stressor memory
    """
    stressor: str
    vm: int
    vm_bytes: str
    mmap: typing.Optional[str] = None
    mmap_bytes: typing.Optional[str] = None

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
class matrixStressorParams:
    """ 
    This is the data structure that holds the results for the Matrix stressor. 
    This stressor is a good way to exercise the CPU floating point operations
    as well as memory and processor data cache
    """
    stressor: str
    matrix: int

    def to_jobfile(self) -> str:
        matrix = "matrix {}\n".format(self.matrix)
        result = matrix
        return result


@dataclass
class mqStressorParams:
    """
    This is the data structure that holds the results for the MQ stressor 
    """
    stressor: str
    mq: int

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
    timeout: str
    cleanup: bool
    items: typing.List[
        typing.Annotated[
            typing.Union[
                typing.Annotated[cpuStressorParams,
                                 annotations.discriminator_value("cpu")],
                typing.Annotated[vmStressorParams,
                                 annotations.discriminator_value("vm")],
                typing.Annotated[matrixStressorParams,
                                 annotations.discriminator_value("matrix")],
                typing.Annotated[mqStressorParams,
                                 annotations.discriminator_value("mq")]
            ],
            annotations.discriminator("stressor")
        ]
    ]
    verbose: typing.Optional[bool] = None
    metrics_brief: typing.Optional[bool] = None

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
        metadata={"id": "stress-ng-version"})
    run_by: str = dataclasses.field(metadata={"id": "run-by"})
    date: str = dataclasses.field(metadata={"id": "date-yyyy-mm-dd"})
    time: str = dataclasses.field(metadata={"id": "time-hh-mm-ss"})
    epoch: int = dataclasses.field(metadata={"id": "epoch-secs"})
    hostname: str
    sysname: str
    nodename: str
    release: str
    version: str
    machine: str
    uptime: int
    totalram: int
    freeram: int
    sharedram: int
    bufferram: int
    totalswap: int
    freeswap: int
    pagesize: int
    cpus: int
    cpus_online: int = dataclasses.field(metadata={"id": "cpus-online"})
    ticks_per_second: int = dataclasses.field(
        metadata={"id": "ticks-per-second"})


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
    wall_clock_time: float = dataclasses.field(
        metadata={"id": "wall-clock-time"})
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
    wall_clock_time: float = dataclasses.field(
        metadata={"id": "wall-clock-time"})
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
        metadata={"id": "bogo-ops-per-second-usr-sys-time"})
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"})
    wall_clock_time: float = dataclasses.field(
        metadata={"id": "wall-clock-time"})
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
        metadata={"id": "bogo-ops-per-second-usr-sys-time"})
    bogo_ops_per_second_real_time: float = dataclasses.field(
        metadata={"id": "bogo-ops-per-second-real-time"})
    wall_clock_time: float = dataclasses.field(
        metadata={"id": "wall-clock-time"})
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
def stressng_run(params: WorkloadParams) -> typing.Tuple[str, typing.Union[WorkloadResults, WorkloadError], ]:
    # def stressng_run(params: WorkloadParams) -> str:
    """
    This function is implementing the step. It needs the decorator to turn it into a step. The type hints for the params are required.

    :param params

    :return: the string identifying which output it is, as well as the output structure
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
    with open(stressng_jobfile[1], 'w') as jobfile:
        jobfile.write(result)
    stressng_command = ["/usr/bin/stress-ng", "-j",
                        stressng_jobfile[1], "--metrics", "-Y", stressng_outfile[1]]

    print("==>> Running stress-ng with the temporary jobfile...")
    try:
        print(subprocess.check_output(stressng_command,
              cwd="/tmp", text=True, stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError(f"{error.cmd[0]} failed with return code {error.returncode}:\n{error.output}")

    with open(stressng_outfile[1], 'r') as output:
        try:
            stressng_yaml = yaml.safe_load(output)
        except yaml.YAMLError as e:
            print(e)

    system_info = (stressng_yaml['system-info'])
    metrics = (stressng_yaml['metrics'])

    # allocate all stressor information with None in case they don't get called
    cpuinfo_un = None
    vminfo_un = None
    matrixinfo_un = None
    mqinfo_un = None

    system_un = system_info_output_schema.unserialize(system_info)
    for metric in metrics:
        if metric['stressor'] == "cpu":
            cpuinfo_un = cpu_output_schema.unserialize(metric)
        if metric['stressor'] == "vm":
            vminfo_un = vm_output_schema.unserialize(metric)
        if metric['stressor'] == "matrix":
            matrixinfo_un = matrix_output_schema.unserialize(metric)
        if metric['stressor'] == "mq":
            mqinfo_un = mq_output_schema.unserialize(metric)

    print("==>> Workload run complete!")
    os.close(stressng_jobfile[0])
    os.close(stressng_outfile[0])

    # TODO: if cleanup is set to true, remove the temporary files
    if params.StressNGParams.cleanup == True:
        print("==>> Cleaning up operation files...")
        os.remove(stressng_jobfile[1])
        # os.remove(stressng_outfile)

    return "success", WorkloadResults(system_un, vminfo_un, cpuinfo_un, matrixinfo_un, mqinfo_un)


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                stressng_run,
            )
        )
    )
