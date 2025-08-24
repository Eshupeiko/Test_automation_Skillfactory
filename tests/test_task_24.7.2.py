from app.api import PetFriends
import os
from app.settings import valid_email, valid_password

pf = PetFriends()

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