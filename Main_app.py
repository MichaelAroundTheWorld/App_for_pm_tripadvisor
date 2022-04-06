from tkinter import *
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
import urllib.request , urllib.error, urllib.parse
from telnetlib import EC
from tkinter.filedialog import askdirectory


from selenium import webdriver
import io
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pathlib
import time
import os
from bs4 import BeautifulSoup
import re
import pandas as pd


root = Tk()
root.title('App for scraping pages from Tripadvisor')
root.geometry('400x200')

canvas = Canvas(root, width=400, height=200)

label_url = Label(root, text='URL винодельни')
label_url.place(x=10, y=10)
entry_url = Entry(root)
entry_url.place(x=10, y=40)

def create_window():
    root = Tk().winfo_toplevel()
    root.title('Название файла')
    label_name_file_csv = Label(root, text='Введите название файла')
    label_name_file_csv.place(x=10, y=10)

    entry_name_of_csv_file = Entry(root)
    entry_name_of_csv_file.place(x=10, y=40)

    btn_ok = Button(root, text='Преобразовать файлы')
    btn_ok.place(x=10, y=60)
    btn_ok.bind('<Button-1>', lambda event: ParsePages(entry_name_of_csv_file.get()))


def well_done_window():
    root = Tk().winfo_toplevel()
    root.title('Готово')
    label_name_file_csv = Label(root, text='Страницы успешно скачаны')
    label_name_file_csv.place(x=20, y=20)

def GetPages(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--enable-javascript")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")

    # url = 'https://www.tripadvisor.co.uk/Restaurants-g186402-Birmingham_West_Midlands_England.html'
    driver = webdriver.Chrome("driver/chromedriver_win32 (4)/chromedriver.exe", options=options)
    driver.get(url)
    output = askdirectory()

    page = 0
    restraunt_num = 0
    resume = True
    while resume:
        try:
            WebDriverWait(driver, 20).until(
                ec.visibility_of_element_located((By.XPATH, './/a[contains(@class, "bHGqj Cj b")]')))
        except TimeoutException:
            print('Cannot locate producers table')
            continue

        time.sleep(20)
        restraunts = driver.find_elements_by_class_name('bHGqj')
        for restraunt in restraunts:

            restraunt_num += 1
            # if pathlib.Path('{}/{}.html'.format(output, str(restraunt_num))).exists():
            #     print('File {} already exists, continue'.format(restraunt_num))
            #     continue

            ActionChains(driver).key_down(Keys.CONTROL).click(restraunt).key_up(Keys.CONTROL).perform()
            try:
                driver.switch_to.window(driver.window_handles[1])
            except IndexError:
                print('Index error on vine {}'.format(restraunt_num))
                continue

            # driver.switch_to.window(driver.window_handles[1])

            try:
                WebDriverWait(driver, 20).until(
                    ec.visibility_of_element_located((By.XPATH, './/div[contains(@class, "page ")]')))
            except TimeoutException:
                print('Cannot locate vine card')
                continue
            time.sleep(0.1)

            with io.open(output + '/' + str(restraunt_num) + ".html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                f.close()
            print('Saved vine {}'.format(str(restraunt_num)))
            time.sleep(0.5)

            # restraunt_num += 1
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        try:
            time.sleep(5)
            current_button = driver.find_elements_by_xpath(
                './/a[contains(@class, "nav next rndBtn ui_button primary taLnk")]'.format(page)).pop()
            # driver.execute_script("arguments[0].scrollIntoView();", current_button)
            # driver.implicitly_wait(2)
            ActionChains(driver).move_to_element(current_button).perform()
            ActionChains(driver).click(current_button).perform()
            print('Next page button clicked')
        except IndexError:
            resume = False

    print('Done')
    driver.quit()
    well_done_window()

def ParsePages(entry_name_of_csv_file):
    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    bd = pd.DataFrame(columns=['name', 'address', 'e-mail', 'site', 'telephone'])

    dir_name = askdirectory()

    for root, dirs, files in os.walk(dir_name):
        iter = 0
        files.sort(key=natural_keys)
        for name in files:
            fullname = os.path.join(root, name)
            if os.path.isfile(fullname) and (
                    re.search(r'.html', fullname)):
                print(fullname)
                with open(fullname, encoding='utf-8', errors='ignore') as fp:
                    iter += 1
                    soup = BeautifulSoup(fp, "html5lib")

                    name = None
                    if soup.find('h1', {'class': 'fHibz'}):
                        try:
                            name = soup.find('h1', {'class': 'fHibz'}).text
                            print(name)
                        except:
                            print('No name')

                    address = None
                    if soup.find('span', {'class': 'dyNBF'}):
                        try:
                            geo_icon = soup.find('span', {'class': 'dyNBF'})
                            address1 = geo_icon.find_parent('span')
                            address = address1.findChild('a', {'class': 'fhGHT'}).text
                        #address = soup.find('a', {'class': 'fhGHT'}).text
                            print(address)
                        except:
                            print('No adress')

                    site = None
                    if soup.find('a', {'class': 'dOGcA Ci Wc _S C fhGHT'}):
                        try:
                            site = soup.find('a', {'class': 'dOGcA Ci Wc _S C fhGHT'})
                            site = site.get('href')
                    #if soup.find_all('a', {'class': '_2wKz--mA _27M8V6YV'}).__len__() > 1:
                     #   site = soup.find_all('a', {'class': '_2wKz--mA _27M8V6YV'})[1]
                      #  site = site.get('href')
                            print(site)
                        except:
                            print('No web-site')

                    email = None
                    if soup.find('span', {'class': 'ui_icon email bPFFU'}):
                        try:
                            email1 = soup.find('span', {'class': 'ui_icon email bPFFU'})
                            email = email1.find_parent('a').get('href')
                            print(email)
                        except:
                            print('No email')

                    telephone = None
                    if soup.find('a', {'class': 'eKwUx'}):
                        telephone_parent = soup.find('span', {'class': 'fhGHT'})
                        try:
                            telephone = telephone_parent.findChild('a', {'class': 'iPqaD _F G- ddFHE eKwUx'}).get('href')
                            print(telephone)
                        except:
                            print('No telephone number')

                    bd = bd.append(
                        {'name': name, 'address': address, 'e_mail': email, 'site': site, 'telephone': telephone},
                        ignore_index=True)
            bd.to_csv(entry_name_of_csv_file + '.csv', sep=';')
    bd.to_csv(entry_name_of_csv_file + '.csv', sep=';')


btn_download = Button(root, text='Скачать страницы')
btn_download.bind('<Button-1>', lambda event: GetPages(entry_url.get()))
btn_download.place(x=10, y=100)

btn_parse = Button(root, text='Загрузить информацию в csv файл')
btn_parse.bind('<Button-1>', lambda event: create_window())
btn_parse.place(x=10, y= 140)


canvas.pack()

root.mainloop()