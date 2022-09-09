#!/usr/bin/env python3
import socket
import unittest
import iperf_plugin
import iperf_schema
import contextlib
from arcaflow_plugin_sdk import plugin


simple_profile = iperf_schema.Profile(
    name="test", groups=[
        iperf_schema.ProfileGroup(
            nthreads=1,
            transactions= [
                iperf_schema.ProfileTransaction(
                    iterations = 1,
                    flowops = [
                        iperf_schema.AcceptFlowOp(
                            type="accept",
                            remotehost="127.0.0.1",
                            protocol=iperf_schema.IProtocol.TCP,
                            wndsz=5,
                            tcp_nodelay=True
                        )
                    ]
                ),
                iperf_schema.ProfileTransaction(
                    duration="50ms",
                    flowops = [
                        iperf_schema.WriteFlowOp(
                            type="write",
                            size=90
                        ),
                        iperf_schema.ReadFlowOp(
                            type="read",
                            size=90
                        )
                    ]
                ),
                iperf_schema.ProfileTransaction(
                    iterations = 1,
                    flowops = [
                        iperf_schema.DisconnectFlowOp(
                            type="disconnect"
                        )
                    ]
                )
            ]
        )
    ]
)

sample_profile_expected = '''<?xml version='1.0' encoding='us-ascii'?>
<profile name="test">
  <group nthreads="1">
    <transaction iterations="1">
      <flowop type="accept" options="remotehost=127.0.0.1 protocol=tcp tcp_nodelay wndsz=5k" />
    </transaction>
    <transaction duration="50ms">
      <flowop type="write" options="size=90k" />
      <flowop type="read" options="size=90k" />
    </transaction>
    <transaction iterations="1">
      <flowop type="disconnect" />
    </transaction>
  </group>
</profile>
'''

class ExamplePluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(simple_profile)

        plugin.test_object_serialization(
            iperf_plugin.IPerfServerParams(5)
        )

        plugin.test_object_serialization(
            iperf_plugin.IPerfResults("test", {})
        )

        plugin.test_object_serialization(
            iperf_plugin.IPerfServerResults()
        )

        plugin.test_object_serialization(
            iperf_plugin.IPerfError("Some error")
        )

        plugin.test_object_serialization(
            iperf_plugin.IPerfServerError(1, "Not a real error")
        )
    
    def test_profile_gen(self):
        iperf_plugin.clean_profile()
        iperf_plugin.write_profile(simple_profile)
        with open(iperf_plugin.profile_path, 'r', encoding='us-ascii') as file:
            generated_file = file.read()
        iperf_plugin.clean_profile()
        self.assertEqual(sample_profile_expected, generated_file)

    def test_functional(self):
        # Test the server succesfully exiting
        server_1sec_input = iperf_plugin.IPerfServerParams(1)

        output_id, _ = iperf_plugin.run_iperf_server(server_1sec_input)

        self.assertEqual("success", output_id)
        # The output data is currently empty.

        # --------------------------
        # Test for error when port is in use
        # Make socket for port be in use.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 20000))
        server.listen(8)
        server.setblocking(False)
        # Run the server, which should fail.
        output_id, _ = iperf_plugin.run_iperf_server(server_1sec_input)
        server.close()

        self.assertEqual("error", output_id)

        # --------------------------
        # Test the client failing due to no server

        with contextlib.redirect_stdout(None): # Hide error messages
            output_id, output_obj = iperf_plugin.run_iperf(simple_profile)
        self.assertEqual("error", output_id)
        self.assertEqual(1, output_obj.error.count("TCP: Cannot connect to 127.0.0.1:20000 Connection refused"))

        # --------------------------
        # Test an actual working scenario
        # Start server for 1 second.
        # TODO. This requires multiple processes.


if __name__ == '__main__':
    unittest.main()
