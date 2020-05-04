from datetime import datetime


class Logger:
    def __init__(self, print_to_console=False, log_path='log.txt'):
        self.caster = None
        self.print_to_console = print_to_console
        self.log_path = log_path

    def log(self, s):
        line = f'[{datetime.now().__str__()}] 【{self.caster}】' + s + " (゜-゜)つロ "
        self.print(line)

    def err(self, pos, msg, exc=None):
        line = f'[{datetime.now().__str__()}] ERROR: in [{pos}]' + msg
        self.print(line)
        if exc is not None:
            self.print(exc)

    def print(self, line):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            print(line, file=f)
            if self.print_to_console:
                print(line)
