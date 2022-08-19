# smallfile workload plugin for Arcaflow

arca-smallfile is a workload plugin of the [smallfile](https://github.com/distributed-system-analysis/smallfile) benchmark tool
using the [Arcaflow python SDK](https://github.com/arcalot/arcaflow-plugin-sdk-python).

Supported smallfile parameters are defined in the `SmallfileParams` schema of the [smallfile_schema.py](smallfile_schema.py) file.
You define your test parameters in a YAML file to be passed to the plugin command as shown in [smallfile-example.yaml](smallfile-example.yaml).

## To run directly without the Arcaflow engine:

In order to run the [arca-smallfile plugin](smallfile_plugin.py) follow these steps:

### Containerized
1. Clone this repository
2. Create the container with `docker build -t arca-smallfile <clone_directory>`
3. Run `cat smallfile-example.yaml | docker run -i arca-smallfile -f -`

### Native
*Prerequisite: smallfile should already be installed on your system.* 

1. Clone this repository
2. Create a `venv` in the current directory with `python3 -m venv ./venv`
3. Activate the `venv` by running `source ./venv/bin/activate`
4. Run `pip install -r requirements.txt`
5. Edit `smallfile_plugin.py` to set `smallfile_dir=<path_to_smallfile_dir>`
6. Run `./smallfile_plugin.py -f smallfile-example.yaml`
