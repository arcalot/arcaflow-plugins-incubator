# stress-ng workload plugin for Arcaflow

This plugin provides the functionality of [stress-ng](https://github.com/ColinIanKing/stress-ng) with various stressors using the 
[Arcaflow python SDK](https://github.com/arcalot/arcaflow-plugin-sdk-python).

## To run directly with the Arcaflow engine:

In order to run the [arca-stressng plugin](stressng_plugin.py) follow these steps:

### Containerized
1. Clone this repository
2. Create the container with either 
`docker build -t arca-stressng <clone-directory>` or
`podman build -t arca-stressng <clone-directory>`
3. Run the container with either
`cat stressng_example.yaml | docker run -i arca-stressng -f - ` or
`cat stressng_example.yaml | podman run -i arca-stressng -f -`

### Native
* Prerequisite: stress-ng needs to be installed on your system *

1. Clone this repository
2. Create a python `venv` in the current directory with `python3 -m venv ./venv`
3. Activate the `venv` by running `source ./venv/bin/activate`
4. Run `pip install -r requirements.txt`
5. Edit `stressng_example.yaml` to suit your needs
6. Run `./stressng_plugin.py -f stressng_example.yaml`
