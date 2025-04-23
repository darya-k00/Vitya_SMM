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


def validate_post():
    pass
