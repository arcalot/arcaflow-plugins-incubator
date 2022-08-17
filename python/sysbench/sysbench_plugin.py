#!/usr/bin/env python3

import re
import sys
import typing
from dataclasses import dataclass, field
from typing import List,Dict
from arcaflow_plugin_sdk import plugin,schema
import subprocess


@dataclass
class SysbenchCpuInputParams:
    """
    This is the data structure for the input parameters of Sysbench CPU benchmark.
    """
    operation: str = field(metadata={"name": "Operation", "description": "Sysbench Operation to perform"})
    threads: typing.Optional[int] = field(default=1,metadata={"name": "Threads", "description": "Number of worker threads to create"})
    events: typing.Optional[int] = field(default=0,metadata={"name": "Number of events", "description": "Maximum number of events"})
    cpumaxprime: typing.Optional[int] =  field(default=10000,metadata={"name": "CPU max prime", "description": "The upper limit of the number of prime numbers generated"})
    time: typing.Optional[int] = field(default=10,metadata={"name": "Time", "description": "Limit for total execution time in seconds"})

@dataclass
class SysbenchMemoryInputParams:
    """
    This is the data structure for the input parameters of Sysbench Memory benchmark.
    """
    operation: str = field(metadata={"name": "Operation", "description": "Sysbench Operation to perform"})
    threads: typing.Optional[int] = field(default=1,metadata={"name": "Threads", "description": "Number of worker threads to create"})
    events: typing.Optional[int] = field(default=0,metadata={"name": "Number of events", "description": "Maximum number of events"})
    time: typing.Optional[int] = field(default=10,metadata={"name": "Time", "description": "Limit for total execution time in seconds"})
    memoryblocksize: typing.Optional[str] = field(default='1KiB',metadata={"name": "Block Size", "description": "size of memory block for test in KiB/MiB/GiB"})
    memorytotalsize: typing.Optional[str] = field(default='100G',metadata={"name": "Total Size", "description": "Total size of data to transfer in GiB"})
    memoryscope: typing.Optional[str] =  field(default='global',metadata={"name": "Memory Scope", "description": "Memory Access Scope(global/local)"})
    memoryoperation: typing.Optional[str] = field(default='write',metadata={"name": "Memory Operation", "description": "Type of memory operation(write/read)"})

@dataclass
class LatencyAggregates:
    avg: float = field(metadata={"name": "Average", "description":"Average Latency"})
    min: float = field(metadata={"name": "Minimum", "description":"Minimum latency"})
    max: float = field(metadata={"name": "Maximum", "description":"Maximum Latency"})
    P95thpercentile: float = field(metadata={"name": "95th Percentile", "description":"95th percentile latency"})
    sum: float = field(metadata={"name": "Sum", "description":"Sum of latencies"})

@dataclass
class ThreadFairnessAggregates:
  avg: float = field(metadata={"name": "Average", "description":"Average value across all threads"})
  stddev: float = field(metadata={"name": "Standard Deviation", "description":"Standard deviation of all threads"})

@dataclass
class ThreadsFairness:
  events: ThreadFairnessAggregates = field(metadata={"name": "Thread Fairness events", "description": "number of events executed by the threads "})
  executiontime: ThreadFairnessAggregates = field(metadata={"name": "Thread Fairness execution time", "description": "Execution time of threads"})

@dataclass
class CPUmetrics:
    eventspersecond: float = field(metadata={"name": "Events per second", "description": "Number of events per second to measure CPU speed"})

@dataclass
class SysbenchMemoryOutputParams:
    """
    This is the data structure for output parameters returned by sysbench memory benchmark.
    """

    totaltime: float = field(metadata={"name": "Total time", "description": "Total execution time of workload"})
    totalnumberofevents: float = field(metadata={"name": "Total number of events", "description": "Total number of events performed by the workload"})
    blocksize: str = field(metadata={"name": "Block size", "description": "Block size in KiB"})
    totalsize: str = field(metadata={"name": "Total size", "description": "Total size in MiB"})
    operation: str = field(metadata={"name": "Operation", "description": "memory operation performed"})
    scope: str = field(metadata={"name": "Scope", "description": "scope of operation"})
    Totaloperationspersecond: float = field(metadata={"name": "Total operations per second", "description": "Total number of operations performed by the memory workload per second"})
    Totaloperations: float = field(metadata={"name": "Total operations", "description": "Total number of operations performed by the memory workload"})
    Numberofthreads: float = 1

