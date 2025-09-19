import time
import argparse
import colorama

from .monitor import Monitor

parser = argparse.ArgumentParser(
    prog="pymon",
)

parser.add_argument(
    "command",
    type=str,
    help="the file to be executed or command to run with pymon",
    metavar="command",
)

parser.add_argument(
    "-w",
    "--watch",
    type=str,
    help="paths/patterns to watch (e.g., 'src/*.py', 'data/**/*.json'). use once for each path/pattern. default is '*.py'",
    action="append",
    default=["*.py"],
    metavar="path_pattern",
)

parser.add_argument(
    "-d",
    "--debug",
    help="logs detected file changes to the terminal",
    action="store_true",
)

parser.add_argument(
    "-c",
    "--clean",
    help="runs pymon in clean mode (no logs, no commands)",
    action="store_true",
)

parser.add_argument(
    "-i",
    "--ignore",
    type=str,
    help="patterns of files/paths to ignore. use once for each pattern.",
    action="append",
    default=[],
    metavar="patterns",
)

parser.add_argument(
    "-x",
    "--exec",
    help="execute a shell command instead of running a Python file",
    action="store_true",
    default=False,
)


def main():
    colorama.init()
    arguments = parser.parse_args()

    monitor = Monitor(arguments)
    monitor.start()

    try:
        while True:
            if not arguments.clean:
                cmd = input()
                if cmd == "rs":
                    monitor.restart_process()
                elif cmd == "stop":
                    monitor.stop()
                    break
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()

    return


if __name__ == "__main__":
    main()
