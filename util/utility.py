import os
import configparser
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
profile = os.getenv('PROFILE', 'local')


def get_config_value(key):
    print(f"#### selected profile: {profile} ####")

    # read value from environment variable
    value = os.getenv(key)

    # if the environment variable is not set or is empty, read from config file
    if not value or value == "":
        config = configparser.ConfigParser()
        config.read('config.ini')
        value = config.get(profile, key, fallback=None)

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