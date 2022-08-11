#!/usr/bin/env python3

import re
import unittest
import smallfile_schema
from arcaflow_plugin_sdk import plugin


class SmallfilePluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            smallfile_schema.smallfile_schema.unserialize(
                {
                    'top': '/var/tmp',
                    'operation': 'ls-l',
                    'threads': 5,
                    'file-size': 64,
                    'files': 100,
                    'auto-pause': 'Y',
                    'fsync': 'N',
                    'files-per-dir': 30,
                    'dirs-per-dir': 10,
                    'record-size': 99,
                    'xattr-size': 3,
                    'xattr-count': 20,
                    'stonewall': 'Y',
                    'finish': 'Y',
                    'prefix': 'foo',
                    'suffix': 'bar',
                    'hash-into-dirs': 'N',
                    'same-dir': 'N',
                    'verify-read': 'Y',
                    'incompressible': 'N',
                    'cleanup-delay-usec-per-file': 100
                }
            )
        )

        plugin.test_object_serialization(
            smallfile_schema.output_params_schema.unserialize(
                {
                    'host_set': 'localhost',
                    'launch_by_daemon': False,
                    'version': '3.2',
                    'top': '/var/tmp',
                    'operation': 'swift-get',
                    'files_per_thread': 100,
                    'threads': 5,
                    'file_size': 64,
                    'file_size_distr': -1,
                    'files_per_dir': 100,
                    'share_dir': 'N',
                    'fname_prefix': '',
                    'fname_suffix': '',
                    'hash_to_dir': 'N',
                    'fsync_after_modify': 'N',
                    'pause_between_files': 0.0,
                    'auto_pause': False,
                    'cleanup_delay_usec_per_file': 0,
                    'finish_all_requests': 'Y',
                    'stonewall': 'Y',
                    'verify_read': 'Y',
                    'xattr_size': 0,
                    'xattr_count': 0,
                    'permute_host_dirs': 'N',
                    'network_sync_dir': '/var/tmp/network_shared',
                    'min_directories_per_sec': 50,
                    'total_hosts': 1,
                    'startup_timeout': 3,
                    'host_timeout': 3
                }
            )
        )

        plugin.test_object_serialization(
            smallfile_schema.output_results_schema.unserialize(
                {
                    'elapsed': 0.04768657684326172,
                    'files': 492,
                    'records': 492,
                    'filesPerSec': 10865.623614104166,
                    'IOPS': 10865.623614104166,
                    'MiBps': 679.1014758815104,
                    'totalhreads': 5,
                    'totalDataGB': 0.030029296875,
                    'pctFilesDone': 98.4,
                    'startTime': 1660215714.4111445,
                    'status': 'Success',
                    'date': '2022-08-11T11:01:54.000Z',
                    'thread': {
                        '0': {
                            'elapsed': 0.04768657684326172,
                            'files': 98,
                            'records': 98,
                            'filesPerSec': 2055.0856548607085,
                            'IOPS': 2055.0856548607085,
                            'MiBps': 128.44285342879428
                        }
                    }

                }
            )
        )

        plugin.test_object_serialization(
            smallfile_schema.SmallfileOutputRsptimes(
                host_thread='d1bb2508b4ca:all-thrd',
                samples=500,
                min=9.0e-05,
                max=0.00125,
                mean=0.000313,
                pctdev=53.04448,
                pctile50=0.000258,
                pctile90=0.000526,
                pctile95=0.000593,
                pctile99=0.000913
            )
        )

        plugin.test_object_serialization(
            smallfile_schema.WorkloadError(
                error='This is an error'
            )
        )


if __name__ == '__main__':
    unittest.main()
