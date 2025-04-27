import gspread
from pathlib import Path
from environs import env


env.read_env()


def get_posts():
    gc = gspread.service_account(filename=Path('google_api.json'))
    url = env.str('SHEET_URL')
    sheet = gc.open_by_url(url)
    posts = sheet.sheet1.get_all_records()
    return [post for post in posts if post['Статус'] == 'В обработке']


def validate_post(post: dict):
    required_fields = ['Ссылка на Google Документ', 'social_media', 'id_media', 'Статус']
    for field in required_fields:
        if field not in post:
            return f'Отсутствует обязательное поле: {field}'

    if post['Статус'] != 'В обработке':
        return 'Пост уже опубликован'

    if not post['social_media']:
        return 'Не указана социальная сеть'

    if post['social_media'] == 'tg':
        if post['id_media'].startswith('@'):
            if not post['id_media'][1:].isalnum():
                return "Некорректный Telegram id"
        else:
            return 'Id канала в tg, должен начинаться с @'
    if post['social_media'] == 'vk':
        if not post['id_media'].isalnum():
            return "Некорректный vk id"

    if post['social_media'] == 'ok':
        if not post['id_media'].isalnum():
            return "Некорректный ok id"
