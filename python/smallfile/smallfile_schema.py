#!/usr/bin/env python3

import enum
import typing
from dataclasses import dataclass
from dataclasses import field
from arcaflow_plugin_sdk import plugin
from arcaflow_plugin_sdk import schema


class Operations(enum.Enum):
    """
    These are the supported operation types for smallfile
    """
    CREATE = 'create'
    APPEND = 'append'
    DELETE = 'delete'
    RENAME = 'rename'
    DELETE_RENAMED = 'delete_renamed'
    READ = 'read'
    STAT = 'stat'
    CHMOD = 'chmod'
    SETXATTR = 'setxattr'
    GETXATTR = 'getxattr'
    SYMLINK = 'symlink'
    MKDIR = 'mkdir'
    RMDIR = 'rmdir'
    READDIR = 'readdir'
    LS_L = 'ls-l'
    CLEANUP = 'cleanup'
    SWIFT_PUT = 'swift-put'
    SWIFT_GET = 'swift-get'
    OVERWRITE = 'overwrite'
    TRUNCATE_OVERWRITE = 'truncate-overwrite'


class YesNo(enum.Enum):
    """
    smallfile expects its boolean inputs in string Y or N format
    """
    YES = 'Y'
    NO = 'N'


@dataclass
class SmallfileParams:
    """
    The parameters in this schema will be passed through to the smallfile_cli.py command unchanged.
    These are documented with the smallfile project at https://github.com/distributed-system-analysis/smallfile#how-to-specify-test
    """
    top: str = field(metadata={
        "name": "Top directory",
        "description": "Directory where file operations are performed"
    })
    operation: Operations = field(metadata={
        "name": "Operation",
        "description": "Type of smallfile operation"
    })
    file_size: typing.Optional[int] = field(default=None, metadata={
        "id": "file-size",
        "name": "File size (B)",
        "description": "Size in bytes of files"
    })
    threads: typing.Optional[int] = field(default=None, metadata={
        "name": "Threads",
        "description": "Number of workload threads"
    })
    files: typing.Optional[int] = field(default=None, metadata={
        "name": "File count",
        "description": "Number of files per thread"
    })
    auto_pause: typing.Optional[YesNo] = field(default=None, metadata={
        "id": "auto-pause",
        "name": "Auto pause",
        "description": "Auto-adjust the pause time between files"
    })
    fsync: typing.Optional[YesNo] = field(default=None, metadata={
        "name": "fsync",
        "description": "Insert fsync() call before closing a file"
    })
    files_per_dir: typing.Optional[int] = field(default=None, metadata={
        "id": "files-per-dir",
        "name": "Files per directory",
        "description": "Maximum number of files per directory"
    })
    dirs_per_dir: typing.Optional[int] = field(default=None, metadata={
        "id": "dirs-per-dir",
        "name": "Directories per directory",
        "description": "Maximum number of subdirectories per directory"
    })
    record_size: typing.Optional[int] = field(default=None, metadata={
        "id": "record-size",
        "name": "Record size (KB)",
        "description": "Size in KB of data transferred in a single system call"
    })
    xattr_size: typing.Optional[int] = field(default=None, metadata={
        "id": "xattr-size",
        "name": "xattr size (B)",
        "description": "Size in bytes of extended attribute value in bytes"
    })
    xattr_count: typing.Optional[int] = field(default=None, metadata={
        "id": "xattr-count",
        "name": "xattr count",
        "description": "Number of extended attributes per file"
    })
    stonewall: typing.Optional[YesNo] = field(default=None, metadata={
        "name": "Stonewall",
        "description": "Measure thread throughput when another thread has finished"
    })
    finish: typing.Optional[YesNo] = field(default=None, metadata={
        "name": "Finish operations",
        "description": "Complete all file operations even if measurement has finished"
    })
    prefix: typing.Optional[str] = field(default=None, metadata={
        "name": "File prefix",
        "description": "Filename prefix"
    })
    suffix: typing.Optional[str] = field(default=None, metadata={
        "name": "File suffix",
        "description": "Filename suffix"
    })
    hash_into_dirs: typing.Optional[YesNo] = field(default=None, metadata={
        "id": "hash-into-dirs",
        "name": "Hash into directories",
        "description": "Assign next file to a directory using a hash function"
    })
    same_dir: typing.Optional[YesNo] = field(default=None, metadata={
        "id": "same-dir",
        "name": "Same directory",
        "description": "Threads share a single directory"
    })
    verify_read: typing.Optional[YesNo] = field(default=None, metadata={
        "id": "verify-read",
        "name": "Verify read",
        "description": "Verify read data is correct"
    })
    incompressible: typing.Optional[YesNo] = field(default=None, metadata={
        "name": "Incompressible files",
        "description": "Generate pure-random files that are not compressible"
    })
    cleanup_delay_usec_per_file: typing.Optional[int] = field(default=None, metadata={
        "id": "cleanup-delay-usec-per-file",
        "name": "Cleanup delay (usec)",
        "description": "Delay in usec after cleanup operation"
    })


