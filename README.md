# Unofficial test and under-development plugins repository for Arcaflow

This is the repository for unofficial Arcaflow plugins that are under development or used for testing purposes.

**These plugins should be considered unmaintained and possibly even unsafe, so please review any code carefully before using it.**

## Contributing a plugin

In order to contribute a plugin, please fork the repository and add your plugin to either the [go](go) or the [python](python) folder. We currently only support these two languages with SDKs.

## Requirements for plugins

### Basic requirements:

- Your plugin should include a `README.md` file that explains the basic function of how to use the plugin as a standalone script and the functions it uses.
- You should have tests, they should run in a network-disconnected environment, and they should run from the Dockerfile.
- Your code should use the official Arcaflow plugin SDKs.
- All schema fields should have a [name and a description](https://arcalot.github.io/arcaflow/creating-plugins/python/#metadata).

### License requirements

- The code committed to this repository MUST be licensed under the Apache 2.0 license.
- You MUST NOT copy code from other projects, even if they are Apache 2.0 licensed, as there may be requirements to keep copyright notices. Include other projects as dependencies instead.
- You MAY include dependencies (code or runtime) under the following licenses:
  - Apache License 2.0
  - BSD (0-clause, 2-clause or 3-clause)
  - EPL 2.0
  - GPLv2 or later
  - LGPLv2 or later
  - MIT, MIT-0
  - CC0
  - Unlicense
- Any copyright notices MUST read "Arcalot contributors".
- Your plugin code MUST NOT include copyright or license headers in each file.

### Container requirements

- Your plugin should contain a `Dockerfile` that is based on CentOS Stream 8 (`quay.io/centos/centos:stream8`).
- Your `Dockerfile` should install all utilities that are required to run your plugin, and your image must work in a network-disconnected environment.
- Your `Dockerfile` should use [multiple build stages](https://docs.docker.com/develop/develop-images/multistage-build/) if interim utilities such as `git` are needed to enable your plugin workload.
- The [LICENSE file from arcaflow-plugins](https://github.com/arcalot/arcaflow-plugins/blob/main/LICENSE) MUST be included in the container image next to your runnable plugin.
- Your `ENTRYPOINT` MUST point to your plugin with the full path in the JSON-array-form (array), while the default `CMD` should be empty. See [the Dockerfile documentation](https://docs.docker.com/engine/reference/builder/#understand-how-cmd-and-entrypoint-interact) for details.
- Unless your plugin runs in privileged mode (see labels below), your Dockerfile must switch to the user ID and group ID of `1000`.

### Container labels

You must add the following labels to your container:

|Label|Description|
|-----|-----------|
|`org.opencontainers.image.source`|a link to the target directory in the main branch of this repository|
|`org.opencontainers.image.licenses`|a valid [SPDX license expression](https://spdx.dev/spdx-specification-21-web-version/#h.jxpfx0ykyb60) describing the licenses of the components in the image. (e.g. `Apache-2.0` AND `GPL-2.0`)|
|`org.opencontainers.image.vendor`|must be `Arcalot project`|
|`org.opencontainers.image.authors`|must be `Arcalot contributors`|
|`org.opencontainers.image.title`|a human-readable name for the plugin|
|`io.github.arcalot.arcaflow.plugin.version`|must be `1`|
|`io.github.arcalot.arcaflow.plugin.privileged`|can be set to `0` if your plugin can only run unprivileged, or `1` if your plugin can only run privileged. Default to both execution modes. The plugin must still be able to start unprivileged and provide a schema even if it normally runs privileged|
|`io.github.arcalot.arcaflow.plugin.hostnetwork`|can be set to `0` if your plugin can only run on the container network, or `1` if it can only run on the host network. Default to both execution modes|

### Requirements for Go plugins

- You should use the standard Go tooling and add the `go.mod` and `go.sum` files.
- Your code should be gofmt'd.
- Tests should be runnable using `go test ./...` and report the output in the standard Go test output format.
- Running `go generate ./...` should not produce changes in the git tree. (`git diff` should be empty after running `go generate`.)
- Your code should pass the [golangci-lint vetting](go/.golangci.yml).
- Add all `LICENSE` and `NOTICE` files for any dependencies to your container image.

### Requirements for Python plugins

- Your code should be runnable with Python 3.10.
- Your project should include a `requirements.txt` or a `pyproject.toml` with all relevant dependencies declared.
- All tests should be included in files called `test_*.py`. These files must be directly runnable and exit with a non-zero exit code if the tests failed.
- Your code should be formatted according to [PEP-8](https://peps.python.org/pep-0008/). Use [autopep8](https://pypi.org/project/autopep8/) if your IDE does not support formatting.