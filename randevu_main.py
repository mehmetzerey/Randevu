import undetected_chromedriver as uc
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import winsound
from selenium.webdriver.chrome.options import Options
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from anasayfa_python import Ui_Widget

import glob


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.ui.KayitEkle.clicked.connect(self.add_record)
        self.ui.KrediKartiEkle.clicked.connect(self.add_credit_card)
        self.ui.Kategori.currentTextChanged.connect(self.category)
        self.ui.AltKategori.currentTextChanged.connect(self.sub_category)
        self.ui.KrediKartiCheck.stateChanged.connect(self.credit_card_check)
        self.ui.Baslat.clicked.connect(self.start)
        self.ui.Kayitlar_list.itemDoubleClicked.connect(self.update_input_fields)
        self.ui.yenile.clicked.connect(self.refresh_records)

        self.applicationdetails_url = "https://visa.vfsglobal.com/tur/tr/pol/applicationdetails"

        # Initialize your variables here
        self.driver = None
        self.selected_category = None
        self.selected_sub_category = None
        self.sub_category_short_period_xpath_list = [
            '//*[@id="mat-option-463"]/span',
            '//*[@id="mat-option-464"]/span',
            '//*[@id="mat-option-465"]/span',
            '//*[@id="mat-option-466"]/span'
        ]

        self.sub_category_long_period_xpath_list = [
            '//*[@id="mat-option-467"]/span',
            '//*[@id="mat-option-468"]/span',
            '//*[@id="mat-option-469"]/span',
            '//*[@id="mat-option-470"]/span'
        ]
        # Update the list of records
        self.update_records_list()

    @staticmethod
    def wait_for_element_to_become_visible(driver, by, value, timeout=50):
        """
        Belirtilen element belirtilen süre içinde görünür olana kadar bekler.

        Args:
            driver (WebDriver): WebDriver nesnesi.
            by (By): Belirtilen elementi bulmak için kullanılan By nesnesi (ör. By.XPATH).
            value (str): Elementin lokatör değeri (ör. XPath veya CSS seçici).
            timeout (int): Maksimum bekleme süresi (saniye).

        Returns:
            WebElement: Bulunan element nesnesi.
        """
        try:
            while True:
                try:
                    element = WebDriverWait(driver, 0.1).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'ngx-overlay'))
                    )
                except:
                    break
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except Exception as e:
            raise Exception(f"Element görünür olana kadar bekleme başarısız: {e}")

    def update_records_list(self):
        record_files = glob.glob('records/*.txt')

        self.ui.Kayitlar_list.clear()
        for file_path in record_files:
            user = (file_path.split("\\")[1].split(".txt")[0])
            file = open("records/" + user + ".txt", 'r')
            user = file.readline()
            file.close()
            user = user.split(";")
            user.pop(-1)
            if user[-1] == "0":
                self.ui.Kayitlar_list.addItem(file_path.split("\\")[1].split(".txt")[0])

    def wait(self):
        while True:

            try:
                WebDriverWait(self.driver, 0.1).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'ngx-overlay'))
                )
            except:
                break

    def start(self):
        user_email = "mehmetzerey.developer@gmail.com"  # Replace with your email
        user_pass = "ahmetEdurepa34*"  # Replace with your password
        # user_email = "jane.doe@email.com"  # Replace with your email
        # user_pass = "your_password"  # Replace with your password

        self.selected_region = str(self.ui.Bolge.currentIndex())
        self.selected_category = str(self.ui.Kategori.currentIndex())
        self.selected_sub_category = str(self.ui.AltKategori.currentIndex())

        if self.driver is None:
            self.check_dashboard(user_email, user_pass)
            self.verify_code()
            self.click_checkboxes_and_start_reservation()
            self.terms_and_conditions()
            self.create_details()
            self.appointment_details_fill()

    def check_dashboard(self, user_email, user_pass):
        options = Options()
        # proxy = "164.92.195.118:8080"
        # options.add_argument(f"--proxy-server={proxy}")
        self.driver = uc.Chrome(headless=False, use_subprocess=False, version_main=116, options=options)
        self.driver.get("https://visa.vfsglobal.com/tur/tr/pol/dashboard")
        time.sleep(10)
        if "https://visa.vfsglobal.com/tur/tr/pol/dashboard" in self.driver.current_url:
            print("anasayfadayız")
        else:
            print("logindeyiz")
            self.login(user_email=user_email, user_pass=user_pass)

    def login(self, user_email, user_pass):
        self.driver.get("https://visa.vfsglobal.com/tur/tr/pol/login")

        # reCAPTCHA'yı onaylayın
        recaptcha_checkbox = False
        while recaptcha_checkbox is False:
            try:
                recaptcha_input = input("Chaptch geçildi mi: 1 evet")
                if recaptcha_input == "1":
                    recaptcha_checkbox = True
            except Exception as e:
                print("reCAPTCHA henüz onaylanmadı.", e)
                pass

        print("reCAPTCHA onaylandı.")

        # E-posta ve şifre alanlarını doldurun
        email_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, "//input[@formcontrolname='username']")
        email_input.send_keys(user_email)

        time.sleep(2)

        password_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, "//input[@formcontrolname='password']")
        password_input.send_keys(user_pass)

        time.sleep(2)

        # Oturum Aç düğmesine tıkla
        login_button = self.wait_for_element_to_become_visible(self.driver, By.XPATH, "/html/body/app-root/div/div/app-login/section/div/div/mat-card/form/button/span[1]")
        login_button.click()

        time.sleep(2)

    def verify_code(self):
        verification_input_element = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                     "//input[@formcontrolname='otp']")
        verification_input = input("Doğrulama kodunu giriniz")
        verification_input_element.send_keys(int(verification_input))

        time.sleep(3)

        login_button = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                               "/html/body/app-root/div/div/app-login/section/div/div/mat-card/form/button/span[1]")
        login_button.click()
        time.sleep(10)
        if "https://visa.vfsglobal.com/tur/tr/pol/login" in self.driver.current_url:
            info = input("loginde kaldı bir sorun olabilir sayfayı konrol et. devam etmek için bir tuşa bas")

    def click_checkboxes_and_start_reservation(self):
        try:
            if "Yeni Rezervasyon Başlat" in self.driver.page_source:

                # İlk checkbox'ı bul ve işaretle
                checkbox1 = self.driver.find_element(By.XPATH, '//*[@id="mat-checkbox-1"]/label/span[1]')
                if not checkbox1.is_selected():
                    checkbox1.click()

                time.sleep(1)

                # İkinci checkbox'ı bul ve işaretle
                checkbox2 = self.driver.find_element(By.XPATH, '//*[@id="mat-checkbox-2"]/label/span[1]')
                if not checkbox2.is_selected():
                    checkbox2.click()

                time.sleep(1)

                # "Yeni Rezervasyon Başlat" düğmesini bul ve tıkla
                yeni_rezervasyon_button = self.driver.find_element(By.XPATH,
                                                              "/html/body/app-root/div/div/app-dashboard/section[1]/div/div[2]/div/button/span[1]")
                yeni_rezervasyon_button.click()
            else:
                print("anasayfada checkboxlar yani yeni rezervasyon başlat bulunamadı")

        except Exception as e:
            print(f'Hata: {str(e)}')

    def terms_and_conditions(self):
        if "Şartlar ve koşullar" in self.driver.page_source:
            checkbox1 = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-checkbox-3"]/label/span[1]')
            if not checkbox1.is_selected():
                checkbox1.click()

            time.sleep(1)

            devamet_buton = self.wait_for_element_to_become_visible(self.driver, By.XPATH, "/html/body/app-root/div/div/app-dashboard/section/div/button/span[1]")
            devamet_buton.click()

    def create_details(self):
        if "https://visa.vfsglobal.com/tur/tr/pol/your-details" in self.driver.current_url:
            try:
                # Ad girişi
                ad_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-3"]')
                ad_input.send_keys("MEHMET")

                time.sleep(1)

                # Soyadı girişi
                soyad_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-4"]')
                soyad_input.send_keys("ZEREY")

                time.sleep(1)

                # Cinsiyet seçimi (örneğin, "female" seçeneği)
                # female //*[@id="mat-option-0"]/span
                self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-select-0"]/div/div[2]/div').click()
                time.sleep(1)
                cinsiyet_female = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-option-1"]/span')
                cinsiyet_female.click()

                time.sleep(1)

                # Uyruk seçimi (örneğin, "Türkiye" seçeneği)
                self.wait_for_element_to_become_visible(self.driver,By.XPATH, '//*[@id="mat-select-2"]/div/div[2]/div').click()
                time.sleep(1)
                uyruk_turkiye = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-option-396"]/span')
                uyruk_turkiye.click()

                time.sleep(1)

                # Pasaport girişi
                pasaport_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-5"]')
                pasaport_input.send_keys("AB123456")

                time.sleep(1)

                # Telefon kodu girişi (eğer bu alanla ilgili bilgi yoksa boş bırakabilirsiniz)
                tel_kod_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-6"]')
                tel_kod_input.send_keys("90")

                # Telefon numarası girişi
                numara_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-7"]')
                numara_input.send_keys("5551234567")

                time.sleep(1)

                # E-posta girişi
                eposta_input = self.wait_for_element_to_become_visible(self.driver, By.XPATH, '//*[@id="mat-input-8"]')
                eposta_input.send_keys("mehmetzerey@gmail.com")

                time.sleep(1)

                # Kaydet butonu tıklama
                kaydet_button = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                         '/html/body/app-root/div/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[1]/button/span[1]')
                kaydet_button.click()

                print("Bilgiler başarıyla girildi ve kaydedildi.")
            except Exception as e:
                print("Hata oluştu:", e)
        else:
            print("Detay sayfası gelmedi")

    def appointment_details_fill(self):
        # önce kategori hazırla aşağıda clickle

        sub_category_select_open = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                     '//*[@id="mat-select-6"]/div/div[2]')

        category_select_open = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                     '//*[@id="mat-select-4"]/div/div[2]/div')
        category_select_open.click()
        time.sleep(2)
        # uzun dönem
        if self.selected_category == "0":
            print("kategori 1")
            # uzun döneme clickle
            category_select_long_period = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                           '//*[@id="mat-option-460"]/span')
            category_select_long_period.click()

            time.sleep(2)
            sub_category_select_open.click()

            selected_long_period_subcategory_xpath = self.sub_category_short_period_xpath_list[
                int(self.selected_sub_category)]

            subcategory_selected_long_period = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                                  selected_long_period_subcategory_xpath)
            subcategory_selected_long_period.click()

            try:
                # Verilen dökümanı bul
                overlay_container = self.wait_for_element_to_become_visible(self.driver, By.CLASS_NAME, 'cdk-overlay-container')

                # Seçenekleri içeren elementi bul
                # options_element = overlay_container.find_element(By.ID, 'mat-select-8-panel')

                # Seçeneklerin sayısını bul
                options = overlay_container.find_elements(By.CLASS_NAME, 'mat-option')

                if options:
                    # 1. sıradaki seçeneğin span etiketine tıkla
                    first_option = options[0].find_element(By.TAG_NAME, 'span')
                    first_option.click()
                    print("1. sıradaki seçenek seçildi.")
                else:
                    print("Seçenekler bulunamadı.")

            except NoSuchElementException:
                print("Seçenekler bulunamadı.")


        # kısa dönem
        elif self.selected_category == "1":
            # kısa donem clickle
            category_select_short_period = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                           '//*[@id="mat-option-461"]/span')
            category_select_short_period.click()

            time.sleep(2)
            sub_category_select_open.click()

            selected_short_period_subcategory_xpath = self.sub_category_short_period_xpath_list[
                int(self.selected_sub_category)]

            subcategory_selected_short_period = self.wait_for_element_to_become_visible(self.driver, By.XPATH,
                                                                                       selected_short_period_subcategory_xpath)
            subcategory_selected_short_period.click()


        # alt kategori kısa
        # //*[@id="mat-option-467"]/span is seyehati
        # //*[@id="mat-option-468"]/span
        # //*[@id="mat-option-469"]/span
        # //*[@id="mat-option-470"]/span

        # merkez
        # ana select div //*[@id="mat-select-8"]
    # eğer merkez bulamazsa anasayfadan baştan başlasın



    def credit_card_check(self):

        if self.ui.KrediKartiCheck.isChecked() == True:

            # kayıtları listede güncelleme
            self.ui.KrediKartiList.clear()
            open_credit_card_txt = open("creditcard/creditcard.txt", 'r')
            read_credit_card_txt = open_credit_card_txt.readline()
            open_credit_card_txt.close()
            read_credit_card_txt = read_credit_card_txt.split(";")
            read_credit_card_txt.pop(-1)
            self.ui.KrediKartiList.addItem("Kart No:" + read_credit_card_txt[0])
            self.ui.KrediKartiList.addItem("Ay:" + read_credit_card_txt[1])
            self.ui.KrediKartiList.addItem("Yıl:" + read_credit_card_txt[2])
            self.ui.KrediKartiList.addItem("Kod:" + read_credit_card_txt[3])
            self.ui.KrediKartiList.addItem("Ad::" + read_credit_card_txt[4])
            self.ui.KrediKartiList.addItem("Adres:" + read_credit_card_txt[5])
            self.ui.KrediKartiList.addItem("Posta:" + read_credit_card_txt[6])
        else:
            self.ui.KrediKartiList.clear()

    def sub_category(self):
        self.selected_category = str(self.ui.Kategori.currentIndex())
        self.selected_sub_category = str(self.ui.AltKategori.currentIndex())

    def category(self):

        selected_index = self.ui.Kategori.currentIndex()
        self.selected_category = self.ui.Kategori.currentIndex()
        self.selected_sub_category = self.ui.AltKategori.currentIndex()

        if selected_index == 0:
            self.ui.AltKategori.clear()
            self.ui.AltKategori.addItem("Yuksek Öğrenim")
            self.ui.AltKategori.addItem("Çalışma İzni")
            self.ui.AltKategori.addItem("Diğer Uzun Dönem")
        if selected_index == 1:
            self.ui.AltKategori.clear()
            self.ui.AltKategori.addItem("İş Seyehati")
            self.ui.AltKategori.addItem("Turistlik")
            self.ui.AltKategori.addItem("Tir Soforu")
            self.ui.AltKategori.addItem("Diğer Kısa Dönem")

    def add_credit_card(self):
        credit_card_number = str(self.ui.kartno.text())
        credit_card_month = str(self.ui.ay.text())
        credit_card_year = str(self.ui.yil.text())
        credit_card_cvv = str(self.ui.kod.text())
        credit_card_name_surname = str(self.ui.adisoyadi.text())
        address = str(self.ui.adres.text())
        post_code = str(self.ui.postakodu.text())

        open_credit_card_txt = open("creditcard/creditcard.txt", 'w')

        open_credit_card_txt.write(credit_card_number + ";" + credit_card_month + ";" + credit_card_year + ";" + credit_card_cvv + ";" + credit_card_name_surname + ";" + address + ";" + post_code + ";")
        open_credit_card_txt.close()
        QMessageBox.about(self, "Kayit", "Basarili")

        # kayıtları listede güncelleme
        if self.ui.KrediKartiCheck.isChecked():
            open_credit_card_txt = open("creditcard/creditcard.txt", 'r')
            read_credit_card_txt = open_credit_card_txt.readline()
            open_credit_card_txt.close()
            read_credit_card_txt = read_credit_card_txt.split(";")
            read_credit_card_txt.pop(-1)
            self.ui.KrediKartiList.addItem("Kart No:" + read_credit_card_txt[0])
            self.ui.KrediKartiList.addItem("Ay:" + read_credit_card_txt[1])
            self.ui.KrediKartiList.addItem("Yıl:" + read_credit_card_txt[2])
            self.ui.KrediKartiList.addItem("Kod:" + read_credit_card_txt[3])
            self.ui.KrediKartiList.addItem("Ad::" + read_credit_card_txt[4])
            self.ui.KrediKartiList.addItem("Adres:" + read_credit_card_txt[5])
            self.ui.KrediKartiList.addItem("Posta:" + read_credit_card_txt[6])

    def add_record(self):
        name = str(self.ui.giris1.text())
        surname = str(self.ui.giris2.text())
        gender = str(self.ui.giris3.text())
        birth_date = str(self.ui.giris4.text())
        nationality = str(self.ui.giris5.text())
        passport_number = str(self.ui.giris6.text())
        passport_date = str(self.ui.giris7.text())
        area_code = str(self.ui.giris8.text())
        phone_number = str(self.ui.giris9.text())
        email = str(self.ui.giris10.text())
        mail_txt = str(self.ui.vfsmail.text())
        password_txt = str(self.ui.vfssifre.text())
        approval = "0"

        file_name = "records/" + name + surname + ".txt"
        with open(file_name, 'w') as file:
            file.write(
                f"{name};{surname};{gender};{birth_date};{nationality};{passport_number};"
                f"{passport_date};{area_code};{phone_number};{email};{mail_txt};{password_txt};{approval};"
            )

        QMessageBox.about(self, "Record", "Successful")

        # Update the list of records
        records = glob.glob('records/*.txt')

        self.ui.Kayitlar_list.clear()
        for file_path in records:
            user_info = (file_path.split("\\")[1].split(".txt")[0])
            with open("records/" + user_info + ".txt", 'r') as file:
                user_info = file.readline()
                user_info = user_info.split(";")
                user_info.pop(-1)
                if user_info[-1] == "0":
                    self.ui.Kayitlar_list.addItem(file_path.split("\\")[1].split(".txt")[0])

    def refresh_records(self):
        # Kayıtları liste olarak güncelleme
        record_files = glob.glob('records/*.txt')

        self.ui.Kayitlar_list.clear()
        for record_file in record_files:
            username = (record_file.split("\\")[1].split(".txt")[0])
            file = open("records/" + username + ".txt", 'r')
            username = file.readline()
            file.close()
            username = username.split(";")
            username.pop(-1)
            if username[-1] == "0":
                self.ui.Kayitlar_list.addItem(record_file.split("\\")[1].split(".txt")[0])

    def update_input_fields(self, item):
        filename = str(item.text())

        with open("records/" + filename + ".txt", 'r') as file:
            data = file.readline().split(";")

        input_fields = [
            self.ui.giris1, self.ui.giris2, self.ui.giris3, self.ui.giris4,
            self.ui.giris5, self.ui.giris6, self.ui.giris7, self.ui.giris8,
            self.ui.giris9, self.ui.giris10, self.ui.vfsmail, self.ui.vfssifre
        ]

        for i in range(min(len(input_fields), len(data))):
            input_fields[i].setText(data[i])


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Randevu Alma Programı")
    window.show()
    sys.exit(app.exec_())
