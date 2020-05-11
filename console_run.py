import argparse
import os
import signal
import warnings
from datetime import datetime, timedelta

from LatiaoAid import LatiaoAid
from Logger import Logger


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments for the `LatiaoAid` binary.

    :return: Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="python3 console_run.py",
        description="Collects 辣条/亲密度 on live.bilibili.com using selenium webdriver",
    )

    parser.add_argument(
        "-r", "--room", type=int, help="default room", default=22198526,
    )

    # runtime behaviors
    parser.add_argument(
        "--headless", help="do not show the browser", action="store_true",
    )

    parser.add_argument(
        "-d", "--disable-image", help="do not show the images", action="store_true",
    )

    # log settings
    parser.add_argument(
        "--silent", help="do not print log to console", action="store_true",
    )

    parser.add_argument(
        "-l", "--log", help="save log to the log file", action="store_true",
    )

    # arg check
    parser.add_argument(
        "--skip-check", help="skip the arg check", action="store_true",
    )

    # timer
    parser.add_argument(
        "-s", "--second", type=int, help="planned running time in seconds", default=0,
    )
    parser.add_argument(
        "-m", "--minute", type=int, help="planned running time in minutes", default=0,
    )

    # paths
    parser.add_argument(
        "--log-path", type=str, help="path of the log file", default="./log.txt",
    )

    parser.add_argument(
        "--driver-path",
        type=str,
        help="path of the geckodriver. If it's not install, "
             "see https://github.com/mozilla/geckodriver/releases for more information",
        default="/usr/local/bin/geckodriver",
    )

    return parser.parse_args()


def check_args(args: argparse.Namespace):
    """Check whether the arguments is valid.

    :note: Only checks the existence of the file, not its validity
    """
    if not os.path.isfile(args.driver_path):
        raise FileNotFoundError("Unable to find the geckodriver")
    if not os.path.isfile(args.log_path) and args.log:
        warnings.warn(f"Unable to find the log:{args.log_path}, create it now")
        with open(args.log_path, "w") as f:
            f.write("")


def run_LatiaoAid_main(args: argparse.Namespace):
    """
    Run LatiaoAid.main with given args

    :param args: Namespace with parsed arguments.
    :return: None
    """
    return LatiaoAid(
        geckodriver_path=args.driver_path,
        headless=args.headless,
        disable_image=args.disable_image,
        logger=Logger(
            print_to_console=not args.silent,
            print_to_log=args.log,
            log_path=args.log_path,
        ),
    ).main()


def exit_timer(seconds_before_exit: int) -> callable:
    """
    decorator with parameter
    :param seconds_before_exit: If not larger than 0, timer will be cancelled.
                                Otherwise, function will exit after the specified time(in second)
    :return: decorator
    """
    if seconds_before_exit <= 0:
        # do nothing
        def decorator(f):
            return f

    else:
        # set a timer
        def decorator(f):
            def handler(signum, frame):
                print(f"[{datetime.now().__str__()}] 已经到预订的终止时间啦，程序终止 (゜-゜)つロ ")
                exit(0)

            def new_f(*args, **kwargs):
                old = signal.signal(signal.SIGALRM, handler)
                signal.alarm(seconds_before_exit)
                try:
                    f(*args, **kwargs)
                finally:
                    signal.signal(signal.SIGALRM, old)
                    signal.alarm(0)

            print(
                f"[{datetime.now().__str__()}]  "
                f"计时器设置成功，LatiaoAid大概会在"
                f"[{(datetime.now() + timedelta(seconds=seconds_before_exit)).__str__()}]终止 (゜-゜)つロ "
            )
            return new_f

    return decorator


if __name__ == "__main__":

    # parse the input args
    args = parse_args()

    # check the args unless skip it
    if not args.skip_check:
        check_args(args)

    # set the base_tab_link
    LatiaoAid.base_tab_link = f"https://live.bilibili.com/{args.room}"

    # run the LatiaoAid.main with timer(if it's specified)
    exit_timer(args.second + args.minute * 60)(run_LatiaoAid_main)(args)
