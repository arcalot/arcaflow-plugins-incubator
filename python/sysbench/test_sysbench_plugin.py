#!/usr/bin/env python3

import re
import unittest
import sysbench_plugin
from arcaflow_plugin_sdk import plugin


class SysbenchPluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            sysbench_plugin.SysbenchCpuInputParams(
                operation="cpu",
                threads=2
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.SysbenchMemoryInputParams(
                operation="memory",
                threads=2
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_cpu_output_schema.unserialize(
                {'Numberofthreads': 2.0, 'Primenumberslimit': 10000.0, 'totaltime': 10.0008, 'totalnumberofevents': 26401.0}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_cpu_results_schema.unserialize(
                {'CPUspeed': {'eventspersecond': '2639.51'}, 'Latency': {'min': '0.67', 'avg': '0.76', 'max': '1.26', 'P95thpercentile': '0.87', 'sum': '19987.57'}, 'Threadsfairness': {'events': {'avg': 13200.5, 'stddev': 17.5}, 'executiontime': {'avg': 9.9938, 'stddev': 0.0}}}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_memory_output_schema.unserialize(
                {'Numberofthreads': 2.0, 'blocksize': '1KiB', 'totalsize': '102400MiB', 'operation': 'write', 'scope': 'global', 'Totaloperations': 72227995.0, 'Totaloperationspersecond': 7221925.38, 'totaltime': 10.0001, 'totalnumberofevents': 72227995.0}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_memory_results_schema.unserialize(
                {'transferred_MiB': 70535.15, 'transferred_MiBpersec': 7052.66, 'Latency': {'min': '0.00', 'avg': '0.00', 'max': '1.18', 'P95thpercentile': '0.00', 'sum': '13699.95'}, 'Threadsfairness': {'events': {'avg': 36113997.5, 'stddev': 710393.5}, 'executiontime': {'avg': 6.85, 'stddev': 0.07}}}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.WorkloadError(
                exit_code=1,
                error="This is an error"
            )
        )

    def test_functional_cpu(self):
        input = sysbench_plugin.SysbenchCpuInputParams(
            operation="cpu",
            threads=2
        )

        output_id, output_data = sysbench_plugin.RunSysbenchCpu(input)

        self.assertEqual("success", output_id)
        self.assertGreaterEqual(output_data.sysbench_output_params.Numberofthreads,1)
        self.assertGreater(output_data.sysbench_output_params.totaltime,0)
        self.assertGreater(output_data.sysbench_output_params.totalnumberofevents,0)
        self.assertGreater(output_data.sysbench_results.CPUspeed.eventspersecond,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.avg,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.sum,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.events.avg,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.executiontime.avg,0)
        

    def test_functional_memory(self):
        input = sysbench_plugin.SysbenchMemoryInputParams(
            operation="memory",
            threads=2
        )

        output_id, output_data = sysbench_plugin.RunSysbenchMemory(input)

        self.assertEqual("success", output_id)
        self.assertGreaterEqual(output_data.sysbench_output_params.Numberofthreads,1)
        self.assertGreater(output_data.sysbench_output_params.totaltime,0)
        self.assertGreater(output_data.sysbench_output_params.Totaloperations,0)
        self.assertIsNotNone(output_data.sysbench_output_params.blocksize)
        self.assertIsNotNone(output_data.sysbench_output_params.operation)
        self.assertGreater(output_data.sysbench_results.transferred_MiB,0)
        self.assertGreater(output_data.sysbench_results.transferred_MiBpersec,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.avg,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.sum,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.events.avg,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.executiontime.avg,0)

    def test_parsing_function_memory(self):
        sysbench_output = {'Numberofthreads': 2.0, 'blocksize': '1KiB', 'totalsize': '102400MiB', 'operation': 'write', 'scope': 'global', 'Totaloperations': 70040643.0, 'Totaloperationspersecond': 7003215.47, 'totaltime': 10.0001, 'totalnumberofevents': 70040643.0}
        sysbench_results = {'transferred_MiB': 68399.07, 'transferred_MiBpersec': 6839.08, 'Latency': {'min': '0.00', 'avg': '0.00', 'max': '0.11', 'P95thpercentile': '0.00', 'sum': '13958.52'}, 'Threadsfairness': {'events': {'avg': 35020321.5, 'stddev': 955973.5}, 'executiontime': {'avg': 6.9793, 'stddev': 0.07}}}
        with open('tests/memory_parse_output.txt', 'r') as fout:
            mem_output = fout.read()

        output,results = sysbench_plugin.parse_output(mem_output)
        self.assertEqual(sysbench_output,output)
        self.assertEqual(sysbench_results,results)

    def test_parsing_function_cpu(self):
        sysbench_output= {'Numberofthreads': 2.0, 'Primenumberslimit': 10000.0, 'totaltime': 10.0005, 'totalnumberofevents': 29281.0}
        sysbench_results= {'CPUspeed': {'eventspersecond': '2927.61'}, 'Latency': {'min': '0.67', 'avg': '0.68', 'max': '1.56', 'P95thpercentile': '0.70', 'sum': '19995.74'}, 'Threadsfairness': {'events': {'avg': 14640.5, 'stddev': 1.5}, 'executiontime': {'avg': 9.9979, 'stddev': 0.0}}}

        with open('tests/cpu_parse_output.txt', 'r') as fout:
            cpu_output = fout.read()

        output,results = sysbench_plugin.parse_output(cpu_output)
        self.assertEqual(sysbench_output,output)
        self.assertEqual(sysbench_results,results)


if __name__ == '__main__':
    unittest.main()
