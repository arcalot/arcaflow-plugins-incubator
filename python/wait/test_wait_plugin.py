#!/usr/bin/env python3
import unittest

from arcaflow_plugin_sdk import plugin

import wait_plugin

WAIT_TIME = 0.1


class WaitTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            wait_plugin.InputParams(
                WAIT_TIME
            )
        )

        plugin.test_object_serialization(
            wait_plugin.SuccessOutput(
                "Waited for {} seconds".format(WAIT_TIME)
            )
        )

        plugin.test_object_serialization(
            wait_plugin.ErrorOutput(
                error="Failed waiting for {} seconds".format(WAIT_TIME)
            )
        )

    def test_functional(self):
        input_params = wait_plugin.InputParams(
            seconds=WAIT_TIME
        )

        output_id, output_data = wait_plugin.wait(input_params)

        self.assertEqual("success", output_id)
        self.assertEqual(
            output_data,
            wait_plugin.SuccessOutput(
                "Waited for {} seconds".format(WAIT_TIME)
            )
        )


if __name__ == '__main__':
    unittest.main()
