from curses import meta
import typing
import enum
from dataclasses import dataclass, field
from arcaflow_plugin_sdk import plugin, annotations

type_descriptions = """The flowop name for uperf.\n""" \
                    """- connect: Specifies that a connection needs to be opened.\n""" \
                    """- accept: Specifies that a connection needs to be accepted from the remote a\n""" \
                    """- disconnect: Disconnects from the existing connection.\n""" \
                    """- read: Data read on the client side (from the server).\n""" \
                    """- write: Data written from the client (to the server).\n""" \
                    """- redv: Receiving a message back from the server to the client.\n""" \
                    """- sendto: A message sent from the client to the server.\n""" \
                    """- sendfile: Uses the sendfile(3EXT) function call to transfer a single file.\n""" \
                    """- sendfilev: Transfers a set of files using the sendfilev(3EXT) interface. Multiple files are randomly picked from all transferrable files (see dir below) and tranferred to the server.\n""" \
                    """- NOP: Does no operation.\n""" \
                    """- think: For period of time with the CPU idling or busy."""

# Utility

@dataclass
class ThinkType(enum.Enum):
    IDLE = "idle"
    BUSY = "busy"

@dataclass
class IProtocol(enum.Enum):
    TCP = "tcp"
    UDP = "udp"
    SSL = "ssl"
    SCTP = "sctp"
    VSOCK = "vsock"

# Profile

# Base classes with items used by several flowops

@dataclass
class ProfileFlowOpCommon:
    type: str = field(
        default="error",
        metadata={
            "name": "type",
            "description": type_descriptions
        }
    )
    count: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "count",
            "description": "The number of times this flowop will be executed."
        }
    )
    rate: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "rate",
            "description": """Experimental: This option causes uperf to execute """
            """this flowop at the specified rate for iterations or duration seconds."""
        }
    )# Unit: Default uperf unit

    def get_options(self):
        options = []
        if self.count != None:
            options.append(f"count={self.count}")
        if self.rate != None:
            options.append(f"rate={self.rate}")
        return options

@dataclass
class ProfileFlowOpConnection(ProfileFlowOpCommon):
    # Connection
    remotehost: str = field(
        default="127.0.0.1",
        metadata={
            "name": "remotehost",
            "description": "The remote host that we need to connect or accept connection from"
        }
    )
    protocol: IProtocol = field(
        default=IProtocol.TCP,
        metadata={
            "name": "protocol",
            "description": "The protocol used to connect to the remote host."
        }
    )
    tcp_nodelay: bool = field(
        default=False,
        metadata={
            "name": "tcp_nodelay",
            "description": "Sets the TCP_NODELAY socket option."
        }
    )
    wndsz: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "wndsz",
            "description": """Size of the socket send and receive buffer in kib.\n"""
            """This parameter is used to set SO_SNDBUF, SO_RCVBUF flags using setsocktopt()"""
        }
    )
    engine: typing.Optional[str] = field(
        default=None,
        metadata={
            "name": "engine",
            "description": "The SSL Engine used by OpenSSL"
        }
    )

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        options.append(f"remotehost={self.remotehost}")
        options.append(f"protocol={self.protocol.value}")
        if self.tcp_nodelay:
            options.append("tcp_nodelay")
        if self.wndsz != None:
            options.append(f"wndsz={self.wndsz}k")
        if self.engine != None:
            options.append(f"engine={self.engine}")

        return options

