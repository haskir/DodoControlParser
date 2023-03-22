import pickle
from time import sleep
from os import getenv
from os.path import isfile as is_exists
from os import stat
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def load_cookies(driver: webdriver) -> bool:
    if not is_exists(cookies_path) or stat(cookies_path).st_size <= 1:
        return False
    args = "br"
    try:
        for cookie in pickle.load(open(cookies_path, args)):
            driver.add_cookie(cookie)
        print(f"Cookies loaded!")
    except Exception as e:
        if DEBUG:
            print(f"load_cookies Error ->\n{e}")
        return False
    else:
        return True


def save_cookies(driver: webdriver) -> bool:
    args = "wb"
    try:
        cookies = driver.get_cookies()
        pickle.dump(cookies, open(cookies_path, args))
    except Exception as e:
        if DEBUG:
            print(f"save_cookies Error ->\n{e}")
        return False
    else:
        print("Cookies saved")
        return True


def _auth_vk(driver: webdriver) -> bool:
    try:
        load_dotenv()
        email: str = getenv('email')
        password: str = getenv('password')
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "pass")
        email_field.send_keys(email)
        password_field.send_keys(password)
        driver.find_element(By.ID, "install_allow").click()
        if __need_code(driver):
            return True
        else:
            return False
    except Exception as e:
        if DEBUG:
            print(f"_auth_vk Error ->\n{e}")
        return False
    input()
    return True


def __need_code(driver: webdriver) -> bool:
    try:
        submit_button = driver.find_element(By.CSS_SELECTOR, "[type=submit]")
    except Exception as e:
        ...
    else:
        try:
            while True:
                sleep(2)
                if len(driver.find_element(By.NAME, "code").get_attribute("value")) == 6:
                    submit_button = driver.find_element(By.CSS_SELECTOR, "[type=submit]")
                    submit_button.click()
                    input("Press Enter to save cookies")
                    save_cookies(driver)
                    return True
        except Exception as e:
            if DEBUG:
                print(f"__need_code Error ->\n{e}")
            return False


def auth_dodo() -> bool:
    have_cookies: bool = False

    driver.get("https://vk.com")
    load_cookies(driver)
    sleep(3)
    driver.refresh()
    sleep(3)
    driver.get(dodo_url)
    button_in_dodo = r'//*[@id="root"]/div[1]/div/form/div/div/a[1]'
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, button_in_dodo)))
    driver.find_element(By.XPATH, button_in_dodo).click()
    sleep(3)

    # if is_exists(cookies_path):
    #     print("Загружаю куки")
    #     have_cookies = load_cookies(driver)
    #     if not have_cookies:
    #         print("Ошибка при загрузке куков")
    #         return False
    #     sleep(3)
    #     driver.refresh()
    # else:
    #     _auth_vk(driver)


def main():
    if auth_dodo():
        print("Я зашёл")
    else:
        print("Что-то пошло не так")


if __name__ == "__main__":
    DEBUG = True
    driver = webdriver.Chrome()
    cookies_path = "cookies.pkl"
    dodo_url = "https://lk.dodocontrol.ru/login"
    main()