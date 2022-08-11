# Stressng workload plugin for Arcaflow

arca-stressng is a workload plugin for the [stressng](https://github.com/ColinIanKing/stress-ng) benchmark tool. It is using the [Arcaflow python SDK](https://github.com/arcalot/arcaflow-plugin-sdk-python).

The supported workflow parameters (not all are implemented yet) and the working stressors can be found in the `WorkloadParams` schema of the [stressng_plugin.py](stressng_plugin.py) file. 
Define your paramaters in the YAML file to be passed to the plugin. 

## To test

### Prerequisites
The plugin expects the stress-ng binary in `/usr/bin/`, so if you have it installed in a different location, please create a symlink. 

In order to run the [stressng plugin](stressng_plugin.py), run the following steps:

1. Clone this repository
2. Create a `venv` in the current directory with `python3 -m venv $(pwd)/venv`
3. Activate the `venv` by running `source venv/bin/activate`
4. Run `pip install -r requirements`
5. Run `./stressng_plugin.py -f stressng_example.yaml`
