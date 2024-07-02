#  (C) 2024 GoodData Corporation
import enum
import os
import platform
import socket
from dataclasses import dataclass
from typing import Any, Optional

from dynaconf import Dynaconf, ValidationError, Validator

_SERVER_SECTION_NAME = "server"


class OtelExporterType(enum.Enum):
    """
    Supported OpenTelemetry exporter types.
    """

    Zipkin = "zipkin"
    OtlpHttp = "otlp-http"
    OtlpGrpc = "otlp-grpc"
    Console = "console"


@dataclass(frozen=True, slots=True)
class OtelConfig:
    exporter_type: Optional[OtelExporterType]
    service_name: str
    service_namespace: Optional[str]
    service_instance_id: Optional[str]


@dataclass(frozen=True, slots=True)
class ServerConfig:
    listen_host: str
    listen_port: int
    advertise_host: str
    advertise_port: int

    task_threads: int

    metrics_host: Optional[str]
    metrics_port: int

    health_check_host: Optional[str]
    health_check_port: int

    malloc_trim_interval_sec: int
    log_event_key_name: str
    log_trace_keys: dict[str, str]

    otel_config: OtelConfig

    # TODO: implement config for these; for now defaulting to 'off' state
    use_tls: bool = False
    use_mutual_tls: bool = False
    tls_cert_and_key: Optional[tuple[bytes, bytes]] = None
    tls_root: Optional[bytes] = None


class _Settings:
    ListenHost = "listen_host"
    ListenPort = "listen_port"
    AdvertiseHost = "advertise_host"
    AdvertisePort = "advertise_port"
    TaskThreads = "task_threads"
    MetricsHost = "metrics_host"
    MetricsPort = "metrics_port"
    HealthcheckHost = "health_check_host"
    HealthcheckPort = "health_check_port"
    MallocTrimIntervalSec = "malloc_trim_interval_sec"
    LogEventKeyName = "log_event_key_name"
    LogTraceKeys = "log_trace_keys"
    OtelExporterType = "otel_exporter_type"
    OtelServiceName = "otel_service_name"
    OtelServiceNamespace = "otel_service_namespace"
    OtelServiceInstanceId = "otel_service_instance_id"


_LOCALHOST = "127.0.0.1"
_DEFAULT_ADVERTISE_HOST = socket.gethostbyaddr("127.0.0.1")[0] if platform.system() == "Darwin" else socket.getfqdn()
_DEFAULT_LISTEN_PORT = 17001
_DEFAULT_TASK_THREADS = 32
_DEFAULT_MALLOC_TRIM_INTERVAL_SEC = 30
_DEFAULT_METRICS_PORT = 17101
_DEFAULT_HEALTHCHECK_PORT = 8877
_DEFAULT_LOG_EVENT_KEY_NAME = "event"
_SUPPORTED_EXPORTERS = [
    "none",
    OtelExporterType.Zipkin.value,
    OtelExporterType.OtlpHttp.value,
    OtelExporterType.OtlpGrpc.value,
    OtelExporterType.Console.value,
]


def _s(name: str) -> str:
    return f"{_SERVER_SECTION_NAME}.{name}"


def _validate_non_empty_string(val: Any) -> bool:
    return isinstance(val, str) and len(val) > 0


def _validate_non_negative_number(val: Any) -> bool:
    try:
        return int(val) > 0
    except ValueError:
        return False


def _validate_supporter_exporter(val: Any) -> bool:
    return val in _SUPPORTED_EXPORTERS


def _validate_mapping(val: Any) -> bool:
    return isinstance(val, dict)