@dataclass
class SysbenchCpuOutputParams:
    """
    This is the data structure for output parameters returned by sysbench cpu benchmark.
    """

    totaltime: float = field(metadata={"name": "Total time", "description": "Total execution time of workload"})
    totalnumberofevents: float = field(metadata={"name": "Total number of events", "description": "Total number of events performed by the workload"})
    Primenumberslimit: float = field(metadata={"name": "Prime numbers limit", "description": "Number of prime numbers to use for CPU workload"})
    Numberofthreads: float = 1

@dataclass
class SysbenchMemoryResultParams:
    """
    This is the output results data structure for sysbench memory results.
    """
    transferred_MiB: float = field(metadata={"name": "Transferred memory", "description": "Total Memory Transferred"})
    transferred_MiBpersec: float = field(metadata={"name": "Transferred memory per second", "description": "Total Memory Transferred per second"})
    Latency: LatencyAggregates = field(metadata={"name": "Latency", "description": "Memory Latency in mili seconds"})
    Threadsfairness: ThreadsFairness = field(metadata={"name": "Threads fairness", "description": "Event distribution by threads for number of executed events by threads and total execution time by thread"})

@dataclass
class SysbenchCpuResultParams:
    """
    This is the output results data structure for sysbench cpu results.
    """
    CPUspeed: CPUmetrics = field(metadata={"name": "CPU speed", "description": "No of events per second"})
    Latency: LatencyAggregates = field(metadata={"name": "Latency", "description": "CPU latency in miliseconds"})
    Threadsfairness: ThreadsFairness = field(metadata={"name": "Threads fairness", "description": "Event distribution by threads for number of executed events by threads and total execution time by thread"})

@dataclass
class WorkloadResultsCpu:
    """
    This is the output results data structure for the Sysbench CPU success case.
    """
    sysbench_output_params: SysbenchCpuOutputParams
    sysbench_results: SysbenchCpuResultParams

@dataclass
class WorkloadResultsMemory:
    """
    This is the output results data structure for the Sysbench memory success case.
    """
    sysbench_output_params: SysbenchMemoryOutputParams
    sysbench_results: SysbenchMemoryResultParams

@dataclass
class WorkloadError:
    """
    This is the output data structure in the error  case.
    """
    exit_code: int
    error: str

sysbench_cpu_input_schema = plugin.build_object_schema(SysbenchCpuInputParams)
sysbench_memory_input_schema = plugin.build_object_schema(SysbenchMemoryInputParams)
sysbench_cpu_output_schema = plugin.build_object_schema(SysbenchCpuOutputParams)
sysbench_cpu_results_schema = plugin.build_object_schema(SysbenchCpuResultParams)
sysbench_memory_output_schema = plugin.build_object_schema(SysbenchMemoryOutputParams)
sysbench_memory_results_schema = plugin.build_object_schema(SysbenchMemoryResultParams)


