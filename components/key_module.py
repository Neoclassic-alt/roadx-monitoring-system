import usb.core
import usb.util
import dearpygui.dearpygui as dpg
from datetime import date, datetime, timedelta
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import os

from components.storage import storage
from components.storage import keys

error = ''

class records:
    open_program = "Приложение открыто"
    flash_did_not_connect = "Проверено на наличие устройства (не подключено)"
    flash_is_connect = "Проверено на наличие устройства (подключено)"
    functional_has_limited = "Функциональность приложения ограничена"
    key_has_created = "Ключ создан"
    key_successfully_checked = "Проверка ключа (успешно)"
    key_expired = "Проверка ключа (срок ключа истёк)"
    key_is_not_valid = "Проверка ключа (ключ невалиден)"
    program_has_activated = "Приложение активировано"
    program_has_closed = "Приложение закрыто\n"

class USBKey:
    def __init__(self):
        self.write_in_journal(records.open_program)
        self.error = ''
        self.key = None # файл лицензии, если прочитан
        self.dev = None
        self.connect()

    def write_in_journal(self, source):
        moment = datetime.today().strftime('%d.%m.%Y %H:%M:%S')
        with open("C:/ProgramData/cv_experiments/journal.txt", 'a') as journal_file:
            journal_file.write(f'{moment} {source}\n')

    # после загрузки ограничим функциональность
    def try_limit(self):
        if not self.check_key():
            self.limit()
        else:
            storage.set_value(keys.DEMO, False)

    # ограничить функции программы
    def limit(self):
        #dpg.disable_item("open_from_internet_button")
        dpg.set_viewport_title("RoadX Monitoring System (DEMO)")
        storage.set_value(keys.DEMO, True)

    # разблокировать программу
    def unlock(self):
        dpg.enable_item("upload_images_from_internet")
        dpg.enable_item("open_from_internet_button")
        dpg.hide_item("demo_menu_item")
        dpg.set_viewport_title("RoadX Monitoring System")
        storage.set_value(keys.DEMO, False)

    def connect(self):
        try:
            self.dev = usb.core.find(idVendor=0x3538)
        except usb.core.NoBackendError:
            self.error = 'Не найдено библиотек для взаимодействия с USB'
        else:
            if not self.dev is None:
                self.hasUSB = True
            else:
                self.hasUSB = False

    def check_connect(self) -> bool:
        self.connect()
        return not self.dev is None

    def open_create_key_window(self):
        result = self.check_connect()
        if not result:
            dpg.show_item("please_connect_flash")
            self.write_in_journal(records.flash_did_not_connect)
            return
        self.write_in_journal(records.flash_is_connect)
        dpg.show_item("form_of_key")
        if os.path.exists("C:/ProgramData/cv_experiments/license.bin"):
            dpg.show_item("key_already_exists")
        else:
            dpg.hide_item("key_already_exists")

    # запись в файл на флешке
    def create_key(self):
        result = self.check_connect()
        if not result:
            dpg.hide_item("form_of_key")
            dpg.show_item("please_connect_flash")
            self.write_in_journal(records.flash_did_not_connect)
            return
        self.write_in_journal(records.flash_is_connect)
        # данные из формы
        user_name = dpg.get_value("username")
        organization = dpg.get_value("name_of_organization")
        duration = dpg.get_value("duration_of_key")
        letter = dpg.get_value("letter_of_key")
        time_string = ''
        if duration == '30 дней':
            time_string = (date.today() + timedelta(days=30)).strftime('%d.%m.%Y')
        if duration == '90 дней':
            time_string = (date.today() + timedelta(days=90)).strftime('%d.%m.%Y')
        if duration == '180 дней':
            time_string = (date.today() + timedelta(days=180)).strftime('%d.%m.%Y')
        # Valid - для проверки корректности
        info = f"""Valid
Name: {user_name}
Organization: {organization}
Expiration: {time_string}
"""
        self.key = info
        # создание случайного ключа
        AES_key = get_random_bytes(16)
        with open(rf"{letter}/key/key.bin", "wb") as key_file:
            key_file.write(AES_key)
        
        #AES_key = self.dev.iSerialNumber.to_bytes((self.dev.iSerialNumber.bit_length() + 7) // 8, 'big')
        #print(AES_key)

        # шифрование
        cipher = AES.new(AES_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(info.encode('utf-8'))
        file_out = open(r"C:/ProgramData/cv_experiments/license.bin", "wb")
        [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
        file_out.close()
        # сохраним букву диска, чтобы не спрашивать
        file_letter = open(r"C:/ProgramData/cv_experiments/letter.txt", "w")
        file_letter.write(letter)
        file_letter.close()
        dpg.hide_item("form_of_key")
        self.write_in_journal(records.key_has_created)

    def decode_file(self):
        with open("C:/ProgramData/cv_experiments/letter.txt", 'r') as letter_file:
            letter = letter_file.read()

        key = None

        if os.path.exists(rf"{letter}/key/key.bin"):
            with open(rf"{letter}/key/key.bin", 'rb') as key_file:
                key = key_file.read()
        #key = self.dev.iSerialNumber.to_bytes((self.dev.iSerialNumber.bit_length() + 7) // 8, 'big')

        if os.path.exists(r"C:/ProgramData/cv_experiments/license.bin") and not key is None:
            file_in = open("C:/ProgramData/cv_experiments/license.bin", "rb")
            nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
            
            cipher = AES.new(key, AES.MODE_EAX, nonce)
            self.key = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

    def view_key(self):
        result = self.check_connect()
        if not result:
            dpg.show_item("please_connect_flash")
            self.write_in_journal(records.flash_did_not_connect)
            return
        if self.key is None:
            self.decode_file()

        dpg.show_item("info_about_key")

        if not self.key is None:
            with open("C:/ProgramData/cv_experiments/letter.txt", 'r') as letter_file:
                letter = letter_file.read()

            dpg.configure_item("letter_of_key_text", default_value=f'Диск: {letter}')
            dpg.configure_item("info_about_key_text", default_value=self.key)
        else:
            dpg.configure_item("letter_of_key_text", default_value='Ключ отсутствует')

    def key_params(self):
        if self.dev is None:
            dpg.show_item("please_connect_flash")
            self.write_in_journal(records.flash_did_not_connect)
            return
        dpg.show_item("params_of_key")
        dpg.configure_item("params_of_key_text", default_value=self.dev)

    def check_key(self) -> bool:
        if self.key is None:
            self.decode_file()
        
        if not self.key is None:
            data = self.key.split('\n')
        else:
            return False
        
        if data[0] == "Valid":
            key_expiration = datetime.strptime(data[3].split(': ')[1], '%d.%m.%Y').date()
            if date.today() > key_expiration:
                self.write_in_journal(records.key_expired)
                return False
        else:
            self.write_in_journal(records.key_is_not_valid)
            return False

        self.write_in_journal(records.key_successfully_checked)
        return True

    # проверить ключ и открыть окно
    def check_key_with_window(self):
        result = self.check_connect()
        if not result:
            dpg.show_item("please_connect_flash")
            self.write_in_journal(records.flash_did_not_connect)
            dpg.show_item("key_check")
            dpg.configure_item("key_validity", default_value="Ключ не вставлен в компьютер",
            color=(255, 0, 0, 255))
            dpg.hide_item("key_expiration")
            return
        
        if self.key is None:
            self.decode_file()
        
        if not self.key is None:
            data = self.key.split('\n')
        else:
            dpg.show_item("key_check")
            dpg.configure_item("key_validity", default_value="Ключ отсутствует в системе")
            return

        valid = False
        expired = True

        if data[0] == "Valid":
            valid = True
            dpg.configure_item("key_validity", default_value="Ключ валиден",
            color=(70, 204, 40))
            key_expiration = datetime.strptime(data[3].split(': ')[1], '%d.%m.%Y').date()
            if key_expiration >= date.today():
                expired = False
            else:
                self.write_in_journal(records.key_expired)
        else:
            self.write_in_journal(records.key_is_not_valid)

        #dpg.hide_item("app_has_activated")

        dpg.show_item("key_check")
        if not valid:
            dpg.configure_item("key_validity", default_value="Ключ не валиден!\nНеобходимо пересоздание",
            color=(255, 0, 0, 255))
            dpg.configure_item("key_expiration", default_value="")
            return
        if expired:
            dpg.configure_item("key_expiration", default_value="Истёк срок действия ключа",
            color=(255, 0, 0, 255))

        dpg.show_item("key_expiration")
        self.write_in_journal(records.key_successfully_checked)

    def show_journal(self):
        with open("C:/ProgramData/cv_experiments/journal.txt", 'r') as journal_file:
            journal = journal_file.read()
        dpg.configure_item("journal", default_value=journal)
        dpg.show_item("journal_of_checks")

    def clear_journal(self):
        with open("C:/ProgramData/cv_experiments/journal.txt", 'w') as journal_file:
            journal_file.write('')
        dpg.configure_item("journal", default_value='')