from .configs import Config
config = Config()


def print_info(message):
    if config.settings.print_info:
        print(f"\033[94m[INFO]\033[0m {message}")


def print_error(message):
    if config.settings.print_errors:
        print(f"\033[91m[ERROR]\033[0m {message}")
