import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from threading import Thread
import time
import datetime
import json

from process_captcha import ProcessCaptcha

LATER_SECS = 259200

class Script:
    def __init__(self):
        self.threads = []
        self.running_states = []
        self.main()

    def main(self):
        saat = datetime.datetime.strptime(input("Time (XX XX): "), "%H %M").time()
        sm = input("Single or Multi? (S/M): ").upper()
        while True:
            posin = input("Hangi Tesis: ").lower()
            date = datetime.datetime.combine(time=saat, date=datetime.datetime.now().date()).timestamp()
            saha_posses = input("Enter the positions of the courts (Divide by '/'): ").split('/')
            for saha in saha_posses:
                leng = len(self.threads)
                self.threads.append(Thread(target=self.startScript, args=(int(saha), posin, date, leng+1), name=f"{posin}/{saha}"))
            if sm == "S":
                break
            else:
                ex = input("Type X to finish: ").upper()
                if ex == "X":
                    break
        self.running_states = [True for _ in range(len(self.threads))]
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    def startScript(self, saha, posin, date, thread_num):
        with open("assets/login_info.json", "r") as f:
            data = json.load(f)
        while datetime.datetime.now().timestamp() < (date - 60):
            continue
        TC = data["TC"]
        SIFRE = data["Sifre"]
        driver = webdriver.Chrome(service=Service(executable_path="assets/chromedriver.exe"))
        driver.get("https://online.spor.istanbul/uyegiris")
        wait_presence(driver, By.NAME, "txtSifre")
        tc_giris = driver.find_element(By.NAME, "txtTCPasaport")
        tc_giris.send_keys(TC)
        while True:
            if not self.running_states[thread_num - 1]: # killer check
                driver.quit()
                return
            sifre_giris = driver.find_element(By.NAME, "txtSifre")
            giris_button = driver.find_element(By.NAME, "btnGirisYap")
            sifre_giris.send_keys(SIFRE)
            giris_button.click()
            wait_presence(driver, By.XPATH, "/html/body")
            try:
                driver.find_element(By.NAME, "txtSifre")
                continue
            except NoSuchElementException:
                break
        closePopup(driver, True)
        wait_presence(driver, By.ID, "contacttab6")
        rentButton = driver.find_element(By.ID, "contacttab6")
        rentButton.click()
        wait_presence(driver, By.ID, "pageContent_ucUrunArama_lbtnKiralikAra")
        combobox_brans = driver.find_element(By.XPATH, "/html/body/form/section[1]/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/span/span[1]/span")
        combobox_brans.click()
        combobox_brans.send_keys(Keys.ENTER)
        wait_presence(driver, By.ID, "pageContent_ucUrunArama_lbtnKiralikAra")
        times = date + LATER_SECS
        timelater = times + 3600
        tim = datetime.datetime.fromtimestamp(times).strftime("%H:%M")
        timlater = datetime.datetime.fromtimestamp(timelater).strftime("%H:%M")
        strtim = tim + " - " + timlater
        index = self.rentTesis(driver, posin, date, saha, strtim, thread_num)
        if not self.running_states[thread_num - 1]:  # killer check
            driver.quit()
            return
        startline = driver.find_elements(By.CLASS_NAME, "col-md-1")[index]
        parent = startline.find_element(By.XPATH, "div/div[2]")
        starthour = None
        for ele in parent.find_elements(By.TAG_NAME, "div"):
            err = True
            try:
                _ = ele.find_element(By.XPATH, "div/span")
                err = False
            except NoSuchElementException:
                __ = None
            if not err:
                hour = ele.find_element(By.XPATH, "div/span").text
                if hour == strtim:
                    starthour = ele
                    break
        starthour.find_element(By.TAG_NAME, "a").click()
        if not self.running_states[thread_num - 1]:  # killer check
            driver.quit()
            return
        for th in range(thread_num, len(self.threads)):
            self.running_states[th] = True
        alert = driver.switch_to.alert
        alert.accept()
        if not self.running_states[thread_num - 1]:  # killer check
            driver.quit()
            return
        while True:
            wait_presence(driver, By.NAME, "ctl00$pageContent$txtCaptchaText")
            captcha_image = driver.find_element(By.NAME, "ctl00$pageContent$captchaImage")
            captcha_image.screenshot('assets/captcha.png')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", captcha_image)
            captcha = driver.find_element(By.NAME, "ctl00$pageContent$txtCaptchaText")
            captcha.click()
            pc = ProcessCaptcha('captcha', 'optimal_model')
            captcha.send_keys(pc.main())
            if not self.running_states[thread_num - 1]:  # killer check
                driver.quit()
                return
            cart = driver.find_element(By.ID, "pageContent_lbtnSepeteEkle")
            while len(captcha.get_attribute("value")) < 6:
                if not self.running_states[thread_num - 1]:  # killer check
                    driver.quit()
                    return
            cart.click()
            try:
                time.sleep(0.5)
                _ = driver.find_element(By.NAME, "ctl00$pageContent$captchaImage")
            except:
                os.remove('assets/captcha.png')
                break
            os.remove('assets/captcha.png')
            captchax = driver.find_element(By.NAME, "ctl00$pageContent$txtCaptchaText")
            captchax.clear()
        time.sleep(30)

    def rentTesis(self, driver, pos, date, saha, strtim, thread_num):
        if not self.running_states[thread_num - 1]:  # killer check
            driver.quit()
            return
        combobox_tesis = driver.find_element(By.XPATH, "/html/body/form/section[1]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/span/span[1]/span")
        combobox_tesis.click()
        searchbar = driver.find_element(By.CLASS_NAME, "select2-search__field")
        searchbar.send_keys(pos)
        combobox_tesis.send_keys(Keys.ENTER)
        if not self.running_states[thread_num - 1]:  # killer check
            driver.quit()
            return
        wait_presence(driver, By.ID, "pageContent_ucUrunArama_lbtnKiralikAra")
        combobox_salon = driver.find_element(By.XPATH, "/html/body/form/section[1]/div/div/div/div/div/div/div/div[2]/div/div/div[3]/div/div/div/span/span[1]/span")
        combobox_salon.click()
        combobox_salon.send_keys(Keys.DOWN*(saha-1) + Keys.ENTER)
        ara = driver.find_element(By.ID, "pageContent_ucUrunArama_lbtnKiralikAra")
        court_text = driver.find_element(By.XPATH, "/html/body/form/section[1]/div/div/div/div/div/div/div/div[2]/div/div/div[3]/div/div/div/span/span[1]/span/span[1]").text
        while datetime.datetime.now().timestamp() < date-10:
            if not self.running_states[thread_num - 1]:  # killer check
                driver.quit()
                return
            continue
        ara.click()
        wait_presence(driver, By.CLASS_NAME, "col-md-1")
        dat = datetime.datetime.fromtimestamp(date+LATER_SECS).strftime("%d.%m.%Y")
        column = None
        columns = driver.find_elements(By.CLASS_NAME, "col-md-1")
        for i in range(len(columns)):
            col = columns[i]
            if col.text.split("\n")[1] == dat:
                column = ((i+1) if i < 7 else (i+2))
                break
        while True:
            if not self.running_states[thread_num - 1]:  # killer check
                driver.quit()
                return
            wait_presence(driver, By.XPATH, "/html/body/form/section/div[1]/div[1]")
            isPos = False
            par = findCol(driver, column).find_element(By.XPATH, "div/div[2]")
            for x in par.find_elements(By.TAG_NAME, "div"):
                er = True
                try:
                    _ = x.find_element(By.XPATH, "div/span")
                    er = False
                except NoSuchElementException:
                    __ = None
                if not er:
                    if x.find_element(By.XPATH, "div/span").text == strtim:
                        isPos = True
                        break
            if isPos:
                break
            driver.refresh()
            wait_presence(driver, By.XPATH, "/html/body/form/div[3]/div[3]/div[1]/div/div/div/div/div[1]/span[2]/span[1]/span")
            fut = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[3]/div[1]/div/div/div/div/div[1]/span[2]/span[1]/span")
            fut.click()
            driver.find_element(By.XPATH, "/html/body/span/span/span[1]/input").send_keys("futbol" + Keys.ENTER)
            wait_presence(driver, By.XPATH, "/html/body/form/section/div[1]/div[1]")
            tes = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[3]/div[1]/div/div/div/div/div[2]/span[2]/span[1]/span")
            tes.click()
            if not self.running_states[thread_num - 1]:  # killer check
                driver.quit()
                return
            driver.find_element(By.XPATH, "/html/body/span/span/span[1]/input").send_keys(pos + Keys.ENTER)
            wait_presence(driver, By.XPATH, "/html/body/form/section/div[1]/div[1]")
            sah = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[3]/div[1]/div/div/div/div/div[3]/span[2]/span[1]/span")
            sah.click()
            driver.find_element(By.XPATH, "/html/body/span/span/span[1]/input").send_keys(str(court_text) + Keys.ENTER)
        return column - 1 if column < 9 else column - 2

def closePopup(driver, dont_show_again=False):
    wait_presence(driver, By.ID, "closeModal")
    popup_close = driver.find_element(By.ID, "closeModal")
    dontshow = driver.find_element(By.CLASS_NAME, "form-check-input")
    if dont_show_again:
        dontshow.click()
    popup_close.click()

def wait_presence(driver, by:str, value:str, timeout=5):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def findCol(driver, num:int) -> WebElement:
    try:
        return driver.find_element(By.XPATH, f"/html/body/form/div[3]/div[3]/div[3]/div[2]/div[2]/div/div[{num}]")
    except Exception:
        return driver.find_element(By.XPATH, f"/html/body/form/div[3]/div[3]/div[4]/div[2]/div[2]/div/div[{num}]")

Script()