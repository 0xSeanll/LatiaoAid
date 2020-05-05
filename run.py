# -*- coding: utf-8 -*-

from LatiaoAid import LatiaoAid
from Logger import Logger

LatiaoAid(
    geckodriver_path='/usr/local/bin/geckodriver',
    headless=False,
    disable_image=False,
    logger=Logger(
        print_to_console=True,
        print_to_log=False,
        log_path='./log.txt',
    )
).main()
