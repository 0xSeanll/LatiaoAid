import traceback
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Logger import Logger

WEBDRIVER_PATH = '/usr/local/bin/geckodriver'
BASE_URL = "https://passport.bilibili.com/login"
YJZ_CHANNEL = "https://live.bilibili.com/528"


class LatiaoDisappearException(Exception):
    pass


class LatiaoAid:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=WEBDRIVER_PATH)
        self.base_tab = None
        self.loot_tab = None

    def close_go_back(self):
        self.driver.execute_script("window.close()")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
        self.driver.switch_to.window(self.base_tab)

    def to_loot_tab(self):
        self.driver.switch_to.window(self.loot_tab)

    def to_base_tab(self):
        self.driver.switch_to.window(self.base_tab)

    def load_channel_528(self):
        self.driver.get(YJZ_CHANNEL)
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@class="chat-history-panel"]')))
            except TimeoutError:
                Logger.err("login()", "Failed to load channel 528")
                self.driver.get(YJZ_CHANNEL)
                continue
            else:
                break
        self.base_tab = self.driver.current_window_handle

    def login(self):
        self.driver.get(BASE_URL)
        WebDriverWait(self.driver, 99999).until(ec.url_to_be("https://www.bilibili.com/"))

    def wait_for_present(self):
        links = []
        while True:
            latiaos = self.driver.find_elements_by_xpath('//div[@class="chat-item  system-msg border-box"]')
            if len(latiaos) != 0:
                break
            sleep(5)
        for latiao in latiaos:
            try:
                link = latiao.find_element_by_tag_name('a').get_attribute('href')
                if link not in links:
                    links.append(link)
            except NoSuchElementException as e:
                # Logger.err("wait_for_present()", "", e)
                if YJZ_CHANNEL not in links:
                    links.append(YJZ_CHANNEL)
                continue
        self.clear_chat_history_panel()
        return links

    def clear_chat_history_panel(self):
        while True:
            try:
                self.driver.find_element_by_xpath('//span[@class="icon-item icon-font icon-clear"]').click()
            except ElementClickInterceptedException as _:
                try:
                    element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
                except NoSuchElementException:
                    Logger.err("clear_chat_history_panel()",
                               "It seems that some thing obscures the clear screen button. Retry in 10 seconds.")
                    sleep(10)
                else:
                    try:
                        element.click()
                    except ElementClickInterceptedException as e:
                        Logger.err("clear_chat_history_panel()", "Unable to click 清楚弹幕. Retry.")
                        continue
            else:
                break

    def load_new_tab(self, link):
        self.driver.execute_script(f"window.open('{link}')")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(2))
        tabs = self.driver.window_handles
        self.loot_tab = [tab for tab in tabs if tab != self.base_tab][0]
        self.driver.switch_to.window(self.loot_tab)
        _ = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "function-bar")]'))
        )

    def wait_for_countdown(self, link):
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        if element.text == '点击领奖':
            return
        else:
            s = element.text.replace('等待开奖', '')
            if len(s) == 1:
                print("【真让人搞不懂】难道是字突然变了？", s)
                return
            second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
            if second > 5:
                self.close_go_back()
                Logger.log(f"等 {second - 5} 秒再来")
                sleep(second - 5)
                self.load_new_tab(link)
            return

    def collect(self):
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        while element.text != '点击领奖':
            s = element.text.replace('等待开奖', '')
            try:
                second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
            except IndexError:
                break
            if second > 5:
                Logger.err("collect()", "真让人搞不懂")
                return
        sender_info_text = str(self.driver.find_element_by_xpath('//div[@class="gift-sender-info"]').text)

        while True:
            try:
                element.click()
            except ElementClickInterceptedException as e:
                # Logger.err("collect()", "Cannot click 点击领奖", e)
                sleep(1)
                continue
            except StaleElementReferenceException as e:
                Logger.err("collect()", "点击领奖 Staled", e)
                break
            else:
                break

        loot = "辣条" if "赠送" in sender_info_text else \
            "辣条" if "赢得大乱斗PK胜利" in sender_info_text else \
                "亲密度" if "上任" in sender_info_text else "不知道什么东西"

        msg = f'{sender_info_text} {loot}到手'

        # ! This message sometimes is printed multiple times
        Logger.log(msg)

    # def show_loots(self):
    #     # self.driver.find_element_by_xpath('//div[@class="gift-package live-skin-highlight-bg"]').click()
    #     # _ = WebDriverWait(self.driver, 10).until(
    #     #     ec.presence_of_element_located((By.XPATH, '//div[@class="wrap"]'))
    #     # )
    #     loots = self.driver.find_elements_by_xpath('//div[@class="gift-item-wrap"]')[1:]
    #     total = 0
    #     expired_today = 0
    #     for loot in loots:
    #         expiration = loot.find_element_by_class_name("expiration").text
    #         # try:
    #         num = int(str(loot.find_element_by_class_name("num").text))
    #         # except ValueError:
    #         #     return
    #         # except StaleElementReferenceException:
    #         #     return
    #         total += num
    #         if expiration == "1天":
    #             expired_today += num
    #     Logger.log(f"包里有 {total} 根辣条，今天有 {expired_today} 根到保质期")
    #     # while True:
    #     #     try:
    #     #         self.driver.find_element_by_xpath('//div[@class="gift-package live-skin-highlight-bg"]').click()
    #     #     except ElementClickInterceptedException:
    #     #         continue
    #     #     else:
    #     #         break

    def main(self):
        self.login()
        self.load_channel_528()
        while True:
            try:
                while True:
                    links = self.wait_for_present()
                    for link in links:
                        try:
                            # TODO Remove duplicate links when finishing processing a link.
                            self.load_new_tab(link)
                        except TimeoutException as e:
                            Logger.err("load_new_tab", "load failed", e)
                            self.close_go_back()
                            continue

                        owner_name = \
                            self.driver.find_element_by_xpath('//a[starts-with(@class, "room-owner-username")]').text
                        Logger.caster = owner_name
                        Logger.log("白嫖启动")

                        while True:
                            try:
                                # TODO: 不应该一直在一个直播间墨迹
                                self.wait_for_countdown(link)
                                self.collect()
                            except IndexError as e:
                                Logger.err("LOOP", "Index Error", e)
                                traceback.print_exc()
                                continue
                            except NoSuchElementException as e:
                                Logger.log("没辣条了")
                                sleep(1)
                                self.close_go_back()
                                break
                            except StaleElementReferenceException as e:
                                Logger.err("LOOP", "StaleElementReferenceException", e)
                                traceback.print_exc()
                                self.close_go_back()
                                break
                            except TimeoutException as e:
                                Logger.err("LOOP", "load failed", e)
                                self.close_go_back()
                                break
                            except WebDriverException as e:
                                Logger.err("LOOP", "Unexpected exception", e)
                                traceback.print_exc()
                                self.close_go_back()
                                break

                        # try:
                        #     self.driver.find_element_by_xpath(
                        #         '//div[@class="gift-package live-skin-highlight-bg"]'
                        #     ).click()
                        #     self.show_loots()
                        # except WebDriverException as e:
                        #     Logger.err("show_loots()", e)

            except WebDriverException as e:
                Logger.err("OUTER LOOP", "Unexpected exception. Recovering.", e)
                traceback.print_exc()
                if len(self.driver.window_handles) == 2:
                    self.driver.execute_script("window.close()")
                    WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
                    self.base_tab = self.driver.current_window_handle
                self.load_channel_528()
                continue
            finally:
                self.driver.close()
                Logger.print("Driver closed")


if __name__ == '__main__':
    LatiaoAid().main()
