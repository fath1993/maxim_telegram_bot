import os
import pickle
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import jdatetime
import tkinter as tk



def get_base_path():
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return path


def get_executable_path():
    executable_path = f'{get_base_path()}\\chromedriver\\chromedriver.exe'
    return executable_path


def folder_maker():
    try:
        os.mkdir(f'{get_base_path()}\\cookie')
    except:
        pass


def motion_array_sign():
    MotionArraySignThread().start()


class MotionArraySignThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            update_description('...بررسی فولدر ها')
            time.sleep(1)
            folder_maker()
            update_description('...اجرای عملیات ورود برای موشن ارای')
            time.sleep(1)
            update_description('برای اجرای عملیات ورود \n 120 \n  ثانیه فرصت دارید \n لطفا در صفحه اصلی باقی بمانید')
            time.sleep(5)
            options = Options()
            options.add_argument("--window-size=1920,1200")
            prefs = {"download.default_directory": f"{get_base_path()}\\cookie"}
            options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(executable_path=get_executable_path(), options=options)
            driver.get("https://motionarray.com/account/login/")
            current_time = 0
            remain_time = 120
            while True:
                time.sleep(1)
                current_time += 1
                remain_time -= 1
                update_description(f'زمان باقی مانده \n {remain_time}\n ثانیه')
                driver.execute_script("return document.readyState")
                if current_time == 120:
                    break
            cookie_file_path = f'{get_base_path()}\\cookie\\motion_array_cookies_{jdatetime.datetime.now().strftime("%Y_%m_%d_%H_%M")}.pkl'
            pickle.dump(driver.get_cookies(), open(cookie_file_path, "wb"))
            driver.quit()
            update_description('.فایل کوکی موشن ارای ذخیره گردید')
        except Exception as e:
            update_description(f'بسته شد با خطای \n {e} \n لطفا مجددا عملیات را انتخاب نمایید')


def envato_sign():
    EnvatoSignThread().start()


class EnvatoSignThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        try:
            update_description('...بررسی فولدر ها')
            time.sleep(1)
            folder_maker()
            update_description('...اجرای عملیات ورود برای انواتو')
            time.sleep(1)
            update_description('برای اجرای عملیات ورود \n 120 \n  ثانیه فرصت دارید \n لطفا در صفحه اصلی باقی بمانید')
            time.sleep(5)
            folder_maker()
            options = Options()
            options.add_argument("--window-size=1920,1200")
            prefs = {"download.default_directory": f"{get_base_path()}\\cookie"}
            options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(executable_path=get_executable_path(), options=options)
            driver.get("https://elements.envato.com/sign-in")
            current_time = 0
            remain_time = 120
            while True:
                time.sleep(1)
                current_time += 1
                remain_time -= 1
                update_description(f'زمان باقی مانده \n {remain_time}\n ثانیه')
                driver.execute_script("return document.readyState")
                if current_time == 120:
                    break
            cookie_file_path = f'{get_base_path()}\\cookie\\envato_cookies_{jdatetime.datetime.now().strftime("%Y_%m_%d_%H_%M")}.pkl'
            pickle.dump(driver.get_cookies(), open(cookie_file_path, "wb"))
            driver.quit()
            update_description('.فایل کوکی انواتو ذخیره گردید')
        except Exception as e:
            update_description(f'بسته شد با خطای \n {e} \n لطفا مجددا عملیات را انتخاب نمایید')


def update_description(message):
    global description_text
    description_text.delete("1.0", tk.END)
    description_text.tag_configure("rtl", justify="right")
    description_text.insert(tk.END, message, 'rtl')


print(f'path: {get_base_path()}')
print(f'executable_path: {get_executable_path()}')

root = tk.Tk()
root.title('Sign Application')

window_width = 300
window_height = 400

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

description_frame_1 = tk.Frame(root, padx=5)
description_frame_1.pack(side="bottom", fill="x")
description_label = tk.Label(description_frame_1, text="MaximShop - @2023 All right reserved", font=("Arial", 10))
description_label.pack(pady=(0, 5), side="bottom", anchor="w", fill="x", padx=5)

button_frame_1 = tk.Frame(root, padx=10, pady=5, bg="lightblue")
button_frame_1.pack(side="bottom", fill="x")
button1 = tk.Button(button_frame_1, text="Envato", command=envato_sign, height=1, bg="gray", fg="white",
                    font=("Helvetica", 14, "bold"))
button1.pack(side="left", expand=True, fill="x", padx=5, pady=10)

button_frame_2 = tk.Frame(root, padx=10, pady=5, bg="lightblue")
button_frame_2.pack(side="bottom", fill="x")
button2 = tk.Button(button_frame_2, text="Motion Array", command=motion_array_sign, height=1, bg="gray", fg="white",
                    font=("Helvetica", 14, "bold"))
button2.pack(side="left", expand=True, fill="x", padx=5)

description_frame_2 = tk.Frame(root, padx=15, pady=15, bg="lightblue")
description_frame_2.pack(fill="y")
description_text = tk.Text(description_frame_2, wrap=tk.WORD, font=("Tahoma", 10))
description_text_start = ''
description_text_start += 'خوش آمدید'
description_text_start += '\n'
description_text_start += 'توسط این ابزار امکان لاگین به اکانت های خود را خواهید داشت'
description_text_start += '\n'
description_text_start += 'کوکی های ذخیره شده را در وبسرویس استفاده نمایید'
description_text_start += '\n'
description_text.tag_configure("rtl", justify="right")
description_text.insert(tk.END, description_text_start, 'rtl')
description_text.pack(anchor="s")

root.mainloop()



