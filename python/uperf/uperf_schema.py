import typing
import enum
from dataclasses import dataclass
from arcaflow_plugin_sdk import plugin, annotations

# Utility

@dataclass
class IProtocol(enum.Enum):
    TCP = "tcp"
    UDP = "udp"
    SSL = "ssl"
    SCTP = "sctp"
    VSOCK = "vsock"

# Profile 

@dataclass
class ProfileFlowOpCommon:
    type: str = "error"
    count: typing.Optional[int] = None
    rate: typing.Optional[int] = None # Unit: Default uperf unit

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
    remotehost: str = "127.0.0.1"
    protocol: IProtocol = IProtocol.TCP
    tcp_nodelay: bool = False
    wndsz: typing.Optional[int] = None # Unit: k
    engine: typing.Optional[str] = None # The openssl engine.

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
    size: int = 64 # Unit: k
    rsize: typing.Optional[int] = None # Unit: k
    canfail: bool = False
    non_blocking: bool = False
    poll_timeout: bool = False
    conn: typing.Optional[int] = None # Connection name ID

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        options.append(f"size={self.size}k")
        if self.rsize != None:
            options.append(f"rsize={self.rsize}k")
        if self.canfail:
            options.append("canfail")
        if self.non_blocking:
            options.append("non_blocking")
        if self.poll_timeout:
            options.append("poll_timeout")
        if self.conn != None:
            options.append(f"conn={self.conn}")
        return options

@dataclass
class ProfileFlowOpSendFileCommon(ProfileFlowOpCommon):
    # File
    dir: str = "./files" # Dir that contains files to send
    nfiles: int = 1 # number of files to transffer
    size: typing.Optional[int] = 64 # Unit: k?. Chunk size

    def get_options(self):
        options = ProfileFlowOpCommon.get_options(self)
        options.append(f"dir={self.dir}")
        options.append(f"nfiles={self.nfiles}")
        if self.nfiles == 1 and self.size != None:
            options.append(f"size={self.size}")

        return options

@dataclass
class ConnectFlowOp(ProfileFlowOpConnection):
    type: str = "connect"

@dataclass
class AcceptFlowOp(ProfileFlowOpConnection):
    type: str = "accept"

@dataclass
class DisconnectFlowOp(ProfileFlowOpCommon):
    type: str = "disconnect"

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
    ]
    iterations: typing.Optional[int] = None
    duration: typing.Optional[str] = None # TODO: Switch to the new time unit once it's added
    rate: typing.Optional[int] = None # Unit: Default uperf unit

@dataclass
class ProfileGroup():
    transactions: typing.List[ProfileTransaction]
    nthreads: typing.Optional[int] = None
    nprocs: typing.Optional[int] = None

@dataclass
class Profile():
    name: str
    groups: typing.List[ProfileGroup]

# Params and results

@dataclass
class UPerfServerParams():
    # How long to run the server
    run_duration: int = 60

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
    raw: typing.Dict[int, UPerfRawData] # Timestamp to data

# Input and output

@dataclass
class UPerfError:
    """
    This is the output data structure in the error case.
    """
    error: str
