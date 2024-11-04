# большой скрипт с разными вариантами систематизации информации
from bs4 import BeautifulSoup # подключаем конструктор BeautifulSoup для удобной обработки получаемых с веб-страниц ответов
import requests # подключаем модуль для запросов к веб-страницам
import json # подключаем модуль для сохранения данных в JSON-файл

quotes = [] # основной список словарей с цитатами, авторами и тэгами
tags_dictionary = {} # словарь со списком тэгов и ссылками на них
authors_info = {} # словарь с авторами и информацией о них
quotes_by_author = {} # словарь с авторами и их цитатами
quotes_by_tag = {} # словарь с тэгами и соответствующими им цитатами

# определяем функцию для обработки данных
def parse_page(page):
    raw_quotes = page.find_all(class_='quote') # находим все блоки цитат с элементами с классом "текст", "автор" и "тэги"
    for rq in raw_quotes: # идем циклом по всем найденным блокам цитат, сохраняем данные
        quote_text = rq.find(class_='text').text.strip('“”') # получаем текст цитаты.
        # срезаем кавычки, т.к. вместо них в JSON файле код "\u201c и \u201d, смысл не теряется, читаемость улучшается
        author = rq.find(class_='author').text # получаем автора
        quotes_by_author[author] = quotes_by_author.get(author, list()) # проверяем, есть ли автор в словаре авторов и цитат, 
        #если нет - создаем на месте значения пустой список
        quotes_by_author[author].append(quote_text) # добавляем к ключу автора в список его цитату
        if not author in authors_info: # проверяем, есть ли автор в словаре авторов и сведений о них. Если нет - добавляем информацию
            bio_page_url = url + rq.find('a', href=True)['href'] # находим и сохраняем ссылку на веб-страницу со сведениями об авторе
            bio_page_raw = requests.get(bio_page_url, headers=headers) # делаем запрос к веб-странице со сведениями об авторе и сохраняем отет
            bio_page = BeautifulSoup(bio_page_raw.text, 'html.parser')# обрабатываем и сохраняем ответ через BeautifulSoup для поиска
            birth_date = bio_page.find(class_='author-born-date').text # находим и сохраняем дату рождения автора
            birth_place = bio_page.find(class_='author-born-location').text # находим и сохраняем место рождения автора
            description = bio_page.find(class_='author-description').text.strip() # находим и сохраняем сведения об авторе
            # при этом срезаем символы перевода строки - улучшаем читаемость и не мешаем машинной обработке
            authors_info[author] = {
                'date_of_birth': birth_date,  
                'place_of_birth': birth_place[3:],
                'description': description
                } # создаем словарь с датой, местом рождения и сведениями об авторе и записываем его как значение в словарь авторов
            #и сведений о них. Место рождения берем срезом с 3 элемента - т.к. первые 3 элемента это "in ", не несущие смысла
        raw_tags = rq.find_all(class_='tag') #находим и сохраняем тэги
        tags = [] # создаем список тэгов для последующего включения в словарь
        for rt in raw_tags: # идем циклом по найденным тэгам
            tag_text = rt.text # удаляем из тэга html-код, оставляем сам тэг
            quotes_by_tag[tag_text] = quotes_by_tag.get(tag_text, list()) # проверяем, есть ли тэг в словаре тэгов, 
            #если нет - создаем на месте значения пустой список
            quotes_by_tag[tag_text].append({quote_text: author}) # записываем к тэгу как ключу текст цитаты и автора как словарь
            tags.append(tag_text) # включаем тэг в список тэгов
            if not tag_text in tags_dictionary: # проверяем, есть ли тэг в словаре тэгов
                tags_dictionary[tag_text] = url + rt['href'] # если тэга нет, вносим тэг в словарь как ключ, url-ссылку по нему - как значение
        
        quotes.append(
        {
            'text': quote_text,
            'author': author,
            'tags': ", ".join(tags)
        } # добавляем в список цитат словарь с текстом цитаты, автором и строкой с тэгами
    )

url = 'https://quotes.toscrape.com/' # сохраняем URL нужного сайта
#большинство сайтов блокируют запросы, не содержащие корректного User-Agent. Конкретно с этим сайтом нет
#необходимости использовать User-Agent, но в код он включен, поскольку обычно требуется
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)# направляем запрос на веб-страницу и сохраняем ответ
response.raise_for_status()# проверяем, понял сервер запрос или нет. 
# Если не вызвать raise_for_status(), программа подумает, что всё в порядке, и отправит запрос на страницу, которой нет.
# В принципе, с данной страницей код работает и без этого.

page = BeautifulSoup(response.text, 'html.parser') # обрабатываем ответ через BeautifulSoup для дальнейшей работы с помощью его методов

parse_page(page) # применяем ранее созданную функцию для поиска и сохранения информации к главной странице

next_page_check = page.find(class_='next') # проверяем, если ли на веб-странице переход к следующей веб-странице

while next_page_check is not None: #запускаем цикл обработки всех страниц сайта с цитатами, пока есть переход к следующей
    next_page_url = url + next_page_check.find('a', href=True)['href'] #создаем адрес следующей страницы
    next_page = requests.get(next_page_url,headers=headers) #делаем запрос к новой странице и сохраняем ответ 
    next_page.raise_for_status() #проверяем, понял сервер запрос или нет
    page = BeautifulSoup(next_page.text, 'html.parser') #обрабатываем ответ через BeautifulSoup для дальнейшей работы 
    parse_page(page) #применяем функцию для поиска и сохранения информации к новой странице
    next_page_check = page.find(class_='next') #проверяем, если ли на веб-странице переход к следующей веб-странице

