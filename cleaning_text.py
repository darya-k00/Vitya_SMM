import re


def format_text(text):
    formated_txt = re.sub(' +', ' ', text)
    formated_txt = formated_txt.replace(' "', ' «')
    formated_txt = formated_txt.replace('" ', '» ')
    formated_txt = formated_txt.replace(' - ', ' – ')
    return formated_txt
