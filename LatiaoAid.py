from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
BASE_URL = "https://passport.bilibili.com/login"
YJZ_CHANNEL = "https://live.bilibili.com/528"


class LatiaoAid:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH)
        self.base_tab = None

    def close_go_back(self):
        self.driver.execute_script("window.close()")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(1))
        self.driver.switch_to.window(self.base_tab)

    def new_tab(self, link):
        self.driver.execute_script(f"window.open('{link}')")
        WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(2))

    def login(self):
        self.driver.get(BASE_URL)
        WebDriverWait(self.driver, 99999).until(ec.url_to_be("https://www.bilibili.com/"))
        self.driver.get(YJZ_CHANNEL)
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@class="chat-history-panel"]')))
            except TimeoutError as e:
                print(e)
                continue
            break

    def wait_tab_loading(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "function-bar")]'))
            )
        except TimeoutException as e:
            return False,
        else:
            return True, element

    def main(self):
        self.login()

        self.base_tab = self.driver.current_window_handle

        while True:
            links = []

            # Smell for latiao
            while True:
                latiaos = self.driver.find_elements_by_xpath('//div[@class="chat-item  system-msg border-box"]')
                if len(latiaos) != 0:
                    break
                else:
                    sleep(5)
            for latiao in latiaos:
                links.append(
                    latiao.find_element_by_tag_name('a').get_attribute('href'))  # will throw NoSuchElementException

            # Clear chat history panel
            while True:
                try:
                    self.driver.find_element_by_xpath('//span[@class="icon-item icon-font icon-clear"]').click()
                except ElementClickInterceptedException as e:
                    print("It seems that some thing obscures the clear screen button. Retry in 10 seconds.")
                    sleep(10)
                else:
                    break

            # Go to the last lottory
            # TODO: Utilize all accessible links
            link = links[-1]

            # Open a new tab
            self.new_tab(link)

            # Switch driver to new tab
            windows_after = self.driver.window_handles
            new_window = [x for x in windows_after if x != self.base_tab][0]
            self.driver.switch_to.window(new_window)

            # Check whether the necessary parts of a current tab has been loaded
            check_result = self.wait_tab_loading()
            if not check_result[0]:
                self.close_go_back()
            element = check_result[1]

            while True:
                # Wait for and claim latiao
                try:
                    while element.text != '点击领奖':
                        s = element.text.replace('等待开奖', '')
                        second = int(s.split(":")[1]) + int(s.split(":")[0]) * 60
                        if second >= 40:
                            sleep(30)
                        elif second > 5:
                            sleep(4)
                    element.click()
                except NoSuchElementException as e:
                    pass
                except IndexError as e:
                    pass
                except ValueError as e:
                    pass
                except ElementClickInterceptedException as e:
                    # Wait for dynamically generated obstacle to disappear.
                    sleep(2)
                else:
                    print("Latiao obtained")

                # Check if there still are.
                try:
                    element = self.driver.find_element_by_xpath('//div[starts-with(@class, "function-bar")]')
                except NoSuchElementException as e:
                    print("都没了")
                    break
            self.close_go_back()


if __name__ == '__main__':
    LatiaoAid().main()