_VALIDATORS = [
    Validator(
        _s(_Settings.ListenHost),
        default=_LOCALHOST,
        condition=_validate_non_empty_string,
        cast=str,
        messages={
            "condition": f"{_Settings.ListenHost} must be an IP address or hostname.",
        },
    ),
    Validator(
        _s(_Settings.ListenPort),
        default=_DEFAULT_LISTEN_PORT,
        condition=_validate_non_negative_number,
        cast=int,
        messages={
            "condition": f"{_Settings.ListenPort} must be a valid port number.",
        },
    ),
    Validator(
        _s(_Settings.AdvertiseHost),
        default=_DEFAULT_ADVERTISE_HOST,
        condition=_validate_non_empty_string,
        cast=str,
        messages={
            "condition": f"{_Settings.AdvertiseHost} must be an IP address or hostname.",
        },
    ),
    Validator(
        _s(_Settings.AdvertisePort),
        condition=_validate_non_negative_number,
        cast=int,
        messages={
            "condition": f"{_Settings.AdvertisePort} must be a valid port number.",
        },
    ),
    Validator(
        _s(_Settings.TaskThreads),
        default=_DEFAULT_TASK_THREADS,
        condition=_validate_non_negative_number,
        cast=int,
        messages={
            "condition": f"{_Settings.TaskThreads} must be a positive number.",
        },
    ),
    Validator(
        _s(_Settings.MetricsHost),
        condition=_validate_non_empty_string,
        cast=str,
        messages={
            "condition": f"{_Settings.MetricsHost} must be an IP address or hostname.",
        },
    ),
    Validator(
        _s(_Settings.MetricsPort),
        default=_DEFAULT_METRICS_PORT,
        condition=_validate_non_negative_number,
        cast=int,
        messages={
            "condition": f"{_Settings.MetricsHost} must be a valid port number.",
        },
    ),
    Validator(
        _s(_Settings.HealthcheckHost),
        condition=_validate_non_empty_string,
        cast=str,
        messages={
            "condition": f"{_Settings.HealthcheckHost} must be an IP address or hostname.",
        },
    ),
    Validator(
        _s(_Settings.HealthcheckPort),
        default=_DEFAULT_HEALTHCHECK_PORT,
        condition=_validate_non_negative_number,
        cast=int,
        messages={
            "condition": f"{_Settings.HealthcheckPort} must be a valid port number.",
        },
    ),
    Validator(
        _s(_Settings.MallocTrimIntervalSec),
        default=_DEFAULT_MALLOC_TRIM_INTERVAL_SEC,
        condition=_validate_non_negative_number,
        messages={
            "condition": f"{_Settings.MallocTrimIntervalSec} must be a positive number.",
        },
    ),
    Validator(
        _s(_Settings.LogEventKeyName),
        default=_DEFAULT_LOG_EVENT_KEY_NAME,
        condition=_validate_non_empty_string,
        messages={
            "condition": f"{_Settings.LogEventKeyName} must be a non-empty string.",
        },
    ),
    Validator(
        _s(_Settings.LogTraceKeys),
        condition=_validate_mapping,
        messages={
            "condition": f"{_Settings.LogTraceKeys} must be a mapping between 'trace_id', 'span_id' "
            f"and 'parent_span_id' -> keys that should appear in structured log messages.",
        },
    ),
    Validator(
        _s(_Settings.OtelExporterType),
        cast=str,
        condition=_validate_supporter_exporter,
        messages={
            "condition": f"{_Settings.OtelExporterType} must be one of {', '.join(_SUPPORTED_EXPORTERS)}.",
        },
    ),
    Validator(
        _s(_Settings.OtelServiceName),
        cast=str,
        condition=_validate_non_empty_string,
        messages={
            "condition": f"{_Settings.OtelServiceName} must be a non-empty string.",
        },
    ),
    Validator(
        _s(_Settings.OtelServiceNamespace),
        cast=str,
        condition=_validate_non_empty_string,
        messages={
            "condition": f"{_Settings.OtelServiceNamespace} must be a non-empty string.",
        },
    ),
    Validator(
        _s(_Settings.OtelServiceInstanceId),
        cast=str,
        condition=_validate_non_empty_string,
        messages={
            "condition": f"{_Settings.OtelServiceInstanceId} must be a non-empty string.",
        },
    ),
]


def _create_server_config(settings: Dynaconf) -> ServerConfig:
    server_settings = settings.get(_SERVER_SECTION_NAME)

    exporter_type = server_settings.get(_Settings.OtelExporterType)
    if exporter_type == "none":
        exporter_type = None

    # advertise port defaults to value of listen port
    advertise_port = server_settings.get(_Settings.AdvertisePort) or server_settings.get(_Settings.ListenPort)

    return ServerConfig(
        listen_host=server_settings.get(_Settings.ListenHost),
        listen_port=server_settings.get(_Settings.ListenPort),
        advertise_host=server_settings.get(_Settings.AdvertiseHost),
        advertise_port=advertise_port,
        task_threads=server_settings.get(_Settings.TaskThreads),
        metrics_host=server_settings.get(_Settings.MetricsHost),
        metrics_port=server_settings.get(_Settings.MetricsPort),
        health_check_host=server_settings.get(_Settings.HealthcheckHost),
        health_check_port=server_settings.get(_Settings.HealthcheckPort),
        malloc_trim_interval_sec=server_settings.get(_Settings.MallocTrimIntervalSec),
        log_event_key_name=server_settings.get(_Settings.LogEventKeyName),
        log_trace_keys=dict(server_settings.get(_Settings.LogTraceKeys) or {}),
        otel_config=OtelConfig(
            exporter_type=OtelExporterType(exporter_type) if exporter_type is not None else None,
            service_name=server_settings.get(_Settings.OtelServiceName),
            service_namespace=server_settings.get(_Settings.OtelServiceNamespace),
            service_instance_id=server_settings.get(_Settings.OtelServiceInstanceId),
        ),
    )


def _load_dynaconf(files: tuple[str, ...] = ()) -> Dynaconf:
    """
    Initializes Dynaconf instance, optionally using a set of configuration files. Dynaconf will read config
    from env variables with the `GDFS_` prefix. See: https://www.dynaconf.com/ to learn more.

    :param files: configuration files to read
    :returns
    """
    for file in files:
        if not os.path.exists(file):
            raise ValidationError(f"Settings file {file} does not exist.")
        elif not os.path.isfile(file):
            raise ValidationError(f"Path {file} is a directory and not a settings file.")

    return Dynaconf(settings_files=files, envvar_prefix="GOODDATA_FLIGHT", environments=False)


def read_config(files: tuple[str, ...]) -> tuple[Dynaconf, ServerConfig]:
    settings = _load_dynaconf(files)
    settings.validators.register(*_VALIDATORS)
    settings.validators.validate()

    return settings, _create_server_config(settings)
