# -*- coding: utf-8 -*-

import sys
import traceback
from PIL import Image
from datetime import datetime, timedelta
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

from Logger import Logger


class LatiaoAid:
    base_url = "https://passport.bilibili.com/login"
    base_tab_link = "https://live.bilibili.com/22198526"

    def __init__(
            self,
            seconds_before_exit=-1,
            headless=False,
            disable_image=False,
            geckodriver_path="",
            logger=None,
    ):
        self.logger = Logger() if logger is None else logger
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        profile = webdriver.FirefoxProfile()
        if disable_image:
            profile.set_preference("permissions.default.image", 2)
        self.driver = webdriver.Firefox(
            executable_path=geckodriver_path, firefox_profile=profile, options=options
        )
        self.logger.log("Firefox Launched")
        self.base_tab = None  # The tab used to collect broadcast info. YJZ_CHANNEL
        self.loot_tab = None  # The tab where the code collect 辣条
        self.qrcode = None  # The login qrcode
        self._del_time = None  # The time when main process destory
        self.timer = seconds_before_exit

    @property
    def timer(self):
        if self._del_time is not None and self._del_time < datetime.now():
            print(f"[{datetime.now().__str__()}] 已经到预订的终止时间啦，程序终止 (゜-゜)つロ ")
            sys.exit(0)
        return True

    @timer.setter
    def timer(self, seconds_before_exit):
        if seconds_before_exit > 0:
            self._del_time = datetime.now() + timedelta(seconds=seconds_before_exit)
            print(
                f"[{datetime.now().__str__()}]  "
                f"计时器设置成功，LatiaoAid大概会在"
                f"[{(datetime.now() + timedelta(seconds=seconds_before_exit)).__str__()}]终止 (゜-゜)つロ "
            )

    def close_go_back(self):
        """
        Close loot tab and go back to base tab.
        :return:
        """
        self.driver.execute_script("window.close()")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
        self.driver.switch_to.window(self.base_tab)

    def delete_element(self, element):
        """
        Delete an specific element of the page
        :param element: the WebElement to be deleted
        :return:
        """
        self.driver.execute_script(
            """
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """,
            element,
        )

    def load_base_tab(self):
        """
        Load base tab, and wait for chat-history-panel(弹幕窗口) to show up. Update self.base_tab
        :return:
        """
        self.logger.log("开始加载 Base Tab")
        self.driver.get(LatiaoAid.base_tab_link)
        while self.timer:
            try:
                # Delete JS player
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located(
                        (By.XPATH, '//div[@class="bilibili-live-player relative"]')
                    )
                )
                self.delete_element(element)
                self.logger.log("播放器被成功干掉了～")
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located(
                        (By.XPATH, '//div[@id="chat-draw-area-vm"]')
                    )
                )
                self.delete_element(element)
                self.logger.log("弹窗被成功干掉了～")
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[@data-upgrade-intro="Follow"]//div[@class="side-bar-btn-cntr"]',
                        )
                    )
                )
                element.click()
                self.logger.log("成功收回了关注窗口～")
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located(
                        (By.XPATH, '//div[@class="chat-history-panel"]')
                    )
                )
                self.logger.log("Base Tab 加载成功～")
            except TimeoutError:
                self.logger.err("login()", "Failed to load channel 528")
                self.driver.get(LatiaoAid.base_tab_link)
                continue
            else:
                break
        self.base_tab = self.driver.current_window_handle

    def login(self):
        """
        Bring up login page and wait for a human to login.
        :return:
        """
        self.driver.get(LatiaoAid.base_url)
        qrcode = self.driver.find_element_by_xpath(
            '//div[@class="qrcode-login"]'
        ).screenshot_as_png
        with open("qrcode.png", "wb") as f:
            f.write(qrcode)
        self.qrcode = Image.open(BytesIO(qrcode))
        self.qrcode.show()
        self.logger.log("等待亲爱的B站用户登陆～！")
        WebDriverWait(self.driver, 99999).until(
            ec.url_to_be("https://www.bilibili.com/")
        )
        self.logger.log("恭喜你这个B站用户，登陆成功啦～！")

    def wait_for_present(self):
        """
        Wait for broadcast message (全区广播). Upon reception, save the none duplicate links of loot tabs in a list and
        clear the chat history panel (弹幕窗口). Return the list.
        :return: A none duplicate list of links of loot tabs.
        """
        links = []
        self.logger.log("等待辣条中...")
        while self.timer:
            latiaos = self.driver.find_elements_by_xpath(
                '//div[@class="chat-item  system-msg border-box"]'
            )
            if len(latiaos) != 0:  # Found
                break
            sleep(5)
        self.logger.log("发现辣条！！！")
        for latiao in latiaos:
            try:
                link = latiao.find_element_by_tag_name("a").get_attribute("href")
                if link not in links:
                    links.append(link)
            except NoSuchElementException:
                # The Latiao is in base_tab channel.
                if LatiaoAid.base_tab_link not in links:
                    links.append(LatiaoAid.base_tab_link)
                continue
        self.clear_chat_history_panel()
        return links

    def clear_chat_history_panel(self):
        """
        Clear the chat-history-channel (弹幕历史).
        :return:
        """
        while self.timer:
            try:
                self.driver.find_element_by_xpath(
                    '//span[@class="icon-item icon-font icon-clear"]'
                ).click()
            except ElementClickInterceptedException:
                try:
                    # See if a popup blocks the button.
                    # This will happen if 主播勋章 upgrades, when A popup will show up.
                    shit = self.driver.find_element_by_xpath(
                        '//div[@class="link-popup-ctnr"]'
                    )
                    self.delete_element(shit)
                except NoSuchElementException:
                    # Some other things that block the button. Require human involvement.
                    self.logger.err(
                        "clear_chat_history_panel()", "清除历史弹幕按钮被遮挡了呢！！ 10 秒钟之后重试！！"
                    )
                    sleep(10)
                continue
            else:
                break

    def load_loot_tab(self, link):
        """
        Load and switch to loot tab. Wait for the lottery window (抽奖窗口) for 10 seconds. TimeoutException will be
        thrown if timeout.
        :param link: link of the loot tab.
        :return:
        """
        self.driver.execute_script(f"window.open('{link}')")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(2))
        tabs = self.driver.window_handles
        self.loot_tab = [tab for tab in tabs if tab != self.base_tab][0]
        self.driver.switch_to.window(self.loot_tab)
        _ = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, '//div[starts-with(@class, "function-bar")]')
            )
        )

    def wait_for_countdown(self, link):
        """
        Wait for Latiao to be claimable.

        If waiting time is longer than 5 seconds, close the loot tab, go back to base tab (to save resources) and put
        the process to sleep. Once the process is waked up, reload the loot tab and return.

        Otherwise return immediately.
        :param link: link of loot tab.
        :return:
        """
        element = self.driver.find_element_by_xpath(
            '//div[starts-with(@class, "function-bar")]'
        )
        if element.text == "点击领奖":
            return
        else:
            # At this moment, element.text can magically turn to "点击领奖", causing IndexError being thrown when
            # calculating second.
            s = element.text.replace("等待开奖", "")
            try:
                second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
            except IndexError:
                return
            if second > 5:
                self.close_go_back()
                self.logger.log(f"等 {second - 5} 秒再来")
                sleep(second - 5)
                self.load_loot_tab(link)
            return

    def collect(self):
        """
        Wait for a short period of time and click "点击领奖" to claim the price.
        :return:
        """
        element = self.driver.find_element_by_xpath(
            '//div[starts-with(@class, "function-bar")]'
        )
        while element.text != "点击领奖":
            pass
        sender_info_text = str(
            self.driver.find_element_by_xpath('//div[@class="gift-sender-info"]').text
        )

        bingos = self.driver.find_elements_by_xpath(
            '//div[@class="draw-bingo-cntr draw-bingo-cntr"]'
        )
        bingos += self.driver.find_elements_by_xpath('//div[@class="draw-bottom"]')
        for bingo in bingos:
            try:
                self.delete_element(bingo)
            except StaleElementReferenceException:
                pass

        while self.timer:
            try:
                element.click()
                break
            except ElementClickInterceptedException:
                self.logger.print(traceback.format_exc())
                return
            except StaleElementReferenceException:
                self.logger.print(traceback.format_exc())
                return
        loot = (
            "辣条"
            if "赠送" in sender_info_text
            else "辣条"
            if "赢得大乱斗PK胜利" in sender_info_text
            else "亲密度"
            if "上任" in sender_info_text
            else "不知道什么东西"
        )
        self.logger.log(f"{sender_info_text} {loot}到手")

    def main_loop(self):
        while self.timer:
            self.logger.caster = "MAIN_LOOP"
            links = self.wait_for_present()
            for link in links:
                try:
                    self.load_loot_tab(link)
                except TimeoutException:
                    self.logger.err("load_new_tab", "这个直播间好像加载的有点慢呢" + link)
                    self.close_go_back()
                    continue
                self.logger.caster = self.driver.find_element_by_xpath(
                    '//a[starts-with(@class, "room-owner-username")]'
                ).text
                self.logger.log("白嫖启动")
                while self.timer:
                    try:
                        self.wait_for_countdown(link)
                        self.collect()
                    except NoSuchElementException:
                        # No loot remains.
                        self.logger.log("白嫖结束")
                        sleep(1)
                        self.close_go_back()
                        break
                    except StaleElementReferenceException as e:
                        self.logger.err("MAIN_LOOP", "不好了不好了！！")
                        self.logger.print(traceback.format_exc())
                        self.close_go_back()
                        break
                    except TimeoutException:
                        # Failed to load page, or loot window magically disappear
                        self.logger.err("MAIN_LOOP", "诶！辣条怎么没了呢？！")
                        self.close_go_back()
                        break
                    except WebDriverException as e:
                        # Unknown exceptions
                        self.logger.err("MAIN_LOOP", "从来没见过的错误诶！")
                        self.logger.print(traceback.format_exc())
                        self.close_go_back()
                        break

    def main(self):
        self.logger.caster = "MAIN"
        self.login()
        self.load_base_tab()
        while self.timer:
            try:
                self.main_loop()
            except WebDriverException as e:
                self.logger.err("MAIN", "从来没见过的错误诶. 正在尝试恢复！.", e)
                self.logger.print(traceback.format_exc())
                try:
                    if len(self.driver.window_handles) == 2:
                        self.driver.execute_script("window.close()")
                        WebDriverWait(self.driver, 10).until(
                            ec.number_of_windows_to_be(1)
                        )
                        self.base_tab = self.driver.current_window_handle
                    self.load_base_tab()
                    continue
                except Exception as e:
                    self.logger.err("RECOVERY", "恢复失败. 程序即将退出.", e)
                    self.logger.print(traceback.format_exc())
                    self.driver.quit()
                    self.logger.log("LatiaoAid Terminated.")

    def __del__(self):
        self.driver.close()
        self.qrcode.close()
