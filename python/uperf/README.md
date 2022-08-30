# arca-uperf

This plugin handles all components of uperf to run the given benchmark profile.

### Operation

This plugin contains two parts: the server and the client. Both need to be running for uperf to run benchmarks.

To start the server, specify how long to run it for. It should be at least 5 seconds longer than the client is run.

```
# yaml-language-server:$schema=uperf_server.input.schema.json

run_duration: 15
```

To start the client, a profile must be defined in the input.

If using arcaflow to orchistrate uperf, it is recommended that you don't over-complicate the profiles and instead break them down into the tests you want to do, then have arcaflow run them.

A a profile is comprised of groups, which are comprised of transactions, which are comprised of flowops.

For more information, see [uperf's documentation](https://uperf.org/manual.html) and the fully-documented schema for this plugin. All options that uperf profiles support are included in the schema. If you include the schema header in your yaml files and your editor has a compatible yaml extension, you will get suggestions and documentation provided while editing your yaml file.

Example
```
# yaml-language-server:$schema=uperf.input.schema.json

name: "netperf"
groups:
  - nthreads: 1
    transactions:
      - iterations: 1
        flowops:
          - type: "accept"
            remotehost: "server"
            protocol: "tcp"
            wndsz: 50
            tcp_nodelay: true
      - duration: "10s"
        flowops:
          - type: "write"
            size: 90
          - type: "read"
            size: 90
      - iterations: 1
        flowops:
          - type: "disconnect"
```

### Running

First, create the yaml files for the client and server inputs. You will pass these into the steps. In the examples below, I use the provided inputs from the input folder.

#### Without containers

First, create a virtual environment and install the items in the requirements.txt
```
python -m venv test
source test/bin/activate
pip install -r requirements.txt
```

Update the input/netperf.yaml.
```
remotehost: 127.0.0.1
```

In separate shells on the same or separate machines, you need to run both steps.

The server:
```
python uperf_plugin.py -s uperf_server --file input/server_input.yaml
```

And the client:
```
python uperf_plugin.py -s uperf --file input/netperf.yaml
```

#### With docker-compose or podman-compose

First, build the containers with `docker-compose build` or `podman-compose build`

Next, start the containers with `docker-compose up` or `podman-compose up`

Lastly, when it's complete, clean up with `docker-compose down` or `podman-compose down`
