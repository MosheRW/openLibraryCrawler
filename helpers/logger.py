printInfo = True
printError = True


def print_info(message):
    if printInfo:
        print(f"\033[94m[INFO]\033[0m {message}")


def print_error(message):
    if printError:
        print(f"\033[91m[ERROR]\033[0m {message}")
