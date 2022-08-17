# sysbench workload plugin for Arcaflow

arca-sysbench is a workload plugin of the [sysbench](https://github.com/akopytov/sysbench) benchmark tool
using the [Arcaflow python SDK](https://github.com/arcalot/arcaflow-plugin-sdk-python).

Supported sysbench input parameters are defined in the `SysbenchInputParams` schema of the [sysbench_plugin.py](sysbench_plugin.py) file.
You define your test parameters in a YAML file to be passed to the plugin command as shown in either [sysbench_cpu_example.yaml](sysbench_cpu_example.yaml) or [sysbench_memory_example.yaml](sysbench_memory_example.yaml).

## To test:

In order to run the [arca-sysbench plugin](sysbench_plugin.py) run the following steps:

### Containerized
1. Cone this repository
2. Create the container with `docker build -t arca-sysbench -f Dockerfile`
3. Run `cat configs/sysbench_cpu_example.yaml | docker run -i arca-sysbench -s sysbenchcpu -f -` to run sysbench for cpu
4. Run `cat configs/sysbench_memory_example.yaml | docker run -i arca-sysbench -s sysbenchmemory -f -` to run sysbench for memory


### Native
*Prerequisite: sysbench should already be installed on your system.* 

1. Clone this repository
2. Create a `venv` in the current directory with `python3 -m venv $(pwd)/venv`
3. Activate the `venv` by running `source venv/bin/activate`
4. Run `pip install -r requirements.txt`
5. Run `./sysbench_plugin.py -f configs/sysbench_cpu_example.yaml -s sysbenchcpu` to run sysbench for cpu
6. Run `./sysbench_plugin.py -f configs/sysbench_memory_example.yaml -s sysbenchmemory` to run sysbench for memory
