from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
BASE_URL = "https://passport.bilibili.com/login"
YJZ_CHANNEL = "https://live.bilibili.com/528"


class Logger:
    owner_name = None

    @staticmethod
    def log(s):
        with open('log.txt', 'a') as f:
            line = f'[{datetime.now().__str__()}] '
            line += f'【{Logger.owner_name}】'
            line += s
            print(line)
            line += '\n'
            f.write(line)


class LatiaoDisappearException(Exception):
    pass


class LatiaoAid:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH)
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

    def login(self):
        self.driver.get(BASE_URL)
        WebDriverWait(self.driver, 99999).until(ec.url_to_be("https://www.bilibili.com/"))
        self.driver.get(YJZ_CHANNEL)
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@class="chat-history-panel"]')))
            except TimeoutError as e:
                self.driver.refresh()
                continue
            break

    def wait_for_present(self):
        links = []
        while True:
            latiaos = self.driver.find_elements_by_xpath('//div[@class="chat-item  system-msg border-box"]')
            if len(latiaos) != 0:
                break
            sleep(5)
        for latiao in latiaos:
            try:
                links.append(
                    latiao.find_element_by_tag_name('a').get_attribute('href')
                )
            except NoSuchElementException as e:
                continue
        self.clear_chat_history_panel()
        return links

    def clear_chat_history_panel(self):
        while True:
            try:
                self.driver.find_element_by_xpath('//span[@class="icon-item icon-font icon-clear"]').click()
            except ElementClickInterceptedException as e:
                print("It seems that some thing obscures the clear screen button. Retry in 10 seconds.")
                sleep(10)
            else:
                break

    def load_new_tab(self, link):
        self.driver.execute_script(f"window.open('{link}')")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(2))
        tabs = self.driver.window_handles
        self.loot_tab = [tab for tab in tabs if tab != self.base_tab][0]
        self.driver.switch_to.window(self.loot_tab)
        _ = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "function-bar")]'))
        )

    def wait_for_countdown(self, link):
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        if element.text == '点击领奖':
            return
        else:
            s = element.text.replace('等待开奖', '')
            second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
            if second > 5:
                self.close_go_back()
                Logger.log(f"等 {second - 5} 秒再来")
                sleep(second - 5)
                self.load_new_tab(link)
            return

    def collect(self):
        """
        Wait for 辣条s to be collectible and collect on the current tab, until there are not any.
        :return: No return value.
        """
        owner_name = self.driver.find_element_by_xpath('//a[starts-with(@class, "room-owner-username")]').text
        element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
        while element.text != '点击领奖':
            pass
        sender_info_text = str(self.driver.find_element_by_xpath('//div[@class="gift-sender-info"]').text)

        try:
            element.click()
        except ElementClickInterceptedException as e:
            print(e)
            sleep(1)
            return
        except StaleElementReferenceException as e:
            print(e)
            return

        loot = "辣条" if "赠送的小电视飞船" in sender_info_text else \
            "辣条" if "赢得大乱斗PK胜利" in sender_info_text else \
                "亲密度" if "上任提督" in sender_info_text else \
                    "亲密度" if "上任舰长" in sender_info_text else "亲密度"

        msg = f'{sender_info_text} {loot}到手'
        Logger.log(msg)

    def main(self):
        self.login()
        self.base_tab = self.driver.current_window_handle
        try:
            while True:
                links = self.wait_for_present()
                for link in links:
                    try:
                        self.load_new_tab(link)
                    except TimeoutException as e:
                        print("load failed", e)
                        self.close_go_back()
                        continue

                    owner_name = \
                        self.driver.find_element_by_xpath('//a[starts-with(@class, "room-owner-username")]').text
                    Logger.owner_name = owner_name
                    Logger.log("白嫖启动")

                    while True:
                        try:
                            self.wait_for_countdown(link)
                            self.collect()
                        except NoSuchElementException as e:
                            print("Latiao disappeared", e)
                            Logger.log("没辣条了")
                            self.close_go_back()
                            break
                        except TimeoutException as e:
                            print("load failed", e)
                            self.close_go_back()
                            break
        finally:
            self.driver.close()
            print("Driver closed")

    def test(self):
        self.login()
        self.base_tab = self.driver.current_window_handle
        while True:
            latiaos = self.driver.find_elements_by_xpath('//div[@class="chat-item  system-msg border-box"]')
            if len(latiaos) != 0:
                for latiao in latiaos:
                    try:
                        print(latiao.text)
                    except NoSuchElementException as e:
                        continue
            sleep(5)


if __name__ == '__main__':
    LatiaoAid().main()