def parse_output(output):
    
    output = output.replace(" ", "")
    section = None
    sysbench_output = {}
    sysbench_results = {}
    for line in output.splitlines():

        if ":" in line:
            key, value = line.split(":")
            if key[0].isdigit():
                key="P"+key
            if value == "":
                key = re.sub(r'\((.*?)\)', "", key)
                if "options" in key or "General" in key:
                    dictionary = sysbench_output
                else:
                    dictionary = sysbench_results
                    section = key
                    dictionary[section] = {}
                continue

            if dictionary == sysbench_output:
                if "totaltime" in key:
                    value = value.replace("s", "")
                    dictionary[key] = float(value)
                elif "Totaloperations" in key:
                    to, tops = value.split("(")
                    tops = tops.replace("persecond)", "")
                    dictionary["Totaloperations"] = float(to)
                    dictionary["Totaloperationspersecond"] = float(tops)
                elif value.isnumeric():
                    dictionary[key] = float(value)
                else:
                    dictionary[key] = value

            else:
                if "latency" in key:
                    section = "Latency"
                if "(avg/stddev)" in key:
                    key = key.replace("(avg/stddev)", "")
                    avg, stddev = value.split("/")
                    dictionary[section][key] = {}
                    dictionary[section][key]["avg"] = float(avg)
                    dictionary[section][key]["stddev"] = float(stddev)
                elif value.isnumeric():
                    dictionary[section][key] = float(value)
                else:
                    dictionary[section][key] = value
        if "transferred" in line:
            mem_t, mem_tps = line.split("transferred")
            mem_tps = re.sub("[()]", "", mem_tps)
            mem_t = float(mem_t.replace("MiB", ""))
            mem_tps = float(mem_tps.replace("MiB/sec", ""))

            sysbench_results["transferred_MiB"] = mem_t
            sysbench_results["transferred_MiBpersec"] = mem_tps
    print("sysbench output : " , sysbench_output)
    print("sysbench results:", sysbench_results)
    return sysbench_output,sysbench_results

@plugin.step(
    id="sysbenchcpu",
    name="Sysbench CPU Workload",
    description="Run CPU performance test using the sysbench workload",
    outputs={"success": WorkloadResultsCpu, "error": WorkloadError},
)
def RunSysbenchCpu(params: SysbenchCpuInputParams) -> typing.Tuple[str, typing.Union[WorkloadResultsCpu, WorkloadError]]:

    print("==>> Running sysbench CPU workload ...")
    try:
        cmd=['sysbench','--threads='+str(params.threads),'--events='+str(params.events),'--time='+str(params.time),'--cpu-max-prime='+str(params.cpumaxprime),params.operation,'run']
        process_out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError(error.returncode,"{} failed with return code {}:\n{}".format(error.cmd[0],error.returncode,error.output))

    stdoutput = process_out.strip().decode("utf-8")
    try:
        output,results = parse_output(stdoutput)
    except KeyError as error:
        return "error", WorkloadError(1,"Failure in parsing sysbench output:\n{}".format(stdoutput))
    except ValueError as error:
        return "error", WorkloadError(1,"Failure in parsing sysbench output:\n{}".format(stdoutput))

    print("==>> Workload run complete!")
    
    return "success", WorkloadResultsCpu(sysbench_cpu_output_schema.unserialize(output),sysbench_cpu_results_schema.unserialize(results))
    

@plugin.step(
    id="sysbenchmemory",
    name="Sysbench Memory Workload",
    description="Run the Memory functions speed test using the sysbench workload",
    outputs={"success": WorkloadResultsMemory, "error": WorkloadError},
)
def RunSysbenchMemory(params: SysbenchMemoryInputParams) -> typing.Tuple[str, typing.Union[WorkloadResultsMemory, WorkloadError]]:

    print("==>> Running sysbench Memory workload ...")
    try:
        cmd=['sysbench','--threads='+str(params.threads),'--events='+str(params.events),'--time='+str(params.time),'--memory-block-size='+str(params.memoryblocksize),'--memory-total-size='+str(params.memorytotalsize),'--memory-scope='+str(params.memoryscope),'--memory-oper='+str(params.memoryoperation),params.operation,'run']
        process_out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError(error.returncode,"{} failed with return code {}:\n{}".format(error.cmd[0],error.returncode,error.output))

    stdoutput = process_out.strip().decode("utf-8")
    try:
        output,results = parse_output(stdoutput)
    except KeyError as error:
        return "error", WorkloadError(1,"Failure in parsing sysbench output:\n{}".format(stdoutput))
    except ValueError as error:
        return "error", WorkloadError(1,"Failure in parsing sysbench output:\n{}".format(stdoutput))

    print("==>> Workload run complete!")
    return "success", WorkloadResultsMemory(sysbench_memory_output_schema.unserialize(output),sysbench_memory_results_schema.unserialize(results))



if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        RunSysbenchCpu,
        RunSysbenchMemory
    )))
