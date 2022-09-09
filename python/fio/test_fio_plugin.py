#!/usr/bin/env python3

import unittest
import json
from pathlib import Path
import sys

import yaml
from arcaflow_plugin_sdk import plugin

import fio_plugin
import fio_schema


with open("fixtures/poisson-rate-submission_output-plus.json", "r") as fout:
    poisson_submit_outfile = fout.read()

poisson_submit_output = json.loads(poisson_submit_outfile)

with open("fixtures/poisson-rate-submission_input.yaml", "r") as fin:
    poisson_submit_infile = fin.read()

poisson_submit_input = fio_schema.fio_input_schema.unserialize(
    yaml.safe_load(poisson_submit_infile)
)


class FioPluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            fio_schema.fio_input_schema.unserialize(
                yaml.safe_load(poisson_submit_infile)
            )
        )

        plugin.test_object_serialization(
            fio_plugin.fio_output_schema.unserialize(poisson_submit_output)
        )

    def test_functional_success(self):
        job = fio_schema.fio_input_schema.unserialize(
            yaml.safe_load(poisson_submit_infile)
        )
        job.cleanup = False
        output_id, output_data = fio_plugin.run(job)

        # if the command didn't succeed, fio-plus.json won't exist.
        try:
            self.assertEqual("success", output_id)
        except AssertionError as e:
            sys.stderr.write("Error: {}\n".format(output_data.error))
            raise

        with open("fio-plus.json", "r") as fio_output_file:
            fio_results = fio_output_file.read()
            output_actual: fio_plugin.FioSuccessOutput = (
                fio_schema.fio_output_schema.unserialize(
                    json.loads(fio_results)
                )
            )

        self.assertEqual(output_data, output_actual)

        Path("fio-plus.json").unlink(missing_ok=True)
        Path("fio-input-tmp.fio").unlink(missing_ok=True)
        Path(job.name + ".0.0").unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
