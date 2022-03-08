# программа для генерации ключа
import sys
import usb.core
from datetime import date, datetime, timedelta
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

print("Здравствуйте! Здесь вы можете создать свой ключ!")
print("Убедитесь, что USB-устройство вставлено")

user_name = input("Имя: ")
organization = input("Название организации: ")
duration = input("Введите число дней: ")
letter = input("Введите букву диска: ")

dev = usb.core.find(idVendor=0x3538)
if dev is None:
    print("Внимание! Устройство не вставлено в компьютер! Создание ключа невозможно!")
    sys.exit()

if duration.isdigit():
    if letter != "":
        time_string = (date.today() + timedelta(days=int(duration))).strftime('%d.%m.%Y')
        # Valid - для проверки корректности
        info = f"""Valid
Name: {user_name}
Organization: {organization}
Expiration: {time_string}
"""
        # создание случайного ключа
        AES_key = get_random_bytes(16)
        with open(rf"{letter}:/key/key.bin", "wb") as key_file:
            key_file.write(AES_key)

        # шифрование
        cipher = AES.new(AES_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(info.encode('utf-8'))
        file_out = open(r"C:/ProgramData/cv_experiments/license.bin", "wb")
        [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
        file_out.close()
        # сохраним букву диска, чтобы не спрашивать
        file_letter = open(r"C:/ProgramData/cv_experiments/letter.txt", "w")
        file_letter.write(letter + ':')
        file_letter.close()
        print("Ключ создан!")
    else:
        print("Введите букву")
else:
    print("Неверное число дней")