smallfile_schema = plugin.build_object_schema(SmallfileParams)


@dataclass
class WorkloadParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    smallfile_params: SmallfileParams
    cleanup: typing.Optional[bool] = field(default=True, metadata={
        "name": "Cleanup files",
        "description": "Whether to cleanup files and directories after a run"
    })


@dataclass
class SmallfileOutputParams:
    """
    smallfile echos its test parameters back in the output, but with some different formats.
    We'll keep these for indexing consistency.
    """
    host_set: str = field(metadata={
        "name": "Host set",
        "description": "Always 'localhost' because we don't use smallfile's multi-host features"
    })
    launch_by_daemon: bool = field(metadata={
        "name": "Launch by daemon",
        "description": "Always 'false' because we don't use smallfile's daemon feature"
    })
    version: str = field(metadata={
        "name": "Version",
        "description": "Smallfile version"
    })
    top: str = field(metadata={
        "name": "Top directory",
        "description": "Directory where file operations are performed"
    })
    operation: Operations = field(metadata={
        "name": "Operation",
        "description": "Type of smallfile operation"
    })
    files_per_thread: int = field(metadata={
        "name": "File count",
        "description": "Number of files per thread"
    })
    threads: int = field(metadata={
        "name": "Threads",
        "description": "Number of workload threads"
    })
    file_size: int = field(metadata={
        "name": "File size (B)",
        "description": "Size in bytes of files"
    })
    file_size_distr: int = field(metadata={
        "name": "File size distribution",
        "description": "Always '-1' as unsupported feature"
    })
    files_per_dir: int = field(metadata={
        "name": "Files per directory",
        "description": "Maximum number of files per directory"
    })
    share_dir: YesNo = field(metadata={
        "name": "Same directory",
        "description": "Threads share a single directory"
    })
    hash_to_dir: YesNo = field(metadata={
        "name": "Hash into directories",
        "description": "Assign next file to a directory using a hash function"
    })
    fsync_after_modify: YesNo = field(metadata={
        "name": "fsync",
        "description": "Insert fsync() call before closing a file"
    })
    pause_between_files: float = field(metadata={
        "name": "Pause between files",
        "description": "Always '0.0' as unsupported feature"
    })
    auto_pause: bool = field(metadata={
        "name": "Auto pause",
        "description": "Auto-adjust the pause time between files"
    })
    cleanup_delay_usec_per_file: int = field(metadata={
        "name": "Cleanup delay (usec)",
        "description": "Delay in usec after cleanup operation"
    })
    finish_all_requests: YesNo = field(metadata={
        "name": "Finish operations",
        "description": "Complete all file operations even if measurement has finished"
    })
    stonewall: YesNo = field(metadata={
        "name": "Stonewall",
        "description": "Measure thread throughput when another thread has finished"
    })
    verify_read: YesNo = field(metadata={
        "name": "Verify read",
        "description": "Verify read data is correct"
    })
    xattr_size: int = field(metadata={
        "name": "xattr size (B)",
        "description": "Size in bytes of extended attribute value in bytes"
    })
    xattr_count: int = field(metadata={
        "name": "xattr count",
        "description": "Number of extended attributes per file"
    })
    permute_host_dirs: YesNo = field(metadata={
        "name": "Permute host directories",
        "description": "Always 'N' as unsupported feature"
    })
    network_sync_dir: str = field(metadata={
        "name": "Network sync directory",
        "description": "Subdirectory of top for network sync"
    })
    min_directories_per_sec: int = field(metadata={
        "name": "Minimum directories per second",
        "description": "Always '50' as unsupported feature"
    })
    total_hosts: int = field(metadata={
        "name": "Total hosts",
        "description": "Total number of hosts in the test"
    })
    startup_timeout: int = field(metadata={
        "name": "Startup timeout",
        "description": "Always '3' as unsupported feature"
    })
    host_timeout: int = field(metadata={
        "name": "Host timeout",
        "description": "Always '3' as unsupported feature"
    })
    fname_prefix: typing.Optional[str] = field(default=None, metadata={
        "name": "File prefix",
        "description": "Filename prefix"
    })
    fname_suffix: typing.Optional[str] = field(default=None, metadata={
        "name": "File suffix",
        "description": "Filename suffix"
    })


