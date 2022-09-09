#!/usr/bin/env python3

import sys
import typing
import json
import subprocess
from traceback import format_exc
from typing import Union
from pathlib import Path

from arcaflow_plugin_sdk import plugin
from fio_schema import (
    FioJob,
    FioSuccessOutput,
    FioErrorOutput,
    fio_output_schema,
)


@plugin.step(
    id="workload",
    name="fio workload",
    description="run an fio workload",
    outputs={"success": FioSuccessOutput, "error": FioErrorOutput},
)
def run(
    params: FioJob,
) -> typing.Tuple[str, Union[FioSuccessOutput, FioErrorOutput]]:
    try:
        outfile_temp_path = Path("fio-plus.json")
        infile_temp_path = Path("fio-input-tmp.fio")
        params.write_params_to_file(infile_temp_path)
        cmd = [
            "fio",
            f"{infile_temp_path}",
            "--output-format=json+",
            f"--output={outfile_temp_path}",
        ]
        subprocess.check_output(cmd)
        output: FioSuccessOutput = fio_output_schema.unserialize(
            json.loads(outfile_temp_path.read_text())
        )

        return "success", output

    except FileNotFoundError as exc:
        if exc.filename == "fio":
            error_output: FioErrorOutput = FioErrorOutput(
                "missing fio executable, please install fio package"
            )
        else:
            error_output: FioErrorOutput = FioErrorOutput(format_exc())
        return "error", error_output

    except Exception:
        error_output: FioErrorOutput = FioErrorOutput(format_exc())
        return "error", error_output

    finally:
        if params.cleanup:
            infile_temp_path.unlink(missing_ok=True)
            outfile_temp_path.unlink(missing_ok=True)
            Path(params.name + ".0.0").unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(run)))
