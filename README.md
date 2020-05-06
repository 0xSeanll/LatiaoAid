# LatiaoAid 1.3

![Github Action Badge](https://github.com/0xSeanll/LatiaoAid/workflows/LatiaoAid/badge.svg)

## Introduction

This python script collects 辣条/亲密度 on live.bilibili.com using selenium webdriver.

*Issues are warmly welcomed. Feel free to raise one if you found a bug, or have a great idea, or anything.*

Example log:

>[2020-04-27 17:15:56.729825] 【一个小奶瓶儿】白嫖启动 (゜-゜)つロ 
>
>[2020-04-27 17:15:57.473284] 【一个小奶瓶儿】恭喜奶瓶家的清雪yu上任舰长 亲密度到手 (゜-゜)つロ 
>
>[2020-04-27 17:16:01.881398] 【一个小奶瓶儿】等 107 秒再来 (゜-゜)つロ 
>
>[2020-04-27 17:17:53.138381] 【一个小奶瓶儿】感谢女神小奶瓶 赠送的小电视飞船 辣条到手 (゜-゜)つロ 
>
>[2020-04-27 17:17:57.562686] 【一个小奶瓶儿】没辣条了 (゜-゜)つロ 
>
>[2020-04-27 17:18:02.972501] 【creamOUO】白嫖启动 (゜-゜)つロ 
>
>[2020-04-27 17:18:03.573169] 【creamOUO】感谢没错我就是FG 赠送的小电视飞船 辣条到手 (゜-゜)つロ 
>
>[2020-04-27 17:18:06.999048] 【creamOUO】没辣条了 (゜-゜)つロ 
>
>[2020-04-27 17:19:16.961655] 【玖绫Aya】白嫖启动 (゜-゜)つロ 
>
>[2020-04-27 17:19:17.582990] 【玖绫Aya】等 109 秒再来 (゜-゜)つロ 
>
>[2020-04-27 17:21:10.759032] 【玖绫Aya】感谢亚总の文件尼 赠送的小电视飞船 辣条到手 (゜-゜)つロ 

## Release Note

### Version 1.3

Various performance and stability improvements.

Add support for headless mode (need pillow to show login qrcode).

### Version 1.2

An ugly, yet stable release. 99.9% exceptions are handled, enabling it to be deployed on a server.

## Dependencies

- Python 3.7
- Firefox browser
- Pillow==7.1.2
- selenium==3.141.0
- urllib3==1.25.9

```shell script
pip install -r requirements.txt
```

You may want to use virtual environment.

```shell script
$ virtualenv LatiaoAidVenv --python=python3.7
$ cd LatiaoAidVenv
$ source bin/activate
$ git clone git@github.com:0xSeanll/LatiaoAid.git
$ cd LatiaoAid
$ pip install -r requirements.txt
$ python3 run.py
```

## Usage

You need browsers that support selenium. See [documentations of selenium](https://selenium-python.readthedocs.io/installation.html#drivers) for more details. The default browser used in this project is Firefox. You can use other browsers, but you need to modify `class LatiaoAid`.
 
Before running, check the parameters in `run.py`.

This is a Pycharm project, so you can run it in Pycharm directly. Or to run with python3, run `python3 run.py`.

You will need login to bilibili.com manually (the script will bring up the login page or qrcode (in headless mode) for you).

After logged in, the script will work automatically.

**Note**: The website may require *some* users to do human-verification. It is recommended use non-headless mode to test whether the script works properly first.

## Todo

- More sophisticated logic for waiting for and collecting Latiao.
- GUI.
- Support headless.

## Disclaimer

This project is just for fun.

Channel 528 on live.bilibili.com is irrelevant to this project, even though it was chosen to be the base tab.
