#!/usr/bin/env python3.9

import sys
import traceback
import typing
from dataclasses import dataclass, field
from arcaflow_plugin_sdk import plugin, validation


@dataclass
class InputParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    name: typing.Annotated[str, validation.min(1)] = field(metadata={
        "name": "Name",
        "description": "Enter your name here."
    })


@dataclass
class SuccessOutput:
    """
    This is the output data structure for the success case.
    """
    message: str = field(metadata={"name": "Message", "description": "A friendly greeting message."})


@dataclass
class ErrorOutput:
    """
    This is the output data structure in the error  case.
    """
    error: str = field(metadata={"name": "Error", "description": "An explanation why the execution failed."})


# The following is a decorator (starting with @). We add this in front of our function to define the metadata for our
# step.
@plugin.step(
    id="hello-world",
    name="Hello world!",
    description="Says hello :)",
    outputs={"success": SuccessOutput, "error": ErrorOutput},
)
def hello_world(params: InputParams) -> typing.Tuple[str, typing.Union[SuccessOutput, ErrorOutput]]:
    """
    The function  is the implementation for the step. It needs the decorator above to make it into a  step. The type
    hints for the params are required.

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """

    try:
        return "success", SuccessOutput(
            "Hello, {}!".format(params.name))
    except Exception as e:
        return "error", ErrorOutput(
            ''.join(traceback.format_exception(e))
        )


if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        hello_world,
    )))
