from datetime import datetime


class Logger:
    caster = None

    @staticmethod
    def log(s):
        with open('log.txt', 'a', encoding='utf-8') as f:
            line = f'[{datetime.now().__str__()}] 【{Logger.caster}】' + s + " (゜-゜)つロ "
            print(line)
            f.write(line + '\n')

    @staticmethod
    def err(pos, msg, exc=None):
        with open('log.txt', 'a', encoding='utf-8') as f:
            line = f'[{datetime.now().__str__()}] 【{pos}】' + msg
            if exc is not None:
                print(exc)
            print(line)
            f.write(line)

    @staticmethod
    def print(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            print(msg)
            f.write(msg + '\n')
