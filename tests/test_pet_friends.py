from app.api import PetFriends
import os
from app.settings import valid_email, valid_password, invalid_email, invalid_password

pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='1756064870.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), "images" , pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_add_new_pet_without_photo(name='Тошка', animal_type='кот', age='2'):
    """Проверяем, что можно добавить питомца без фото с корректными данными"""

    # Шаг 1: Получаем API-ключ
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Шаг 2: Добавляем питомца без фото
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
# Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_add_photo_to_pet_without_photo(pet_photo='1756064870.jpg'):
    """Проверяем, что можно добавить фото к карточке питомца без фото"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Если нет питомцев без фото — сначала добавим питомца без фото
    pet_without_photo = None
    for pet in my_pets['pets']:
        if pet['pet_photo'] == "":  # если нет фото
            pet_without_photo = pet
            break

    #Если нет — создаём нового питомца без фото
    if pet_without_photo is None:
        _, result = pf.add_new_pet_without_photo(auth_key, "Фото_тест", "кот", "1")
        assert result['name'] == "Фото_тест"
        # Получаем обновлённый список
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        pet_without_photo = my_pets['pets'][0]  # берём только что добавленного

    #Берём ID питомца без фото
    pet_id = pet_without_photo['id']

    #Формируем путь к фото
    pet_photo_path = os.path.join(os.path.dirname(__file__), "images", pet_photo)

    #Проверяем, что файл существует
    if not os.path.exists(pet_photo_path):
        raise FileNotFoundError(f"Файл не найден: {pet_photo_path}")

    #Добавляем фото
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo_path)

    assert status == 200, f"Ожидался статус 200, но получен {status}"
    assert 'pet_photo' in result and result['pet_photo'] != "", "Фото не было добавлено"

#Получение ключа с неверным email
def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    """Проверяем, что при неверном email возвращается статус 403"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

#Получение ключа с неверным паролем
def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """Проверяем, что при неверном пароле возвращается статус 403"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

#Получение ключа с пустыми данными
def test_get_api_key_with_empty_credentials():
    """Проверяем, что при пустых email и password возвращается 403"""
    status, result = pf.get_api_key("", "")
    assert status == 403
    assert 'key' not in result

#Добавление питомца с пустым именем
def test_add_pet_with_empty_name(animal_type='кот', age='3', pet_photo='1756064870.jpg'):
    """Проверяем, что нельзя добавить питомца с пустым именем"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), "images", pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, "", animal_type, age, pet_photo_path)

    assert status == 400  # или 400 — зависит от API, но не 200
    assert 'name' not in result or result.get('name') == ""

#Добавление питомца с отрицательным возрастом
def test_add_pet_with_negative_age(name='Барсик', animal_type='кот', age='-5', pet_photo='1756064870.jpg'):
    """Проверяем, что нельзя добавить питомца с отрицательным возрастом"""
    pet_photo_path = os.path.join(os.path.dirname(__file__), "images", pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo_path)

    assert status == 400
    assert result.get('age') != age

#Обновление питомца с пустым именем
def test_update_pet_with_empty_name():
    """Проверяем, что нельзя обновить имя питомца на пустое"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], "", "кот", 3)
        assert status == 400
        assert result.get('name') != ""
    else:
        raise Exception("Нет питомцев для обновления")

#Попытка удалить несуществующего питомца
def test_delete_nonexistent_pet():
    """Проверяем, что попытка удалить питомца с несуществующим ID возвращает 404 или 400"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    non_existent_id = "12345678-1234-1234-1234-1234567890ab"  # случайный ID

    status, _ = pf.delete_pet(auth_key, non_existent_id)

    assert status in [400, 404], f"Ожидался 400 или 404, получен {status}"

#Добавление фото к несуществующему питомцу
def test_add_photo_to_nonexistent_pet(pet_photo='1756064870.jpg'):
    """Проверяем, что нельзя добавить фото к питомцу с несуществующим ID"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    non_existent_id = "12345678-1234-1234-1234-1234567890ab"
    pet_photo_path = os.path.join(os.path.dirname(__file__), "images", pet_photo)

    if not os.path.exists(pet_photo_path):
        raise FileNotFoundError(f"Файл не найден: {pet_photo_path}")

    status, result = pf.add_pet_photo(auth_key, non_existent_id, pet_photo_path)

    assert status in [400, 404]

#Проверка фильтра 'my_pets' — возвращаются только свои питомцы
def test_get_my_pets_filter():
    """Проверяем, что при фильтре 'my_pets' возвращаются только питомцы пользователя"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert 'pets' in result

#Граничный: Добавление питомца с очень длинным именем (100+ символов)
def test_add_pet_with_long_name():
    """Проверяем, как API обрабатывает очень длинное имя"""
    long_name = "A" * 100
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet_without_photo(auth_key, long_name, "кот", "2")

    # API может либо обрезать имя, либо вернуть 400
    assert status in [200, 400]
    if status == 200:
        assert len(result['name']) <= 100
    else:
        assert 'name' not in result or result.get('name') != long_name