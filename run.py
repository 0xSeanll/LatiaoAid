from LatiaoAid import LatiaoAid
from Logger import Logger

LatiaoAid(
    geckodriver_path='/usr/local/bin/geckodriver',
    headless=True,
    disable_image=True,
    logger=Logger(
        print_to_console=False,
        log_path='./log.txt'
    )
).main()
