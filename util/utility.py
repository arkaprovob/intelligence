import configparser
import logging
import os
import socket
import sys

profile = os.getenv('PROFILE', 'local')

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')


def get_config_value(key):
    logging.debug(f"#### selected profile: {profile} ####")

    # read value from environment variable
    value = os.getenv(key)

    # if the environment variable is not set or is empty, read from config file
    if not value or value == "":
        config = configparser.ConfigParser()
        config.read(config_path)
        value = config.get(profile, key, fallback=None)
        logging.debug(f"DEBUG VAlue {value} for key {key}, on profile {profile}xxx")

        # if the value is an empty string, set it to None and then log a warning
        if value == "":
            value = None
            logging.warning(
                f"No value found for {key} in environment variables or config file.")
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    try:
                        if value.lower() in ['true', 'false']:  # check if value is a boolean
                            value = value.lower() == 'true'
                    except ValueError:
                        pass

    return value


def _check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def _check_services():
    services = {
        "Redis": ("REDIS_HOST", "REDIS_PORT"),
        "Quadrant": ("QDRANT_HOST", "QDRANT_PORT"),
        "PostgreSQL": ("PG_HOST", "PG_PORT"),
        "DocsBot": ("localhost", "8000")
    }

    status = {
        "all_services_running": True,
        "services": {}
    }

    for service, (host_key, port_key) in services.items():
        host = "localhost" if host_key == "localhost" else get_config_value(host_key)
        port = 8000 if port_key == "8000" else get_config_value(port_key)

        service_status = {
            "running": False,
            "host": host,
            "port": port,
            "error": None
        }

        if host is None or port is None:
            service_status["error"] = "Configuration missing"
            logging.warning(f"Configuration missing for {service}. Host: {host}, Port: {port}")
        else:
            try:
                service_status["running"] = _check_port(host, port)
                if not service_status["running"]:
                    status["all_services_running"] = False
            except socket.gaierror:
                service_status["error"] = "Invalid hostname"
                status["all_services_running"] = False
                logging.error(f"Invalid host name for {service}: {host}")

        status["services"][service] = service_status

    return status


# Example usage in an API context:
def get_services_status():
    status = _check_services()
    return status


def configure_logging():
    debug = get_config_value("DEBUGGING")

    if debug:
        log_type = logging.DEBUG
    else:
        log_type = logging.INFO

    log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Add a single stream handler
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_type)
    stream_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().setLevel(log_type)
