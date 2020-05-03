import traceback
from io import BytesIO
from time import sleep

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Logger import Logger

WEBDRIVER_PATH = '/usr/local/bin/geckodriver'
BASE_URL = "https://passport.bilibili.com/login"
BASE_TAB_LINK = "https://live.bilibili.com/528"


class LatiaoDisappearException(Exception):
    pass


class LatiaoAid:
    def __init__(self, headless=False, disable_image=False):
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument('-headless')
        profile = webdriver.FirefoxProfile()
        if disable_image:
            profile.set_preference("permissions.default.image", 2)
        self.driver = webdriver.Firefox(executable_path=WEBDRIVER_PATH, firefox_profile=profile, options=options)
        self.base_tab = None  # The tab used to collect broadcast info. YJZ_CHANNEL
        self.loot_tab = None  # The tab where the code collect 辣条

    def close_go_back(self):
        """
        Close loot tab and go back to base tab.
        :return:
        """
        self.driver.execute_script("window.close()")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
        self.driver.switch_to.window(self.base_tab)

    def to_loot_tab(self):
        """
        Switch to loot tab.
        :return:
        """
        self.driver.switch_to.window(self.loot_tab)

    def to_base_tab(self):
        """
        Switch to base tab
        :return:
        """
        self.driver.switch_to.window(self.base_tab)

    def delete_element(self, element):
        """
        Delete an specific element of the page
        :param element: the WebElement to be deleted
        :return:
        """
        self.driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element)

    def load_base_tab(self):
        """
        Load base tab, and wait for chat-history-panel(弹幕窗口) to show up. Update self.base_tab
        :return:
        """
        self.driver.get(BASE_TAB_LINK)
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@class="chat-history-panel"]')))
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@id="chat-draw-area-vm"]')))
                self.delete_element(element)
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located(
                        (By.XPATH, '//div[@data-upgrade-intro="Follow"]//div[@class="side-bar-btn-cntr"]')))
                element.click()
            except TimeoutError:
                Logger.err("login()", "Failed to load channel 528")
                self.driver.get(BASE_TAB_LINK)
                continue
            else:
                break
        self.base_tab = self.driver.current_window_handle

    def login(self):
        """
        Bring up login page and wait for a human to login.
        :return:
        """
        self.driver.get(BASE_URL)
        qrcode_img = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div[3]/div[1]/div').screenshot_as_png
        img = Image.open(BytesIO(qrcode_img))
        img.show()
        WebDriverWait(self.driver, 99999).until(ec.url_to_be("https://www.bilibili.com/"))
        Logger.print("恭喜你这个B站用户，登陆成功啦～")

    def wait_for_present(self):
        """
        Wait for broadcast message (全区广播). Upon reception, save the none duplicate links of loot tabs in a list and
        clear the chat history panel (弹幕窗口). Return the list.
        :return: A none duplicate list of links of loot tabs.
        """
        links = []
        while True:
            latiaos = self.driver.find_elements_by_xpath('//div[@class="chat-item  system-msg border-box"]')
            if len(latiaos) != 0:  # Found
                break
            sleep(5)
        for latiao in latiaos:
            try:
                link = latiao.find_element_by_tag_name('a').get_attribute('href')
                if link not in links:
                    links.append(link)
            except NoSuchElementException:
                # The Latiao is in base_tab channel.
                if BASE_TAB_LINK not in links:
                    links.append(BASE_TAB_LINK)
                continue
        self.clear_chat_history_panel()
        return links

    def clear_chat_history_panel(self):
        """
        Clear the chat-history-channel (弹幕历史).
        :return:
        """
        while True:
            try:
                self.driver.find_element_by_xpath('//span[@class="icon-item icon-font icon-clear"]').click()
            except ElementClickInterceptedException as _:
                try:
                    # See if a popup blocks the button.
                    # This will happen if 主播勋章 upgrades, when A popup will show up.
                    shit = self.driver.find_element_by_xpath('//div[@class="link-popup-ctnr"]')
                    self.delete_element(shit)
                except NoSuchElementException:
                    # Some other things that block the button. Require human involvement.
                    Logger.err("clear_chat_history_panel()",
                               "It seems that some thing obscures the clear screen button. Retry in 10 seconds.")
                    sleep(10)
                finally:
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
            ec.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "function-bar")]'))
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
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        if element.text == '点击领奖':
            return
        else:
            # At this moment, element.text can magically turn to "点击领奖", causing IndexError being thrown when
            # calculating second.
            s = element.text.replace('等待开奖', '')
            try:
                second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
            except IndexError:
                return
            if second > 5:
                self.close_go_back()
                Logger.log(f"等 {second - 5} 秒再来")
                sleep(second - 5)
                self.load_loot_tab(link)
            return

    def collect(self):
        """
        Wait for a short period of time and click "点击领奖" to claim the price.
        :return:
        """
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        while element.text != '点击领奖':
            pass
        sender_info_text = str(self.driver.find_element_by_xpath('//div[@class="gift-sender-info"]').text)

        while True:
            try:
                element.click()
                break
            except ElementClickInterceptedException as e:
                # A feedback window obscures the button.
                bingos = self.driver.find_elements_by_xpath('//div[@class="draw-bingo-cntr draw-bingo-cntr"]')
                bingos += self.driver.find_elements_by_xpath('//div[@class="draw-bottom"]')
                for bingo in bingos:
                    try:
                        self.delete_element(bingo)
                    except StaleElementReferenceException:
                        continue
                continue
        loot = "辣条" if "赠送" in sender_info_text else \
            "辣条" if "赢得大乱斗PK胜利" in sender_info_text else \
                "亲密度" if "上任" in sender_info_text else "不知道什么东西"
        Logger.log(f'{sender_info_text} {loot}到手')

    def main(self):
        self.login()
        self.load_base_tab()
        while True:
            try:
                while True:
                    links = self.wait_for_present()
                    for link in links:
                        try:
                            self.load_loot_tab(link)
                        except TimeoutException:
                            Logger.err("load_new_tab", "这个直播间好像加载的有点慢呢" + link)
                            self.close_go_back()
                            continue
                        Logger.caster = \
                            self.driver.find_element_by_xpath('//a[starts-with(@class, "room-owner-username")]').text
                        Logger.log("白嫖启动")
                        while True:
                            try:
                                self.wait_for_countdown(link)
                                self.collect()
                            except NoSuchElementException:
                                # No loot remains.
                                Logger.log("白嫖结束")
                                sleep(1)
                                self.close_go_back()
                                break
                            except StaleElementReferenceException as e:
                                Logger.err("LOOP", "StaleElementReferenceException 不好了不好了！！", e)
                                traceback.print_exc()
                                self.close_go_back()
                                break
                            except TimeoutException as e:
                                # Failed to load page, or loot window magically disappear
                                Logger.err("LOOP", "诶！辣条怎么没了呢？！")
                                self.close_go_back()
                                break
                            except WebDriverException as e:
                                # Unknown exceptions
                                Logger.err("LOOP", "从来没见过的错误诶！", e)
                                traceback.print_exc()
                                self.close_go_back()
                                break
            except WebDriverException as e:
                Logger.err("OUTER LOOP", "从来没见过的错误诶. 正在尝试恢复！.", e)
                traceback.print_exc()
                if len(self.driver.window_handles) == 2:
                    self.driver.execute_script("window.close()")
                    WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
                    self.base_tab = self.driver.current_window_handle
                self.load_base_tab()
                continue
            finally:
                self.driver.close()
                Logger.print("Driver closed")


if __name__ == '__main__':
    LatiaoAid(headless=True, disable_image=True).main()
