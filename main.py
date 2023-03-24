import pickle
from time import sleep
from os import getenv
from os.path import isfile as is_exists
from os import stat, path
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *


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
                    # input("Press Enter to save cookies")
                    # save_cookies(driver)
                    return True
        except Exception as e:
            if DEBUG:
                print(f"__need_code Error ->\n{e}")
            return False


def auth_dodo() -> bool:
    driver.get(dodo_url)
    # Кликнуть на кнопку войти в lk.dodocontrol.ru
    button_in_dodo = r'//*[@id="root"]/div[1]/div/form/div/div/a[1]'
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, button_in_dodo)))
    driver.find_element(By.XPATH, button_in_dodo).click()
    sleep(2)

    # Уже вошёл
    try:
        driver.find_element(By.CLASS_NAME, "col-sm-12").find_element(By.TAG_NAME, "h1")
        return True
    # Надо войти через VK
    except Exception as E:
        print("Need to LOG IN")
        if _auth_vk(driver):
            return True
    return False


def search_available(driver: webdriver) -> None | dict:
    return {pizzeria.find_element(By.TAG_NAME, "h2").text:
                {temp.find_element(By.CLASS_NAME, "type__name").text:
                     temp.find_element(By.CLASS_NAME, "type__date").text
                 for temp in pizzeria.find_elements(By.CLASS_NAME, "col-sm-4")}
            for pizzeria in driver.find_elements(By.CLASS_NAME, "pizzeria__list")}


def main():
    if not auth_dodo():
        print("Что-то пошло не так")
        return
    print("Я зашёл")
    input("Жду, когда начать сканить элементы в додо\n")
    result = search_available(driver)
    for pizzeria, dicti in result.items():
        # if "Воронеж" in pizzeria:
        print(pizzeria)
        for key, value in dicti.items():
            if key != "Инспекция":
                print(key, value, sep=" -> ", end="\t")
        print("\n\n")


if __name__ == "__main__":
    cookies_path = "cookies.pkl"
    dodo_url = "https://lk.dodocontrol.ru/checkRequests"
    DEBUG = True

    options = webdriver.ChromeOptions()
    options.add_argument('--allow-profiles-outside-user-dir')
    options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument(rf'--user-data-dir=C:\Users\Haskir\AppData\Local\Google\Chrome\Application\DodoUser')
    options.add_argument(rf'--profile-directory=C:\Users\Haskir\AppData\Local\Google\Chrome\Application\DodoUser')

    with webdriver.Chrome(options=options) as driver:
        main()
        input("Закрыть браузер?")
        try:
            driver.quit()
        except:
            ...
