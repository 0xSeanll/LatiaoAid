# LatiaoAid Version 1.1

## Introduction

The program enables automatic collecting bonus(辣条) on live.bilibili.com, while you are watching live stream.

Watching live using this program, 全区礼物广播 is listened. Upon receiving, the corresponding live channel is opened in a new tab and the waiting time for the bonus is obtained. If the waiting time is too long, the tab will be closed temporarily and the program will start timing and switch back to the live channel you watched. When it is almost time to claim the prize, the channel will be reopened, and the prize will be collected.

**Note**: The website may require **some** users to do human-verification.

Example log:

>[2020-04-27 17:15:56.729825] 【一个小奶瓶儿】白嫖启动
>
>[2020-04-27 17:15:57.473284] 【一个小奶瓶儿】恭喜奶瓶家的清雪yu上任舰长 亲密度到手
>
>[2020-04-27 17:16:01.881398] 【一个小奶瓶儿】等 107 秒再来
>
>[2020-04-27 17:17:53.138381] 【一个小奶瓶儿】感谢女神小奶瓶 赠送的小电视飞船 辣条到手
>
>[2020-04-27 17:17:57.562686] 【一个小奶瓶儿】没辣条了
>
>[2020-04-27 17:18:02.972501] 【creamOUO】白嫖启动
>
>[2020-04-27 17:18:03.573169] 【creamOUO】感谢没错我就是FG 赠送的小电视飞船 辣条到手
>
>[2020-04-27 17:18:06.999048] 【creamOUO】没辣条了
>
>[2020-04-27 17:19:16.961655] 【玖绫Aya】白嫖启动
>
>[2020-04-27 17:19:17.582990] 【玖绫Aya】等 109 秒再来
>
>[2020-04-27 17:21:10.759032] 【玖绫Aya】感谢亚总の文件尼 赠送的小电视飞船 辣条到手


## Dependency

- Python 3
- Selenium 3

```
pip install -U selenium
```

## Usage

You need browsers that support selenium. See [documentations of selenium](https://selenium-python.readthedocs.io/installation.html#drivers) for more details. Before running, specified the path to your selenium webdriver in `LatiaoAid.py`.

This is a Pycharm project. You can run it in Pycharm directly.

To run with python3, `python3 LatiaoAid.py` is all you need.

You will need login to bilibili.com manually (the script will bring up the login page for you).

After logged in, the script will work automatically. 

## TODO list

- A friendly GUI.
- A better design.

## Disclaimer

This project is just for fun.

Channel 528 on live.bilibili.com is irrelevant to this project, even though it was chosen to be the base tab.
