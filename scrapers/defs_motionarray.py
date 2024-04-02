import os
import pickle
import threading
import time
from custom_logs.models import custom_log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from maxim_telegram_bot.settings import CHROME_DRIVER_PATH, BASE_DIR
from scrapers.defs_common import check_chrome_connection_status, download_file_with_aria2_download_manager
from scrapers.models import get_motion_array_config_settings, MotionArrayAccount
from utilities.slug_generator import name_cleaner

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}


# ------------ Start Scraper functions -------------------
def get_time_sleep():
    time_sleep = get_motion_array_config_settings().sleep_time
    return time_sleep


def motion_array_check_if_sign_in_is_needed(motion_array_account):
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, desired_capabilities=d)
    webdriver_problem_number_of_reloading = 0
    while True:
        try:
            while True:
                custom_log("motion_array_check_if_sign_in_is_needed: starting page load", f"scrapers")
                driver.get('https://motionarray.com/account/login/')
                try:
                    cookies = pickle.load(open(motion_array_account.motion_array_cookie.path, 'rb'))
                    for cookie in cookies:
                        driver.add_cookie(cookie)
                except Exception as e:
                    custom_log(f"motion_array_check_if_sign_in_is_needed: {str(e)}", f"scrapers")
                    motion_array_account.motion_array_account_description = f'motion array cookie does not exist. please provide new cookie'
                    motion_array_account.is_account_active = False
                    motion_array_account.save()
                    return True

                custom_log("loading cookie has completed. we are waiting for: " + str(get_time_sleep()), f"scrapers")
                time.sleep(get_time_sleep())

                driver.refresh()
                custom_log("driver has been refreshed. we are waiting for: " + str(get_time_sleep()), f"scrapers")
                time.sleep(get_time_sleep())

                check_chrome_connection_status(driver)
                custom_log("checking check_chrome_connection_status has been done.", f"scrapers")

                current_url = driver.current_url
                print("Current URL:", current_url)

                if current_url == 'https://motionarray.com/account/details/':
                    message = f'auth with *{motion_array_account.motion_array_cookie.path}* cookie has been accepted.'
                    custom_log(message, f"scrapers")
                    motion_array_account.motion_array_account_description = message
                    motion_array_account.is_account_active = True
                    motion_array_account.save()
                    driver.quit()
                    return False
                else:
                    message = f'auth with *{motion_array_account.motion_array_cookie.path}* cookie has been failed. it means new sign-in require'
                    custom_log(message, f"scrapers")
                    motion_array_account.motion_array_account_description = message
                    motion_array_account.is_account_active = False
                    motion_array_account.save()
                    driver.quit()
                    return True
        except NoSuchElementException as e:
            custom_log('motion_array_check_if_sign_in_is_needed webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(get_time_sleep())
        except WebDriverException as e:
            custom_log('motion_array_check_if_sign_in_is_needed webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            custom_log('motion_array_check_if_sign_in_is_needed webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(get_time_sleep())
        except Exception as e:
            custom_log('motion_array_check_if_sign_in_is_needed webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            message = "motion_array_check_if_sign_in_is_needed: webdriver exception caused auth function to be aborted"
            custom_log(message, f"scrapers")
            motion_array_account.motion_array_account_description = message
            motion_array_account.save()
            driver.quit()
            return True


def motion_array_check_auth():
    MotionArrayCheckAuthThread().start()


class MotionArrayCheckAuthThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        motion_array_accounts = MotionArrayAccount.objects.filter(is_account_active=True)
        for motion_array_account in motion_array_accounts:
            motion_array_check_if_sign_in_is_needed(motion_array_account)


def motion_array_download_file(motion_array_file, account_to_use):
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--headless=new")
    # options.add_argument("--disable-web-security")
    # options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--ignore-certificate-errors")
    motion_array_files_path = BASE_DIR / 'media/cr/'
    prefs = {"download.default_directory": f"{motion_array_files_path}"}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, desired_capabilities=d)
    webdriver_problem_number_of_reloading = 0
    direct_download_list = []
    scrap_then_download_list = []
    if motion_array_file.file_storage_link:
        direct_download_list.append(motion_array_file)
    else:
        scrap_then_download_list.append(motion_array_file)

    # part 1
    if len(direct_download_list) != 0:
        direct_download_file = direct_download_list[0]
        custom_log("motion_array_download_file: start downloading the files", f"scrapers")
        number_of_try = 0
        while True:
            try:
                custom_log(f"motion_array_download_file: start downloading the file: {direct_download_file.unique_code}", f"scrapers")
                original_name = name_cleaner(direct_download_file.file_storage_link)
                file_name, file_extension = os.path.splitext(original_name)
                if len(file_extension) > 6:
                    file_extension = '.zip'
                new_name = f'{direct_download_file.unique_code}{file_extension}'
                download_file_with_aria2_download_manager(direct_download_file, new_name,
                                                          direct_download_file.file_storage_link)
                break
            except Exception as e:
                custom_log(f"motion_array_download_file: failed to download file: {direct_download_file.unique_code} try/except-> err: " + str(
                        e), f"scrapers")
                time.sleep(1)
                number_of_try += 1
            if number_of_try == 3:
                custom_log(f"motion_array_download_file: after 3 time of reloads failed to download file: {direct_download_file}", f"scrapers")
                direct_download_file.download_percentage = 0
                direct_download_file.is_acceptable_file = False
                direct_download_file.in_progress = False
                direct_download_file.save()
                break

    if len(scrap_then_download_list) != 0:
        scrap_then_download_file = scrap_then_download_list[0]
        # part 2
        while True:
            try:
                number_of_get_accept_cookie_btn_tries = 0
                while True:
                    try:
                        custom_log("motion_array_download_file: start loading cookie", f"scrapers")
                        driver.get('https://motionarray.com/account/login/')

                        cookies = pickle.load(open(account_to_use.motion_array_cookie.path, 'rb'))
                        for cookie in cookies:
                            driver.add_cookie(cookie)
                        custom_log("loading cookie has been completed. we are waiting for: " + str(get_time_sleep()), f"scrapers")
                        time.sleep(get_time_sleep())

                        driver.refresh()
                        custom_log("driver has been refreshed. we are waiting for: " + str(get_time_sleep()), f"scrapers")
                        time.sleep(get_time_sleep())

                        check_chrome_connection_status(driver)
                        custom_log("checking check_chrome_connection_status has been done.", f"scrapers")

                        i = 0
                        try:
                            custom_log(f"motion_array_download_file: start downloading the file: {scrap_then_download_file.page_link}", f"scrapers")
                            driver.switch_to.new_window(f'tab_{i}')
                            driver.get(scrap_then_download_file.page_link)

                            custom_log(f"the url has been gotten. we are waiting for: {get_time_sleep()}", f"scrapers")
                            time.sleep(get_time_sleep())

                            custom_log(f"motion_array_download_file: tab title is: {driver.title}", f"scrapers")

                            if str(driver.title).find('Page not found') != -1:
                                custom_log(
                                    "motion_array_download_file: requested url page not found", f"scrapers")
                                scrap_then_download_file.is_acceptable_file = False
                                scrap_then_download_file.in_progress = False
                                scrap_then_download_file.failed_repeat = 10
                                scrap_then_download_file.save()
                                return

                            number_of_checking_download_btn = 0
                            while True:
                                try:
                                    custom_log("motion_array_download_file: check visibility of download btn", f"scrapers")
                                    WebDriverWait(driver, 15).until(
                                        EC.presence_of_all_elements_located((By.TAG_NAME, 'span')))
                                    all_available_spans = driver.find_elements(By.TAG_NAME, 'span')
                                    for span in all_available_spans:
                                        span_text = span.text.strip()
                                        if span_text == 'Download':
                                            driver.execute_script("return arguments[0].parentNode.click();", span)
                                            custom_log(f"scrapers", "motion_array_download_file: download btn has been clicked.")
                                            break
                                    break
                                except Exception as e:
                                    print(e)
                                    custom_log("motion_array_download_file: failed to find download btn", f"scrapers")
                                    number_of_checking_download_btn += 1
                                if number_of_checking_download_btn == 3:
                                    custom_log("motion_array_download_file: after 3 times of reload, failed to find download btn", f"scrapers")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.failed_repeat = 10
                                    scrap_then_download_file.save()
                                    return

                            driver.switch_to.new_window(f'tab_download_{i}')
                            driver.get('chrome://downloads')

                            chrome_downloads_page_visibility = 0
                            while_situation = True
                            while True:
                                try:
                                    custom_log("motion_array_download_file: check for chrome downloads page", f"scrapers")
                                    WebDriverWait(driver, 15).until(
                                        EC.visibility_of_element_located((By.XPATH,
                                                                          '/html/body/downloads-manager')))
                                    custom_log("motion_array_download_file: chrome downloads has showed up", f"scrapers")
                                    break
                                except Exception as e:
                                    custom_log("motion_array_download_file: failed to find chrome downloads page. err: " + str(e), f"scrapers")
                                    chrome_downloads_page_visibility += 1
                                if chrome_downloads_page_visibility == 3:
                                    driver.quit()
                                    custom_log("motion_array_download_file: after 3 times of reload, failed chrome downloads page", f"scrapers")
                                    while_situation = False
                                    break
                                time.sleep(0.5)
                            if not while_situation:
                                custom_log(f"motion_array_download_file: failed to download file: {scrap_then_download_file.page_link}", f"scrapers")
                                scrap_then_download_file.is_acceptable_file = False
                                scrap_then_download_file.in_progress = False
                                scrap_then_download_file.save()
                                continue
                            custom_log("motion_array_download_file: tab title is: " + str(driver.title), f"scrapers")
                            download_manager = driver.find_element(By.XPATH, '/html/body/downloads-manager')
                            while True:
                                download_item_list = str(download_manager.text).split('\n')
                                if download_item_list[2] == 'Files you download appear here':
                                    print(str(download_manager.text).split('\n'))
                                    time.sleep(1)
                                else:
                                    break
                            while True:
                                download_item_list = str(download_manager.text).split('\n')
                                if str(download_item_list[4]).find('https://') != -1:
                                    name_script = f'''
                                                    const first_shadow_root = document.querySelector("downloads-manager").shadowRoot
                                                    const download_items = first_shadow_root.querySelectorAll("downloads-item")
                                                    const second_shadow_root = download_items[0].shadowRoot
                                                    const name = second_shadow_root.getElementById("name").textContent
                                                    return name
                                                    '''
                                    url_script = f'''
                                                    const first_shadow_root = document.querySelector("downloads-manager").shadowRoot
                                                    const download_items = first_shadow_root.querySelectorAll("downloads-item")
                                                    const second_shadow_root = download_items[0].shadowRoot
                                                    const url = second_shadow_root.getElementById("file-link")['href']
                                                    return url
                                                    '''
                                    name = driver.execute_script(name_script)
                                    url = driver.execute_script(url_script)
                                    print(name)
                                    print(url)
                                    driver.close()
                                    driver.quit()
                                    break
                                else:
                                    print(str(download_manager.text).split('\n'))
                                    time.sleep(0.05)
                            original_name = name
                            original_name = name_cleaner(original_name)
                            file_name, file_extension = os.path.splitext(original_name)
                            if len(file_extension) > 6:
                                file_extension = '.zip'
                            new_name = f'{scrap_then_download_file.unique_code}{file_extension}'
                            download_status = download_file_with_aria2_download_manager(scrap_then_download_file, new_name, url)
                            if not download_status:
                                custom_log(f'motion_array_download_file: download manager download_status is False', f"scrapers")
                                raise
                        except Exception as e:
                            custom_log("motion_array_download_file: failed to download file: " + str(
                                scrap_then_download_file) + " try/except-> err: " + str(e), f"scrapers")
                            scrap_then_download_file.download_percentage = 0
                            scrap_then_download_file.failed_repeat += 1
                            scrap_then_download_file.is_acceptable_file = False
                            scrap_then_download_file.in_progress = False
                            scrap_then_download_file.save()
                        custom_log(f"scrap_then_download_file: finish file: {scrap_then_download_file.page_link}", f"scrapers")
                        return True
                    except Exception as e:
                        number_of_get_accept_cookie_btn_tries += 1
                        if number_of_get_accept_cookie_btn_tries == 3:
                            custom_log("scrap_then_download_file: after 3 times of reload, download has been failed. err: " + str(e), f"scrapers")
                            driver.quit()
                            scrap_then_download_file.download_percentage = 0
                            scrap_then_download_file.is_acceptable_file = True
                            scrap_then_download_file.in_progress = False
                            scrap_then_download_file.save()
                            return False
            except NoSuchElementException as e:
                custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
                time.sleep(get_time_sleep())
            except WebDriverException as e:
                custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
                time.sleep(get_time_sleep())
            except ConnectionError as e:
                custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
                time.sleep(get_time_sleep())
            except Exception as e:
                custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
                time.sleep(get_time_sleep())
            webdriver_problem_number_of_reloading += 1
            if webdriver_problem_number_of_reloading == 3:
                driver.quit()
                custom_log("motion_array_download_file: webdriver exception caused download to be aborted", f"scrapers")
                scrap_then_download_file.download_percentage = 0
                scrap_then_download_file.is_acceptable_file = True
                scrap_then_download_file.in_progress = False
                scrap_then_download_file.save()
                return False
