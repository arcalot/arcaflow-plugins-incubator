#!/usr/bin/env python3
import socket
import unittest
import uperf_plugin
from arcaflow_plugin_sdk import plugin


class ExamplePluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            uperf_plugin.UPerfParams("127.0.0.1",
                uperf_plugin.IProtocol.TCP, 5
            )
        )

        plugin.test_object_serialization(
            uperf_plugin.UPerfServerParams(5)
        )

        plugin.test_object_serialization(
            uperf_plugin.UPerfResults("test", {})
        )

        plugin.test_object_serialization(
            uperf_plugin.UPerfServerResults()
        )

        plugin.test_object_serialization(
            uperf_plugin.UPerfError("Some error")
        )

        plugin.test_object_serialization(
            uperf_plugin.UPerfServerError(1, "Not a real error")
        )

    def test_functional(self):
        # Test the server succesfully exiting
        server_1sec_input = uperf_plugin.UPerfServerParams(1)

        output_id, _ = uperf_plugin.run_uperf_server(server_1sec_input)

        self.assertEqual("success", output_id)
        # The output data is currently empty.

        # --------------------------
        # Test error when port is in use
        # Make socket for port be in use.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 20000))
        server.listen(8)
        server.setblocking(False)
        # Run the server, which should fail.
        output_id, _ = uperf_plugin.run_uperf_server(server_1sec_input)
        server.close()

        self.assertEqual("error", output_id)

        # --------------------------
        # Test the client failing due to no server
        client_input = uperf_plugin.UPerfParams("127.0.0.1",
                uperf_plugin.IProtocol.TCP, 1
            )
        output_id, output_obj = uperf_plugin.run_uperf(client_input)
        self.assertEqual("error", output_id)
        self.assertEqual(1, output_obj.error.count("TCP: Cannot connect to 127.0.0.1:20000 Connection refused"))

        # --------------------------
        # Test an actual work case scenario
        # Start server for 1 second.
        # TODO. This requires multiple processes.


if __name__ == '__main__':
    unittest.main()
