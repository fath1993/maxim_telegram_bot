import os
import pickle
import threading
import aria2p
import time
import http.client
import jdatetime
import paramiko
from custom_logs.models import custom_log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from envato.models import get_envato_config_settings, EnvatoAccount, get_envato_account
from maxim_telegram_bot.settings import CHROME_DRIVER_PATH, BASE_DIR, DOWNLOAD_FOLDER
from utilities.slug_generator import name_cleaner

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}


# ------------ Start Scraper functions -------------------
def get_time_sleep():
    time_sleep = get_envato_config_settings().sleep_time
    custom_log("sleep time: " + str(time_sleep), "d")
    return int(time_sleep)


def get_envato_cookie(envato_account):
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
                custom_log("get_envato_cookie: starting page load", "d")
                driver.get("https://elements.envato.com/sign-in")
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                check_chrome_connection_status(driver)
                custom_log("get_envato_cookie: check for accept cookie button", "d")
                try:
                    WebDriverWait(driver, 60).until(
                        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept")))
                    accept_cookie_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
                    accept_cookie_button.click()

                    number_of_sign_in_tries = 0
                    try:
                        WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.ID, "sso-forms__submit")))
                        username_input = driver.find_element(By.ID, "username")
                        password_input = driver.find_element(By.ID, "password")
                        sign_in_btn = driver.find_element(By.ID, "sso-forms__submit")
                        username_input.send_keys(envato_account.envato_user)
                        password_input.send_keys(envato_account.envato_pass)
                        sign_in_btn.click()
                        time.sleep(30)
                        custom_log("get_envato_cookie: waiting for 30 seconds after click sign-in btn", "d")
                        cookie_file_path = BASE_DIR / f'media/envato/cookies/cookies-{envato_account.envato_user}.pkl'
                        pickle.dump(driver.get_cookies(), open(cookie_file_path, "wb"))
                        envato_account.envato_cookie.name = str(
                            f'envato/cookies/cookies-{envato_account.envato_user}.pkl')
                        envato_account.save()
                        driver.quit()
                        custom_log(
                            'get_envato_cookie: sign-in to Envato has been successful. The cookie has been saved', "d")
                        return True
                    except Exception as e:
                        custom_log(
                            "get_envato_cookie: sign-in problem, we cant sign to Envato site using the provided credential. err: " + str(
                                e), "d")
                    number_of_sign_in_tries += 1
                    if number_of_sign_in_tries == 3:
                        driver.quit()
                        custom_log(
                            "get_envato_cookie: after 3 times of reload, we still cant sign to Envato site using the provided credential, sign-in function has been failed",
                            "d")
                        settings = get_envato_config_settings()
                        settings.login_status = False
                        settings.save()
                        return False
                except Exception as e:
                    custom_log("get_envato_cookie: we cant find accept cookie button. err: " + str(e), "d")
                number_of_get_accept_cookie_btn_tries += 1
                if number_of_get_accept_cookie_btn_tries == 3:
                    driver.quit()
                    custom_log(
                        "get_envato_cookie: after 3 times of reload, we cant find accept cookie button, sign-in function has been failed",
                        "d")
                    driver.quit()
                    settings = get_envato_config_settings()
                    settings.login_status = False
                    settings.save()
                    return False
        except NoSuchElementException as e:
            custom_log('get_envato_cookie webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except WebDriverException as e:
            custom_log('get_envato_cookie webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            custom_log('get_envato_cookie webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except Exception as e:
            custom_log('get_envato_cookie webdriver exception. err: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            custom_log("get_envato_cookie: webdriver exception caused get cookie to be aborted", 'd')
            settings = get_envato_config_settings()
            settings.login_status = False
            settings.save()
            return False


def check_if_sign_in_is_needed(envato_account):
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


def envato_auth(envato_account):
    EnvatoSignInThread(envato_account).start()


class EnvatoSignInThread(threading.Thread):
    def __init__(self, envato_account):
        super().__init__()
        self.envato_account = envato_account

    def run(self):
        if check_if_sign_in_is_needed(self.envato_account):
            get_envato_cookie(self.envato_account)


def envato_auth_all():
    EnvatoSignInAllThread().start()


class EnvatoSignInAllThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
        for envato_account in envato_accounts:
            if check_if_sign_in_is_needed(envato_account):
                time.sleep(5)
                get_envato_cookie(envato_account)
            time.sleep(5)


def envato_check_auth():
    EnvatoCheckAuthThread().start()


class EnvatoCheckAuthThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
        for envato_account in envato_accounts:
            check_if_sign_in_is_needed(envato_account)


def envato_download_file(envato_files, account_to_use):
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--headless=new")
    # options.add_argument("--disable-web-security")
    # options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--ignore-certificate-errors")
    envato_files_path = BASE_DIR / 'media/files/'
    prefs = {"download.default_directory": f"{envato_files_path}"}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, desired_capabilities=d)
    webdriver_problem_number_of_reloading = 0
    direct_download_list = []
    scrap_then_download_list = []
    for envato_file in envato_files:
        if envato_file.file_storage_link:
            direct_download_list.append(envato_file)
        else:
            scrap_then_download_list.append(envato_file)


    if len(direct_download_list) != 0:
        # part 1
        custom_log("envato_download_file: start downloading the files", "d")
        for direct_download_file in direct_download_list:
            number_of_try = 0
            while True:
                try:
                    custom_log(f"envato_download_file: start downloading the file: {direct_download_file.unique_code}")
                    original_name = name_cleaner(direct_download_file.file_storage_link)
                    file_name, file_extension = os.path.splitext(original_name)
                    if len(file_extension) > 6:
                        file_extension = '.zip'
                    new_name = f'{direct_download_file.unique_code}{file_extension}'
                    download_file_with_aria2_download_manager(direct_download_file, new_name, direct_download_file.file_storage_link)
                    break
                except Exception as e:
                    custom_log(f"envato_download_file: failed to download file: {direct_download_file.unique_code} try/except-> err: " + str(e), "d")
                    time.sleep(1)
                    number_of_try += 1
                if number_of_try == 3:
                    custom_log(f"envato_download_file: after 3 time of reloads failed to download file: {direct_download_file}")
                    direct_download_file.download_percentage = 0
                    direct_download_file.is_acceptable_file = False
                    direct_download_file.in_progress = False
                    direct_download_file.save()
                    break

    if len(scrap_then_download_list) != 0:
        # part 2
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
                        for envato_file in scrap_then_download_list:
                            try:
                                custom_log("envato_download_file: start downloading the file: " + str(envato_file), "d")
                                driver.switch_to.new_window(f'tab_{i}')
                                driver.get(envato_file.page_link)
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
                                    custom_log("envato_download_file: 404 error page has happened for: " + str(envato_file),
                                               "d")
                                    envato_file.is_acceptable_file = False
                                    envato_file.in_progress = False
                                    envato_file.failed_repeat = 10
                                    envato_file.save()
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
                                                    envato_file.is_acceptable_file = True
                                                    envato_file.in_progress = False
                                                    envato_file.save()
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
                                        custom_log("envato_download_file: failed to download file: " + str(envato_file),
                                                   "d")
                                        envato_file.is_acceptable_file = False
                                        envato_file.in_progress = False
                                        envato_file.save()
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
                                        custom_log("envato_download_file: failed to download file: " + str(envato_file),
                                                   "d")
                                        envato_file.is_acceptable_file = False
                                        envato_file.in_progress = False
                                        envato_file.save()
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
                                        custom_log("envato_download_file: failed to download file: " + str(envato_file),
                                                   "d")
                                        envato_file.is_acceptable_file = False
                                        envato_file.in_progress = False
                                        envato_file.save()
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
                                        custom_log("envato_download_file: failed to download file: " + str(envato_file),
                                                   "d")
                                        envato_file.is_acceptable_file = False
                                        envato_file.in_progress = False
                                        envato_file.save()
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
                                                    envato_file.is_acceptable_file = True
                                                    envato_file.in_progress = False
                                                    envato_file.save()
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
                                        custom_log("envato_download_file: failed to download file: " + str(envato_file),
                                                   "d")
                                        envato_file.is_acceptable_file = False
                                        envato_file.in_progress = False
                                        envato_file.save()
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
                                    custom_log("envato_download_file: failed to download file: " + str(envato_file), "d")
                                    envato_file.is_acceptable_file = False
                                    envato_file.in_progress = False
                                    envato_file.save()
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
                                new_name = f'{envato_file.unique_code}{file_extension}'
                                download_status = download_file_with_aria2_download_manager(envato_file, new_name, url)
                                if not download_status:
                                    raise
                            except Exception as e:
                                custom_log("envato_download_file: failed to download file: " + str(
                                    envato_file) + " try/except-> err: " + str(e), "d")
                                envato_file.download_percentage = 0
                                envato_file.is_acceptable_file = False
                                envato_file.in_progress = False
                                envato_file.save()
                            i += 1
                        custom_log("envato_download_file: finish a list.", "d")
                        return True
                    except Exception as e:
                        number_of_get_accept_cookie_btn_tries += 1
                        if number_of_get_accept_cookie_btn_tries == 3:
                            custom_log(
                                "envato_download_file: after 3 times of reload, download has been failed. err: " + str(e),
                                "d")
                            driver.quit()
                            for envato_file in envato_files:
                                envato_file.download_percentage = 0
                                envato_file.is_acceptable_file = True
                                envato_file.in_progress = False
                                envato_file.save()
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
                for envato_file in envato_files:
                    envato_file.download_percentage = 0
                    envato_file.is_acceptable_file = True
                    envato_file.in_progress = False
                    envato_file.save()
                return False


# ------------ End Scraper functions -------------------


# ------------ Start Calculator Functions -------------------

# ------------ End Calculator Functions -------------------


# ------------ Start Helper Functions -------------------
def envato_sign_in_page():
    url = "https://elements.envato.com/sign-in"
    return url


def check_chrome_connection_status(driver_object):
    for entry in driver_object.get_log('performance'):
        if str(entry['message']).find('"errorText":"net::ERR_TIMED_OUT"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, "d")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_NO_SUPPORTED_PROXIES"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, "d")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_INTERNET_DISCONNECTED"') != -1:
            errorText = "net::ERR_INTERNET_DISCONNECTED"
            custom_log(errorText, "d")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_TIMED_OUT"') != -1:
            errorText = "net::ERR_CONNECTION_TIMED_OUT"
            custom_log(errorText, "d")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_RESET"') != -1:
            errorText = "net::ERR_CONNECTION_RESET"
            custom_log(errorText, "d")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_REFUSED"') != -1:
            errorText = "net::ERR_CONNECTION_REFUSED"
            custom_log(errorText, "d")
            return ConnectionError


# ------------ End Helper Functions -------------------


def download_file_with_aria2_download_manager(envato_file, file_name: str, url: str):
    envato_file.download_percentage = 0
    envato_file.save()
    time.sleep(1)
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    # Specify custom options as a dictionary
    custom_options = {
        'user-agent': 'Chrome/115.0.0.0',
        'out': f'{file_name}',
    }
    if str(url).find('storagebox.de') != -1:
        webdav_host = "u379344.your-storagebox.de"
        webdav_port = 443
        webdav_path = str(url).split('storagebox.de')[-1]
        webdav_username = "u379344"
        webdav_password = "LKZMfmz2xrtzUhXr"

        # Connect to the WebDAV server
        connection = http.client.HTTPConnection(webdav_host, webdav_port)
        time.sleep(1)
        # Specify the URL with username and password
        url = f"https://{webdav_username}:{webdav_password}@{webdav_host}:{webdav_port}{webdav_path}"
    else:
        pass
    download = aria2.add_uris([f"{url}"], options=custom_options)

    attempt = 0
    while not download.is_complete:
        try:
            download.update()
            if download.status == 'error':
                download.pause()
                envato_file.download_percentage = int(download.progress)
                envato_file.is_acceptable_file = True
                envato_file.in_progress = False
                envato_file.save()
                return print(f'result: download has been failed')
            speed = download.download_speed
            completed_length = download.completed_length
            total_length = download.total_length
            percentage = download.progress
            print(f"download: {download.status}")
            print(f"Download Speed: {speed}")
            print(f"Downloaded: {completed_length}")
            print(f"Remaining: {total_length}")
            print(f"Completion Percentage: {percentage}%")
            print("------------")
            attempt = 0
            if int(percentage) != 100:
                envato_file.download_percentage = int(percentage)
                envato_file.save()
                time.sleep(1)
        except Exception as e:
            attempt += 1
            custom_log(f'download_file_with_aria2_download_manager. try/except:> err: {str(e)}')
            if attempt == 10:
                envato_file.download_percentage = 0
                envato_file.is_acceptable_file = True
                envato_file.in_progress = False
                envato_file.file_storage_link = None
                envato_file.save()
                return False
    if download.is_complete:
        try:
            envato_file.download_percentage = 100
            envato_file.is_acceptable_file = True
            envato_file.in_progress = False
            envato_file.file.name = f'/envato/files/{file_name}'
            envato_file.save()
            if str(url).find('storagebox.de') == -1:
                UploadManager(envato_file).start()
            custom_log(
                f'download_file_with_aria2_download_manager. result: download file: {envato_file.unique_code} has been finished successfully')
            return True
        except Exception as e:
            custom_log(f'download_file_with_aria2_download_manager. try/except:> err: {str(e)}')
            return False
    else:
        custom_log(f'download_file_with_aria2_download_manager. download problem')
        return False



def create_remote_directory(sftp, remote_filepath):
    remote_path, _ = os.path.split(remote_filepath)
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)


def are_files_similar(sftp, remote_filepath, local_filepath):
    try:
        remote_file_size = sftp.stat(remote_filepath).st_size

        local_file_size = os.path.getsize(local_filepath)
        if remote_file_size != local_file_size:
            print(f"File sizes differ. Deleting remote file: {remote_filepath}")
            sftp.remove(remote_filepath)
            return False
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking file similarity: {e}")
        return False


def upload_file_to_remote(local_filepath, remote_filepath, ssh_host, ssh_port, ssh_username, ssh_password):
    try:
        with paramiko.Transport((ssh_host, ssh_port)) as transport:
            transport.connect(username=ssh_username, password=ssh_password)
            with paramiko.SFTPClient.from_transport(transport, window_size=10) as sftp:
                create_remote_directory(sftp, remote_filepath)
                if are_files_similar(sftp, remote_filepath, local_filepath):
                    print(f"File '{local_filepath}' already exists on the remote server with the same content.")
                    return remote_filepath

                sftp.put(local_filepath, remote_filepath)
                print(f"File '{local_filepath}' uploaded to '{remote_filepath}' successfully.")
                return remote_filepath

    except Exception as e:
        print(f"Error uploading or checking file: {e}")
        return None


class UploadManager(threading.Thread):
    def __init__(self, file):
        super().__init__()
        self.file = file

    def run(self):
        number_of_try = 0
        while True:
            try:
                custom_log(f"start ssh upload for file: {self.file.file.name} to server.")
                local_filepath = f'/var/www/maxim_telegram_bot/{self.file.file.url}'
                file_name, file_extension = os.path.splitext(self.file.file.url)
                remote_filepath = f"/{DOWNLOAD_FOLDER}/{self.file.file_type}/{self.file.unique_code}{file_extension}"
                ssh_host = 'u379344.your-storagebox.de'
                ssh_port = 22
                ssh_username = 'u379344'
                ssh_password = 'LKZMfmz2xrtzUhXr'
                upload_file_to_remote(local_filepath, remote_filepath, ssh_host, ssh_port, ssh_username, ssh_password)
                self.file.file_storage_link = ssh_host + remote_filepath
                self.file.save()
                return custom_log(f"{self.file.file.name} uploaded successfully to SSH server.")
            except Exception as e:
                custom_log(f"problem happens during upload {self.file.file.name} to server. err: {e}")
                number_of_try += 1
                time.sleep(10)
            if number_of_try == 3:
                return custom_log(f"after 3 times reload, {self.file.file.name} didnt upload to server successfully.")
