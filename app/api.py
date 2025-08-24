import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import os

class PetFriends:
    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email, password):

        headers = {
            'email': email,
            'password': password,
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def get_list_of_pets(self, auth_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате JSON
        со списком наденных питомцев, совпадающих с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        собственных питомцев"""

        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url + 'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet(self, auth_key: dict, name: str, animal_type: str, age: str, pet_photo: str) -> tuple:
        """Метод отправляет на сервер данные о новом питомце с фото. Возвращает статус и результат."""

        # Открываем файл и включаем его в MultipartEncoder
        with open(pet_photo, 'rb') as photo:
            data = MultipartEncoder(
                fields={
                    'name': name,
                    'animal_type': animal_type,
                    'age': age,
                    'pet_photo': (os.path.basename(pet_photo), photo, 'image/jpeg')  # ← файл внутри данных
                }
            )

            headers = {
                'auth_key': auth_key['key'],
                'Content-Type': data.content_type  # важно: динамический boundary
            }

            # Отправляем POST-запрос
            res = requests.post(self.base_url + 'api/pets', headers=headers, data=data)

        # Обработка ответа
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.JSONDecodeError:
            result = res.text

        return status, result

    def delete_pet(self, auth_key: json, pet_id: str) -> json:
        """Метод отправляет на сервер запрос на удаление питомца по указанному ID и возвращает
        статус запроса и результат в формате JSON с текстом уведомления о успешном удалении.
        На сегодняшний день тут есть баг - в result приходит пустая строка, но status при этом = 200"""

        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def update_pet_info(self, auth_key: json, pet_id: str, name: str,
                        animal_type: str, age: int) -> json:
        """Метод отправляет запрос на сервер о обновлении данных питомуа по указанному ID и
        возвращает статус запроса и result в формате JSON с обновлённыи данными питомца"""

        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'age': age,
            'animal_type': animal_type
        }

        res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_new_pet_without_photo(self, auth_key: dict, name: str, animal_type: str, age: str) -> tuple:
        """
        Добавляет питомца без фото
        """

        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }

        headers = {
            'auth_key': auth_key['key']
            # Content-Type добавлять не нужно — requests сделает сам для data=dict
        }

        response = requests.post(
            self.base_url + 'api/create_pet_simple',
            headers=headers,
            data=data
        )

        status = response.status_code
        result = ""
        try:
            result = response.json()
        except json.JSONDecodeError:
            result = response.text

        return status, result

    def add_pet_photo(self, auth_key: dict, pet_id: str, pet_photo: str) -> tuple:
        """
        Метод добавляет фото к карточке питомца по его pet_id.
            """

        # Проверяем, что файл существует
        if not os.path.exists(pet_photo):
            raise FileNotFoundError(f"Файл изображения не найден: {pet_photo}")

        # Открываем файл
        with open(pet_photo, 'rb') as photo:
            data = MultipartEncoder(
                fields={
                    'pet_photo': (os.path.basename(pet_photo), photo, 'image/jpeg')
                }
            )

            headers = {
                'auth_key': auth_key['key'],
                'Content-Type': data.content_type  # важно: boundary для multipart
            }

            # Отправляем запрос
            response = requests.post(
                self.base_url + f'api/pets/set_photo/{pet_id}',
                headers=headers,
                data=data
            )

        # Обработка ответа
        status = response.status_code
        result = ""
        try:
            result = response.json()
        except json.JSONDecodeError:
            result = response.text

        return status, result