# записываем топ-10 тэгов в словарь
raw_top_tags = page.find(class_='col-md-4 tags-box') # находим топ-10 тэгов 
top_tags_list = [i.text for i in raw_top_tags.find_all(class_='tag')] # создаем список топ-10 тэгов
top_tags = {key: value for key, value in enumerate(top_tags_list, 1)} # сохраняем топ-10 тэгов как словарь. Ключ - порядковый номер, тэг - значение

# записываем основной файл с информацией - список словарей с цитатами, авторами и тэгами, словарем тэгов с url-адресами,
# словарь со сведениями об авторах
# ensure_ascii == True (по умолчанию) - с перекодированием нестандартных (не ASCII) символов и букв. 
# Хуже читаемость для человека, но ниже вероятность ошибок.
with open('quotes_big.json', 'w', encoding='utf-8') as file: # записываем JSON-файл
    for i in quotes, top_tags:
        json.dump(i, file, indent=1)# добавляем в JSON файл список цитат и топ тэгов без сортировки - сортировать цитаты нет нужды, 
        #топ тэгов уже отсортирован по популярности с 1 до 10
        file.write('\n\n') # добавляем двойной перевод строки для разделения блоков информации и улучшения читаемости
    for j in tags_dictionary, authors_info, quotes_by_author, quotes_by_tag:
        json.dump(j, file, indent=1, sort_keys=True) # добавляем в JSON файл словари тэгов, сведений об авторах, цитат 
        #по авторам и цитат по тэгам в сортированном виде по алфавиту
        file.write('\n\n') # добавляем двойной перевод строки для разделения блоков информации и улучшения читаемости

# записываем основной файл с информацией, ensure_ascii == False - 
# не перекодируем нестандартные символы - лучше читаемость, но могут быть проблемы с преобразованием в дальнейшем
with open('quotes_big_human_read.json', 'w', encoding='utf-8') as file:
    for i in quotes, top_tags:
        json.dump(i, file, indent=1, ensure_ascii=False) # добавляем в JSON файл список цитат и топ тэгов без сортировки - сортировать цитаты нет нужды, топ тэгов уже отсортирован
        file.write('\n\n') # добавляем двойной перевод строки для разделения блоков информации и улучшения читаемости
    for j in tags_dictionary, authors_info, quotes_by_author, quotes_by_tag:
        json.dump(j, file, indent=1, ensure_ascii=False, sort_keys=True) # добавляем в JSON файл словари тэгов, сведений об авторах, цитат по авторам и цитат по тэгам в сортированном виде по алфавиту
        file.write('\n\n') # добавляем двойной перевод строки для разделения блоков информации и улучшения читаемости

# поскольку представление данных у топа тэгов, цитат, словаря тэгов и словаря сведений об авторах отличается, запишем также отдельные файлы с ними 
# - так может быть удобнее для работы с данными

# файл с цитатами
with open('quotes_only.json', 'w', encoding='utf-8') as file:
    json.dump(quotes, file, indent=1)

# тот же файл, более читабельный для человека - ensure_ascii == False
with open('quotes_only_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes, file, indent=1, ensure_ascii=False)

# файл с топом тэгов. Поскольку в нем нет особых кодируемых символов, то отдельный файл без кодировки не создается
with open('top_tags.json', 'w', encoding='utf-8') as file:
    json.dump(top_tags, file, indent=1)

# файл со словарем тэгов и ссылок. Поскольку в нем нет не-ASII символов, то отдельный файл без кодировки не создается
with open('tags_dictionary.json', 'w', encoding='utf-8') as file:
    json.dump(tags_dictionary, file, indent=1, sort_keys=True) #

# файл со словарем авторов и сведений о них
with open('authors_info.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, sort_keys=True)

# тот же файл, более читабельный для человека
with open('authors_info_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, ensure_ascii=False, sort_keys=True)

# записываем файл со словарем, в котором авторы - ключи, а цитаты - значения
with open('quotes_by_author.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_author, file, indent=1, sort_keys=True)

# тот же файл, более читабельный для человека
with open('quotes_by_author_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_author, file, indent=1, ensure_ascii=False, sort_keys=True)

# записываем файл со словарем, в котором тэги - ключи, а цитаты - значения
with open('quotes_by_tag.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_tag, file, indent=1, sort_keys=True)

# тот же файл, более читабельный для человека
with open('quotes_by_tag_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_tag, file, indent=1, ensure_ascii=False, sort_keys=True)   

# добавляем в словарь сведений об авторах цитаты каждого автора. 
# Теперь по этому словарю по имени автора можно найти не только сведения о нем, но и его цитаты
for i in quotes:
    authors_info[i['author']]['quotes'] = authors_info[i['author']].get('quotes', list())
    authors_info[i['author']]['quotes'].append(i['text'])

#записываем словарь сведений об авторах с цитатами в файл
with open('authors_info_with_quotes.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, sort_keys=True)

#тот же файл, более читабельный для человека
with open('authors_info_with_quotes_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, sort_keys=True)