output_params_schema = plugin.build_object_schema(SmallfileOutputParams)


@dataclass
class SmallfileOutputThread:
    """
    A data structure for each thread is in the primary command output.
    """
    elapsed: float = field(metadata={
        "name": "Thread elapsed time",
        "description": "Elapsed time of the thread"
    })
    files: int = field(metadata={
        "name": "Thread files",
        "description": "Total files for the thread"
    })
    records: int = field(metadata={
        "name": "Thread records",
        "description": "Total records for the thread"
    })
    filesPerSec: float = field(metadata={
        "name": "Thread files per second",
        "description": "Files per second rate for the thread"
    })
    IOPS: float = field(metadata={
        "name": "Thread IOPS",
        "description": "IOPS rate for the thread"
    })
    MiBps: float = field(metadata={
        "name": "Thread MiBps",
        "description": "MiBps rate for the thread"
    })


@dataclass
class SmallfileOutputResults:
    """
    This the complete results structure, inclusive of the list of thread structures. 
    """
    elapsed: float = field(metadata={
        "name": "Elapsed time",
        "description": "Elapsed time of the job"
    })
    files: int = field(metadata={
        "name": "Total files",
        "description": "Total files for the job"
    })
    records: int = field(metadata={
        "name": "Total records",
        "description": "Total records for the job"
    })
    filesPerSec: float = field(metadata={
        "name": "Total files per second",
        "description": "Files per second rate for the job"
    })
    IOPS: float = field(metadata={
        "name": "Total IOPS",
        "description": "IOPS rate for the job"
    })
    MiBps: float = field(metadata={
        "name": "Total MiBps",
        "description": "MiBps rate for the job"
    })
    totalhreads: int = field(metadata={
        "name": "Total threads",
        "description": "Total number of threads"
    })
    totalDataGB: float = field(metadata={
        "name": "Total Data (GB)",
        "description": "Total data in GB"
    })
    pctFilesDone: float = field(metadata={
        "name": "Percent files done",
        "description": "Total percent of file transactions completed"
    })
    startTime: float = field(metadata={
        "name": "Start time",
        "description": "Test start time"
    })
    status: str = field(metadata={
        "name": "Status",
        "description": "Test run status"
    })
    #date: datetime
    # FIXME: Enable datetime data type
    # https://github.com/arcalot/arcaflow-plugin-sdk-python/issues/3
    date: str = field(metadata={
        "name": "Date",
        "description": "Test run date"
    })
    thread: typing.Dict[int, SmallfileOutputThread]


output_results_schema = plugin.build_object_schema(SmallfileOutputResults)


@dataclass
class SmallfileOutputRsptimes:
    """
    We get response times as part of a post-processing step.
    """
    host_thread: str = field(metadata={
        "name": "Host thread",
        "description": "Job ID and thread identifier"
    })
    samples: int = field(metadata={
        "name": "Samples",
        "description": "Number of file samples"
    })
    min: float = field(metadata={
        "name": "Minimum",
        "description": "Minimum response time"
    })
    max: float = field(metadata={
        "name": "Maximum",
        "description": "Maximum response time"
    })
    mean: float = field(metadata={
        "name": "Mean",
        "description": "Mean response time"
    })
    pctdev: float = field(metadata={
        "name": "Percent deviation",
        "description": "Standard deviation as a percent of mean"
    })
    pctile50: float = field(metadata={
        "name": "50th percentile",
        "description": "50th percentile response time"
    })
    pctile90: float = field(metadata={
        "name": "90th percentile",
        "description": "90th percentile response time"
    })
    pctile95: float = field(metadata={
        "name": "95th percentile",
        "description": "95th percentile response time"
    })
    pctile99: float = field(metadata={
        "name": "99th percentile",
        "description": "99th percentile response time"
    })


output_rsptimes_schema = schema.ListType(
    plugin.build_object_schema(SmallfileOutputRsptimes)
)


@dataclass
class WorkloadResults:
    """
    This is the final output data structure for the success case.
    """
    sf_params: SmallfileOutputParams
    sf_results: SmallfileOutputResults
    sf_rsptimes: typing.List[SmallfileOutputRsptimes]


@dataclass
class WorkloadError:
    """
    This is the output data structure in the error case.
    """
    error: str