@dataclass
class ProfileFlowOpDataCommon(ProfileFlowOpCommon):
    # Data
    size: int = field(
        default=64,
        metadata={
            "name": "size",
            "description": """Unit: Kib\n"""
            """Amount of data that is either read or written. Uperf supports exchange of:\n"""
            """ - Fixed size messages\n"""
            """ - Asymmetrical size messages\n"""
            """ - Random size messages\n"""
            """For fixed size messages, the client and all servers used a fixed size for """
            """receives and transmits. For asymmetrical sized messages, the slaves use the """
            """size specified by the rszize parameter. The master still uses the size """
            """parameter. For a random sized message, the a uniformly distributed value between """
            """the user specifed min and max is used by the transmitting side, and the """
            """receiving side uses the max as the message size. Example: size=64 for 64k"""
        }
    )

    randsize_max: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "Random size max",
            "description": """For when a random message size is desired, this sets the max random """
            """value, and the size parameter sets the minimum. Unit: kib."""
        }
    )

    rsize: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "receive-size",
            "description": """Receive size in kib.\n"""
            """For use with asymmetrical messages. For more contect, see description for "size" """
        }
    )
    canfail: bool = field(
        default=False,
        metadata={
            "name": "canfail",
            "description": """Indicates that a failure for this flowop will not cause uperf to """
            """abort. This is espcially useful in UDP where a packet drop does not constitue a """
            """fatal error. This can be also be used for example, to test a SYN flood attack """
            """(Threads connect() repeatedly ignoring errors)."""
        }
    )
    non_blocking: bool = field(
        default=False,
        metadata={
            "name": "non_blocking",
            "description": "Use non-blocking IO. The socket/file descriptor is set the NO_BLOCK flag."
        }
    )
    poll_timeout: typing.Optional[str] = field(
        default=None,
        metadata={
            "name": "poll_timeout",
            "description": """If this option is set, the thread will first poll for specified """
            """duration before trying to carry out the operation. A poll timeout is returned """
            """as an error back to uperf."""
        }
    )
    conn: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "connection id",
            "description": """Every open connection is assigned a connection name.\n"""
            """Currently, the name can be any valid integer, however, uperf could take a string in """
            """the future. conn identifies the connection to use with this flowop. This connection """
            """name is thread private."""
        }
    )

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        if self.randsize_max == None:
            options.append(f"size={self.size}k")
        else:
            options.append(f"size=rand({self.size}k, {self.randsize_max}k)")
        if self.rsize != None:
            options.append(f"rsize={self.rsize}k")
        if self.canfail:
            options.append("canfail")
        if self.non_blocking:
            options.append("non_blocking")
        if self.poll_timeout != None:
            options.append(f"poll_timeout={self.poll_timeout}")
        if self.conn != None:
            options.append(f"conn={self.conn}")
        return options

@dataclass
class ProfileFlowOpSendFileCommon(ProfileFlowOpCommon):
    # File
    dir: str = field(
        default="./files",
        metadata={
            "name": "dir",
            "description": """This parameter identifies the directory from which the files will """
            """be transferred. The directory is search recursively to generate a list of all """
            """readable files. Example: dir=/space"""
        }
    )
    nfiles: int = field(
        default=1,
        metadata={
            "name": "",
            "description": """This parameter identifies the number of files that will be """
            """transferred with each call to sendfilev(3EXT). This is used as the 3rd argument """
            """to the sendfilev(3EXT). nfiles is assumed to be 1 for the sendfile flowop """
            """function. Example: nfiles=10"""
        }
    )
    size: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "",
            "description": """This parameter identifies the chunk size for the transfer. """
            """Instead of sending the whole file, uperf will send size sized chunks one at """
            """a time. This is used only if nfiles=1. Unit: Kib"""
        }
    )

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        options.append(f"dir={self.dir}")
        options.append(f"nfiles={self.nfiles}")
        if self.nfiles == 1 and self.size != None:
            options.append(f"size={self.size}")

        return options

# The flowop classes that are used directly

@dataclass
class ConnectFlowOp(ProfileFlowOpConnection):
    type: str = "connect"

@dataclass
class AcceptFlowOp(ProfileFlowOpConnection):
    type: str = "accept"

@dataclass
class DisconnectFlowOp(ProfileFlowOpCommon):
    type: str = "disconnect"
    conn: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "connection id",
            "description": "If you know the connection ID, you can specify which one to disconnect."
        }
    )

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        if self.conn != None:
            options.append(f"conn={self.conn}")

        return options

@dataclass
class ReadFlowOp(ProfileFlowOpDataCommon):
    type: str = "read"

@dataclass
class WriteFlowOp(ProfileFlowOpDataCommon):
    type: str = "write"

@dataclass
class RecvFlowOp(ProfileFlowOpDataCommon):
    type: str = "recv"

