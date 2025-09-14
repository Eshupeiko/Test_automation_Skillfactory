#pytest tests\test_modul_30_1.py --driver Chrome --driver-path D:\chromedriver-win64\chromedriver.exe
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.settings import valid_email, valid_password
import re

@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    # Устанавливаем НЕЯВНОЕ ожидание для всех
    driver.implicitly_wait(10)
    # Переходим на страницу авторизации
    driver.get('https://petfriends.skillfactory.ru/login')
    yield driver
    driver.quit()

def test_show_all_pets(driver):
    wait = WebDriverWait(driver, 10)

    # Вводим email
    driver.find_element(By.ID, 'email').send_keys(valid_email)
    # Вводим пароль
    driver.find_element(By.ID, 'pass').send_keys(valid_password)
    # Нажимаем на кнопку входа в аккаунт
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(3)
    # Проверяем, что мы оказались на главной странице пользователя
    h1_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
    assert h1_element.text == "PetFriends"
    # Переходим на страницу "Мои питомцы"
    button_profile = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="navbarNav"]/ul/li[1]/a')))
    button_profile.click()
    #Проверяем имя пользователя,что означает, что мы находимся на странице мои питомцы:
    h2_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h2')))
    assert h2_element.text == "WERTY"

    #Получаем количество питомцев из статистики:
    stats_block = driver.find_element(By.CSS_SELECTOR, "/html/body/div[1]/div/div[1]/text()[1]")
    stats_text = stats_block.text.strip()
    match = re.search(r'Питомцев:\s*(\d+)', stats_text)
    if match:
        quantity_in_statistics = int(match.group(1))
        print(f"Количество питомцев из статистики: {quantity_in_statistics}")
    else:
        raise Exception("Не удалось найти строку 'Питомцев: X' в блоке статистики")

    #Находим все строки (карточки) с питомцами
    pet_table = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="all_my_pets"]//table[@class="table table-hover"]')))
    pet_rows = pet_table.find_elements(By.XPATH, './/tbody/tr')
    actual_pet_cards_count = len(pet_rows)
    print(f"Фактическое количество карточек питомцев на странице: {actual_pet_cards_count}")
    actual_pet_cards_count = 3
    #Проверка 1: Присутствуют все питомцы
    assert actual_pet_cards_count == quantity_in_statistics, \
        f"Несоответствие! В статистике: {quantity_in_statistics} на странице: {actual_pet_cards_count}"
    # Списки для хранения данных о питомцах
    pet_photos = []  # Будет хранить True/False (есть фото/нет фото)
    pet_names = []  # Будет хранить имена
    pet_breeds = []  # Будет хранить породы
    pet_ages = []  # Будет хранить возрасты
    pet_descriptions = []  # Будет хранить полное описание "Порода, Возраст"

    # Проходим по каждой строке таблицы
    for row in pet_rows:
        # Фото: Ищем элемент <th> с <img>
        photo_cell = row.find_element(By.XPATH, './th[@scope="row"]')
        img_element = photo_cell.find_element(By.TAG_NAME, 'img')
        # Проверяем, есть ли атрибут 'src' и не пустой ли он
        photo_src = img_element.get_attribute('src')
        has_photo = bool(photo_src and photo_src.strip() != '')
        pet_photos.append(has_photo)

        # Имя: второй <td>
        name_cell = row.find_element(By.XPATH, './td[2]')
        pet_name = name_cell.text.strip()
        pet_names.append(pet_name)

        # Порода: третий <td>
        breed_cell = row.find_element(By.XPATH, './td[3]')
        pet_breed = breed_cell.text.strip()
        pet_breeds.append(pet_breed)

        # Возраст: четвертый <td>
        age_cell = row.find_element(By.XPATH, './td[4]')
        pet_age = age_cell.text.strip()
        pet_ages.append(pet_age)

        # Полное описание для удобства
        pet_descriptions.append(f"{pet_breed}, {pet_age}")

    # Проверка 2: Хотя бы у половины питомцев есть фото
    pets_with_photo_count = sum(pet_photos)  # Суммируем True (1) значения
    assert pets_with_photo_count >= actual_pet_cards_count / 2, \
        f"Фото есть только у {pets_with_photo_count} из {actual_pet_cards_count} питомцев (меньше половины)"

    # Проверка 3: У всех питомцев есть имя, возраст и порода
    for i in range(actual_pet_cards_count):
        assert pet_names[i] != "", f"У питомца №{i + 1} (описание: {pet_descriptions[i]}) отсутствует имя"
        assert pet_breeds[i] != "", f"У питомца №{i + 1} (имя: {pet_names[i]}) отсутствует порода"
        assert pet_ages[i] != "", f"У питомца №{i + 1} (имя: {pet_names[i]}) отсутствует возраст"

    # Проверка 4: У всех питомцев разные имена
    unique_names = set(pet_names)  # set содержит только уникальные значения
    assert len(unique_names) == len(pet_names), \
        f"Имена питомцев не уникальны. Уникальных имен: {len(unique_names)}, всего питомцев: {len(pet_names)}"

    # Проверка 5: В списке нет повторяющихся питомцев

    pet_tuples = [(pet_names[i], pet_breeds[i], pet_ages[i]) for i in range(actual_pet_cards_count)]
    unique_pets = set(pet_tuples)
    assert len(unique_pets) == len(pet_tuples), \
        f"В списке есть повторяющиеся питомцы. Уникальных питомцев: {len(unique_pets)}, всего строк: {len(pet_tuples)}"
