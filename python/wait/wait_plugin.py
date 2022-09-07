#!/usr/bin/env python3

import sys
import typing
from dataclasses import dataclass, field
from time import sleep

from arcaflow_plugin_sdk import plugin, validation


@dataclass
class InputParams:
    seconds: typing.Annotated[float, validation.min(0.0)] = field(
       metadata={
           "id": "seconds",
           "name": "seconds",
           "description": "number of seconds to wait as a floating point "
                          "number for subsecond precision."
       }
    )


@dataclass
class SuccessOutput:
    """
    This is the output data structure for the success case.
    """
    message: str


@dataclass
class ErrorOutput:
    """
    This is the output data structure in the error  case.
    """
    error: str


@plugin.step(
    id="wait",
    name="Wait",
    description="Waits for the given amount of time",
    outputs={"success": SuccessOutput, "error": ErrorOutput},
)
def wait(
    params: InputParams
) -> typing.Tuple[str, typing.Union[SuccessOutput, ErrorOutput]]:
    """
    :param params:

    :return: the string identifying which output it is,
             as well the output structure
    """
    try:
        sleep(params.seconds)
        return "success", SuccessOutput(
            "Waited for {} seconds".format(params.seconds)
        )
    except BaseException:
        return "error", ErrorOutput(
            "Failed waiting for {} seconds".format(params.seconds)
        )


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        wait,
    )))