@dataclass
class SendtoFlowOp(ProfileFlowOpDataCommon):
    type: str = "sendto"

@dataclass
class SendFileFlowOp(ProfileFlowOpSendFileCommon):
    type: str = "sendfile"

@dataclass
class SendFileVFlowOp(ProfileFlowOpSendFileCommon):
    type: str = "sendfilev"

@dataclass
class NOPFlowOp(ProfileFlowOpCommon):
    type: str = "NOP"

@dataclass
class ThinkFlowOp(ProfileFlowOpCommon):
    type: str = "think"

    think_type: ThinkType = field(
        default=ThinkType.IDLE,
        metadata={
            "name": "Think Type",
            "description": """The type of think type, either idle, which"""
            """sleeps the CPU threads, or busy, which uses CPU time."""
        }
    )
    duration: typing.Optional[str] = None # TODO: Switch to the new time unit once it's added

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        options.append(self.think_type.value)
        if self.duration != None:
            options.append(f"duration={self.duration}")

        return options



@dataclass
class ProfileTransaction():
    flowops: typing.List[
        typing.Annotated[
            typing.Union[
                typing.Annotated[ConnectFlowOp, annotations.discriminator_value("connect")],
                typing.Annotated[AcceptFlowOp, annotations.discriminator_value("accept")],
                typing.Annotated[DisconnectFlowOp, annotations.discriminator_value("disconnect")],
                typing.Annotated[ReadFlowOp, annotations.discriminator_value("read")],
                typing.Annotated[WriteFlowOp, annotations.discriminator_value("write")],
                typing.Annotated[RecvFlowOp, annotations.discriminator_value("recv")],
                typing.Annotated[SendtoFlowOp, annotations.discriminator_value("sendto")],
                typing.Annotated[SendFileFlowOp, annotations.discriminator_value("sendfile")],
                typing.Annotated[SendFileVFlowOp, annotations.discriminator_value("sendfilev")],
                typing.Annotated[NOPFlowOp, annotations.discriminator_value("NOP")],
                typing.Annotated[ThinkFlowOp, annotations.discriminator_value("think")]
            ],
            annotations.discriminator("type")
        ]
    ] = field(
        metadata={
            "name": "flowops",
            "description": type_descriptions
        }
    )
    iterations: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "iterations",
            "description": "The number of times the contents of the transaction will run."
        }
    )
    duration: typing.Optional[str] = field(
        default=None,
        metadata={
            "name": "duration",
            "description": "How long the items in the transaction run."
        }
    ) # TODO: Switch to the new time unit once it's added
    rate: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "rate",
            "description": "For limiting the rate. "
        }
    ) 

@dataclass
class ProfileGroup():
    transactions: typing.List[ProfileTransaction] = field(
        metadata={
            "name": "transactions",
            "description": "A list of transactions in the group"
        }
    )
    nthreads: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "nthreads",
            "description": """The number of threads to run, with each thread running """
            """a clone of the group"""
        }
    )
    nprocs: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "nprocs",
            "description": """The number of processes to run, with each process """
            """running a clone of the group"""
        }
    )

@dataclass
class Profile():
    name: str = field(
        metadata={
            "name": "name",
            "description": """The name you assign to the profile. """
            """Does not change the profile's behavior."""
        }
    )
    groups: typing.List[ProfileGroup] = field(
        metadata={
            "name": "groups",
            "description": "A list of groups in the profile."
        }
    )

# Params and results

@dataclass
class UPerfServerParams():
    run_duration: int = field(
        default=60,
        metadata={
            "name": "run_duration",
            "description": "How long the server should run before terminating."
        }
    )

@dataclass
class UPerfServerError():
    error_code: int
    error: str

@dataclass
class UPerfServerResults():
    pass

@dataclass
class UPerfRawData:
    nr_bytes: int
    nr_ops: int

@dataclass
class UPerfResults:
    """
    This is the output data structure for the success case.
    """
    profile_name: str
    # TODO: Switch to timestamp once supported.
    throughput: typing.Dict[int, UPerfRawData] # Timestamp to data

# Input and output

@dataclass
class UPerfError:
    """
    This is the output data structure in the error case.
    """
    error: str
