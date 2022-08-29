#!/usr/bin/env python3

import re
import tempfile
import unittest
import yaml
from filecmp import cmp
import stressng_plugin
from arcaflow_plugin_sdk import plugin


class StressNGTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            stressng_plugin.CpuStressorParams(stressor="cpu", cpu_count=2)
        )

        plugin.test_object_serialization(
            stressng_plugin.VmStressorParams(stressor="vm", vm=2, vm_bytes="2G")
        )

        plugin.test_object_serialization(
            stressng_plugin.MatrixStressorParams(stressor="matrix", matrix=2)
        )
        plugin.test_object_serialization(
            stressng_plugin.MqStressorParams(stressor="mq", mq=2)
        )

    def test_functional_cpu(self):
        # idea is to run a small cpu bound benchmark and compare its output with a known-good output
        # this is clearly not perfect, as we're limited to the field names and can't do a direct
        # comparison of the returned values

        cpu = stressng_plugin.CpuStressorParams(
            stressor="cpu", cpu_count=2, cpu_method="all"
        )

        stress = stressng_plugin.StressNGParams(
            timeout="99m", cleanup="False", items=[cpu]
        )

        input = stressng_plugin.WorkloadParams(StressNGParams=stress, cleanup="False")

        reference_jobfile = "./reference_jobfile"

        result = stress.to_jobfile()

        for item in stress.items:
            result = result + item.to_jobfile()

        with open(reference_jobfile, "r") as file:
            try:
                reference = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print(e)

        self.assertEqual(yaml.safe_load(result), reference)

    # TODO: Create a test for the actual output of stressng.


if __name__ == "__main__":
    unittest.main()
