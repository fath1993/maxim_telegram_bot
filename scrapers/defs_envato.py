import os
import pickle
import threading
import time
import jdatetime
from custom_logs.models import custom_log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from scrapers.defs_common import check_chrome_connection_status, download_file_with_aria2_download_manager
from scrapers.models import get_envato_config_settings, EnvatoAccount, get_envato_account
from maxim_telegram_bot.settings import CHROME_DRIVER_PATH, BASE_DIR, DOWNLOAD_FOLDER
from utilities.slug_generator import name_cleaner

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}


# ------------ Start Scraper functions -------------------
def get_time_sleep():
    time_sleep = get_envato_config_settings().sleep_time
    return time_sleep


def envato_check_if_sign_in_is_needed(envato_account):
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
            number_of_get_accept_cookie_btn_tries = 0
            while True:
                custom_log("check_if_sign_in_is_needed: starting page load", "d")
                driver.get(
                    'https://elements.envato.com/sign-in?targetUrl=https://account.elements.envato.com/subscription')
                try:
                    cookies = pickle.load(open(envato_account.envato_cookie.path, 'rb'))
                    for cookie in cookies:
                        driver.add_cookie(cookie)
                except Exception as e:
                    custom_log(f"check_if_sign_in_is_needed: {str(e)}", "d")
                    envato_account.envato_account_description = f'cookie does not exist. please provide new cookie'
                    envato_account.save()
                    return True
                driver.refresh()
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                check_chrome_connection_status(driver)
                try:
                    custom_log("check_if_sign_in_is_needed: check for user detail", "d")
                    WebDriverWait(driver, 30).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '.R7UIfAnZ')))
                    try:
                        plan_summery = driver.find_elements(By.CSS_SELECTOR, '.R7UIfAnZ')[0]
                        envato_account.envato_account_description = str(plan_summery.text)
                        envato_account.save()
                        driver.quit()
                        custom_log("check_if_sign_in_is_needed: account plan confirmed", "d")
                        return False
                    except:
                        driver.quit()
                        custom_log("check_if_sign_in_is_needed: account plan not confirmed", "d")
                        envato_account.envato_account_description = f'account plan not confirmed'
                        envato_account.save()
                        return True
                except Exception as e:
                    custom_log(
                        "check_if_sign_in_is_needed: user detail not found", "d")
                number_of_get_accept_cookie_btn_tries += 1
                if number_of_get_accept_cookie_btn_tries == 2:
                    driver.quit()
                    custom_log(
                        "check_if_sign_in_is_needed: after 2 times of reload, auth function with cookie has been failed. it means new sign-in require",
                        "d")
                    envato_account.envato_account_description = f'after 2 times of reload,  auth function with cookie has been failed. it means new sign-in require'
                    envato_account.save()
                    driver.quit()
                    return True
        except NoSuchElementException as e:
            custom_log('check_if_sign_in_is_needed webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except WebDriverException as e:
            custom_log('check_if_sign_in_is_needed webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            custom_log('check_if_sign_in_is_needed webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except Exception as e:
            custom_log('check_if_sign_in_is_needed webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            custom_log("check_if_sign_in_is_needed: webdriver exception caused auth function to be aborted", 'd')
            envato_account.envato_account_description = f'webdriver exception caused auth function to be aborted'
            envato_account.save()
            return True


def envato_check_auth():
    EnvatoCheckAuthThread().start()


class EnvatoCheckAuthThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
        for envato_account in envato_accounts:
            envato_check_if_sign_in_is_needed(envato_account)


def envato_download_file(envato_file, account_to_use):
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--headless=new")
    envato_files_path = BASE_DIR / 'media/files/'
    prefs = {"download.default_directory": f"{envato_files_path}"}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, desired_capabilities=d)
    webdriver_problem_number_of_reloading = 0
    direct_download_list = []
    scrap_then_download_list = []
    if envato_file.file_storage_link:
        direct_download_list.append(envato_file)
    else:
        scrap_then_download_list.append(envato_file)

    # part 1
    if len(direct_download_list) != 0:
        direct_download_file = direct_download_list[0]
        custom_log("envato_download_file: start downloading the files", "d")
        number_of_try = 0
        while True:
            try:
                custom_log(f"envato_download_file: start downloading the file: {direct_download_file.unique_code}")
                original_name = name_cleaner(direct_download_file.file_storage_link)
                file_name, file_extension = os.path.splitext(original_name)
                if len(file_extension) > 6:
                    file_extension = '.zip'
                new_name = f'{direct_download_file.unique_code}{file_extension}'
                download_file_with_aria2_download_manager(direct_download_file, new_name,
                                                          direct_download_file.file_storage_link)
                break
            except Exception as e:
                custom_log(
                    f"envato_download_file: failed to download file: {direct_download_file.unique_code} try/except-> err: " + str(
                        e), "d")
                time.sleep(1)
                number_of_try += 1
            if number_of_try == 3:
                custom_log(
                    f"envato_download_file: after 3 time of reloads failed to download file: {direct_download_file}")
                direct_download_file.download_percentage = 0
                direct_download_file.is_acceptable_file = False
                direct_download_file.in_progress = False
                direct_download_file.save()
                break

    # part 2
    if len(scrap_then_download_list) != 0:

        scrap_then_download_file = scrap_then_download_list[0]
        while True:
            try:
                number_of_get_accept_cookie_btn_tries = 0
                while True:
                    try:
                        custom_log("envato_download_file: starting page load", "d")
                        driver.get('https://elements.envato.com/')
                        cookies = pickle.load(open(account_to_use.envato_cookie.path, 'rb'))
                        for cookie in cookies:
                            driver.add_cookie(cookie)
                        time.sleep(1)
                        driver.refresh()

                        # time.sleep(3600)
                        custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()),
                                   'd')
                        # time.sleep(get_time_sleep())
                        time.sleep(1)
                        check_chrome_connection_status(driver)
                        custom_log("envato_download_file: start downloading the files", "d")

                        i = 0
                        try:
                            custom_log("envato_download_file: start downloading the file: " + str(scrap_then_download_file), "d")
                            driver.switch_to.new_window(f'tab_{i}')
                            driver.get(scrap_then_download_file.page_link)
                            time.sleep(5)
                            custom_log("envato_download_file: tab title is: " + str(driver.title), "d")
                            number_of_checking_categories = 0
                            while_situation = True
                            while True:
                                try:
                                    custom_log("envato_download_file: check that if categories are visible", "d")
                                    WebDriverWait(driver, 15).until(
                                        EC.presence_of_all_elements_located(
                                            (By.CSS_SELECTOR, '.mIe6goMR.igMtSiA8.dp4yRDc1')))
                                    custom_log("envato_download_file: categories are visible", "d")
                                    categories_section = 'NOT 3D'
                                    custom_log("envato_download_file: category is NOT 3D", "d")
                                    break
                                except Exception as e:
                                    custom_log(
                                        "envato_download_file: failed to find none 3D category", "d")
                                    try:
                                        custom_log("envato_download_file: check for 404 error page", "d")
                                        WebDriverWait(driver, 20).until(
                                            EC.visibility_of_element_located((By.CLASS_NAME, 'DsS8cj_E')))
                                        custom_log("envato_download_file: 404 error page has showed up", "d")
                                        while_situation = False
                                        categories_section = 'none'
                                        break
                                    except Exception as e:
                                        pass
                                    number_of_checking_categories += 1
                                if number_of_checking_categories == 2:
                                    categories_section = '3D'
                                    custom_log("envato_download_file: category is 3D", "d")
                                    break
                            if not while_situation:
                                custom_log("envato_download_file: 404 error page has happened for: " + str(scrap_then_download_file),
                                           "d")
                                scrap_then_download_file.is_acceptable_file = False
                                scrap_then_download_file.in_progress = False
                                scrap_then_download_file.failed_repeat = 10
                                scrap_then_download_file.save()
                                continue

                            if categories_section == '3D':
                                number_of_try_to_pick_psd_btn = 0
                                while_situation = True
                                while True:
                                    try:
                                        custom_log("envato_download_file: check for psd btn", "d")
                                        WebDriverWait(driver, 15).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, 'GK9O2uz3')))
                                        custom_log("envato_download_file: psd btn has showed up", "d")
                                        break
                                    except Exception as e:
                                        try:
                                            download_limit_warning = driver.page_source
                                            if str(download_limit_warning).find('Fair Use Warning') != -1:
                                                envato_settings = get_envato_account()
                                                envato_settings.is_account_active = False
                                                envato_settings.envato_account_description = "fair usage policy. for more information visit elements.envato.com"
                                                envato_settings.save()
                                                scrap_then_download_file.is_acceptable_file = True
                                                scrap_then_download_file.in_progress = False
                                                scrap_then_download_file.save()
                                                custom_log(
                                                    f"fair usage policy. for more information visit elements.envato.com. time: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}",
                                                    "d")
                                                return
                                        except:
                                            pass
                                        custom_log(
                                            "envato_download_file: failed to find psd btn", "d")
                                        number_of_try_to_pick_psd_btn += 1
                                        time.sleep(5)
                                    if number_of_try_to_pick_psd_btn == 3:
                                        driver.quit()
                                        custom_log(
                                            "envato_download_file: after 3 times of reload, failed to find psd btn",
                                            "d")
                                        while_situation = False
                                        break
                                if not while_situation:
                                    custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file),
                                               "d")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.save()
                                    continue
                                psd_btn_container = driver.find_element(By.CLASS_NAME, 'GK9O2uz3')
                                psd_btn = psd_btn_container.find_elements(By.CLASS_NAME, 'JzJMtdiR')[1]
                                psd_btn.click()
                                custom_log("envato_download_file: psd_btn has been clicked", "d")
                                time.sleep(1)

                                number_of_try_to_pick_download_this_angle_btn = 0
                                while_situation = True
                                while True:
                                    try:
                                        custom_log("envato_download_file: check for download_this_angle_btn", "d")
                                        WebDriverWait(driver, 60).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'mIe6goMR')))
                                        custom_log("envato_download_file: download_this_angle_btn has showed up", "d")
                                        break
                                    except Exception as e:
                                        custom_log(
                                            "envato_download_file: failed to find download_this_angle_btn", "d")
                                        number_of_try_to_pick_download_this_angle_btn += 1
                                        time.sleep(5)
                                    if number_of_try_to_pick_download_this_angle_btn == 3:
                                        driver.quit()
                                        custom_log(
                                            "envato_download_file: after 3 times of reload, failed to find download_this_angle_btn",
                                            "d")
                                        while_situation = False
                                        break
                                if not while_situation:
                                    custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file),
                                               "d")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.save()
                                    continue
                                download_this_angle_btn = driver.find_element(By.CLASS_NAME, 'mIe6goMR')
                                download_this_angle_btn.click()
                                custom_log("envato_download_file: download_this_angle_btn has been clicked", "d")
                                time.sleep(1)

                                number_of_try_to_pick_download_without_license_btn = 0
                                while_situation = True
                                while True:
                                    try:
                                        custom_log("envato_download_file: check for download_without_license_btn", "d")
                                        WebDriverWait(driver, 60).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'l0Q2UI85')))
                                        custom_log("envato_download_file: download_without_license_btn has showed up",
                                                   "d")
                                        break
                                    except Exception as e:
                                        custom_log(
                                            "envato_download_file: failed to find download_without_license_btn", "d")
                                        number_of_try_to_pick_download_without_license_btn += 1
                                        time.sleep(5)
                                    if number_of_try_to_pick_download_without_license_btn == 3:
                                        driver.quit()
                                        custom_log(
                                            "envato_download_file: after 3 times of reload, failed to find download_without_license_btn",
                                            "d")
                                        while_situation = False
                                        break
                                if not while_situation:
                                    custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file),
                                               "d")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.save()
                                    continue
                                download_without_license_btn = driver.find_element(By.CLASS_NAME, 'l0Q2UI85')
                                download_without_license_btn.click()
                                custom_log("envato_download_file: download_without_license_btn has been clicked", "d")
                                time.sleep(1)
                            else:
                                number_of_checking_download_btn_visibility = 0
                                while_situation = True
                                while True:
                                    try:
                                        custom_log("envato_download_file: check for download btn", "d")
                                        WebDriverWait(driver, 60).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'igMtSiA8')))
                                        custom_log("envato_download_file: download btn has showed up", "d")
                                        break
                                    except Exception as e:
                                        custom_log(
                                            "envato_download_file: failed to find download btn", "d")
                                        number_of_checking_download_btn_visibility += 1
                                        time.sleep(5)
                                    if number_of_checking_download_btn_visibility == 3:
                                        driver.quit()
                                        custom_log(
                                            "envato_download_file: after 3 times of reload, failed to find download btn",
                                            "d")
                                        while_situation = False
                                        break
                                if not while_situation:
                                    custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file),
                                               "d")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.save()
                                    continue
                                download_btn = driver.find_element(By.CLASS_NAME, 'igMtSiA8')
                                download_btn.click()
                                time.sleep(1)
                                custom_log("envato_download_file: download_btn has been clicked", "d")

                                number_of_checking_download_without_license_btn_visibility = 0
                                while_situation = True
                                while True:
                                    try:
                                        custom_log("envato_download_file: check for download without license btn", "d")
                                        WebDriverWait(driver, 60).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'l0Q2UI85')))
                                        custom_log("envato_download_file: without license btn btn has showed up", "d")
                                        break
                                    except Exception as e:
                                        try:
                                            download_limit_warning = driver.page_source
                                            if str(download_limit_warning).find('Fair Use Warning') != -1:
                                                envato_settings = get_envato_account()
                                                envato_settings.is_account_active = False
                                                envato_settings.envato_account_description = "fair usage policy. for more information visit elements.envato.com"
                                                envato_settings.save()
                                                scrap_then_download_file.is_acceptable_file = True
                                                scrap_then_download_file.in_progress = False
                                                scrap_then_download_file.save()
                                                custom_log(
                                                    f"fair usage policy. for more information visit elements.envato.com. time: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}",
                                                    "d")
                                                return
                                        except:
                                            pass
                                        custom_log(
                                            "envato_download_file: failed to find without license btn btn", "d")
                                        number_of_checking_download_without_license_btn_visibility += 1
                                        time.sleep(5)
                                    if number_of_checking_download_without_license_btn_visibility == 3:
                                        driver.quit()
                                        custom_log(
                                            "envato_download_file: after 3 times of reload, failed to find without license btn btn",
                                            "d")
                                        while_situation = False
                                        break
                                if not while_situation:
                                    custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file),
                                               "d")
                                    scrap_then_download_file.is_acceptable_file = False
                                    scrap_then_download_file.in_progress = False
                                    scrap_then_download_file.save()
                                    continue
                                download_without_license_btn = driver.find_element(By.CLASS_NAME, 'l0Q2UI85')
                                download_without_license_btn.click()
                                custom_log("envato_download_file: download_without_license_btn has been clicked", "d")
                                time.sleep(1)
                            driver.switch_to.new_window(f'tab_download_{i}')
                            driver.get('chrome://downloads')

                            chrome_downloads_page_visibility = 0
                            while_situation = True
                            while True:
                                try:
                                    custom_log("envato_download_file: check for chrome downloads page", "d")
                                    WebDriverWait(driver, 15).until(
                                        EC.visibility_of_element_located((By.XPATH,
                                                                          '/html/body/downloads-manager')))
                                    custom_log("envato_download_file: chrome downloads has showed up", "d")
                                    break
                                except Exception as e:
                                    custom_log(
                                        "envato_download_file: failed to find chrome downloads page. err: " + str(e),
                                        "d")
                                    chrome_downloads_page_visibility += 1
                                if chrome_downloads_page_visibility == 3:
                                    driver.quit()
                                    custom_log(
                                        "envato_download_file: after 3 times of reload, failed chrome downloads page",
                                        "d")
                                    while_situation = False
                                    break
                            if not while_situation:
                                custom_log("envato_download_file: failed to download file: " + str(scrap_then_download_file), "d")
                                scrap_then_download_file.is_acceptable_file = False
                                scrap_then_download_file.in_progress = False
                                scrap_then_download_file.save()
                                continue
                            custom_log("envato_download_file: tab title is: " + str(driver.title), "d")
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
                                raise
                        except Exception as e:
                            custom_log("envato_download_file: failed to download file: " + str(
                                scrap_then_download_file) + " try/except-> err: " + str(e), "d")
                            scrap_then_download_file.download_percentage = 0
                            scrap_then_download_file.is_acceptable_file = False
                            scrap_then_download_file.in_progress = False
                            scrap_then_download_file.save()
                        custom_log("envato_download_file: finish a list.", "d")
                        return True
                    except Exception as e:
                        number_of_get_accept_cookie_btn_tries += 1
                        if number_of_get_accept_cookie_btn_tries == 3:
                            custom_log(
                                "envato_download_file: after 3 times of reload, download has been failed. err: " + str(e),
                                "d")
                            driver.quit()
                            scrap_then_download_file.download_percentage = 0
                            scrap_then_download_file.is_acceptable_file = True
                            scrap_then_download_file.in_progress = False
                            scrap_then_download_file.save()
                            return False
            except NoSuchElementException as e:
                custom_log('envato_download_file webdriver exception. err: ' + str(e), "d")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
                time.sleep(get_time_sleep())
            except WebDriverException as e:
                custom_log('envato_download_file webdriver exception. err: ' + str(e), "d")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
                time.sleep(get_time_sleep())
            except ConnectionError as e:
                custom_log('envato_download_file webdriver exception. err: ' + str(e), "d")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
                time.sleep(get_time_sleep())
            except Exception as e:
                custom_log('envato_download_file webdriver exception. err: ' + str(e), "d")
                custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
                time.sleep(get_time_sleep())
            webdriver_problem_number_of_reloading += 1
            if webdriver_problem_number_of_reloading == 3:
                driver.quit()
                custom_log(
                    "envato_download_file: webdriver exception caused download to be aborted", 'd')
                scrap_then_download_file.download_percentage = 0
                scrap_then_download_file.is_acceptable_file = True
                scrap_then_download_file.in_progress = False
                scrap_then_download_file.save()
                return False
