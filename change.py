import json
import logging
import requests
from tqdm import tqdm
from urllib.parse import urlencode
APP_ID = '51724525'
OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
params = {
    'client_id': APP_ID,
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    'display': 'page',
    'scope': 'photos',
    'response_type': 'token'
          }
oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
# print(oauth_url)

class VK:
    API_BASE_URL = 'https://api.vk.com/method/'


    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id


    def common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131',
            'extended': '1'
               }


    def get_photos(self):
        try:
            # Получение фотографий из VK API
            params = self.common_params()
            params.update({'owner_id': self.user_id, 'album_id': 'profile'})
            response = requests.get(f'{self.API_BASE_URL}photos.get', params=params)
            response.raise_for_status()
            photos = response.json()['response']['items']
            return photos
        except (KeyError, requests.exceptions.RequestException) as e:
            logging.error(f"Error getting photos from VK: {str(e)}")



    def get_photo_likes(self, photo):
        likes = photo['likes']['count']
        return likes


class Yandex:
    def __init__(self, token):
        self.token = token


    def create_folder(self, folder_name):
        try:
            # Создание папки на Я.Диске
            headers = {
                'Authorization': f'OAuth {self.token}'
            }
            params = {
                'path': folder_name
            }
            response = requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating folder on Yandex.Disk: {str(e)}")




    def upload_photo(self, folder_name, photo_url, photo_name):
        try:
            # Загрузка фотографии на Я.Диск
            headers = {
                'Authorization': f'OAuth {self.token}'
            }
            params = {
                'path': f"{folder_name}/{photo_name}",
                'url': photo_url
            }
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=headers,
                                     params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error uploading photo to Yandex.Disk: {str(e)}")


def main():
    # Настройка логирования
    logging.basicConfig(filename='log.txt', level=logging.ERROR)


    token = input('Введите токен VK: ')
    yandex_token = input('Введите токен Я.Диска: ')
    user_id = int(input('Введите id пользователя VK: '))
    if not user_id:
        logging.error("User ID is not provided")




    try:
        vk = VK(token, user_id)
        photos = vk.get_photos()

        # Создание папки на Я.Диске
        yandex = Yandex(yandex_token)
        folder_name = 'course'
        yandex.create_folder(folder_name)

        # Загрузка фотографий на Я.Диск и сохранение информации в json-файл
        with open('photos.json', 'w') as file:
            photo_list = []
            for photo in tqdm(photos, desc="Uploading photos"):
                photo_likes = vk.get_photo_likes(photo)
                photo_name = f"{photo_likes}.jpg"
                yandex.upload_photo(folder_name, photo['sizes'][-1]['url'], photo_name)

                photo_info = {
                    'photo_name': photo_name,
                    'size': photo['sizes'][-1]['type'],
                              }
                photo_list.append(photo_info)

            json.dump(photo_list, file, indent=1)

        logging.info("Photos successfully processed")
    except Exception as e:
        logging.error(f"Error processing photos: {str(e)}")


if __name__ == "__main__":
    main()