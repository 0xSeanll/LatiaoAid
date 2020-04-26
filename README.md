# Latiao Aid Version 1.0

## Introduction

This project serves the purpose of automatic collecting 辣条 or 主播亲密度 on live.bilibili.com using selenium. This is the very first version, so the functions are fairly trivial and little attentions are paid to the design.

## Dependency

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

- Multi-tab processing.
- A friendly GUI.
- A logger.
- A better design.

## Disclaimer

This project is just for fun.

Channel 528 on live.bilibili.com is irrelevant to this project, even though it was chosen to be the base tab.