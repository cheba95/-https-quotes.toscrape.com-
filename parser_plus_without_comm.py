from bs4 import BeautifulSoup 
import requests 
import json 

quotes = [] 
tags_dictionary = {} 
authors_info = {} 
quotes_by_author = {} 
quotes_by_tag = {} 

def parse_page(page):
    raw_quotes = page.find_all(class_='quote') 
    for rq in raw_quotes: 
        quote_text = rq.find(class_='text').text.strip('“”') 
        author = rq.find(class_='author').text 
        quotes_by_author[author] = quotes_by_author.get(author, list()) 
        quotes_by_author[author].append(quote_text) 
        if not author in authors_info: 
            bio_page_url = url + rq.find('a', href=True)['href'] 
            bio_page_raw = requests.get(bio_page_url, headers=headers) 
            bio_page = BeautifulSoup(bio_page_raw.text, 'html.parser')
            birth_date = bio_page.find(class_='author-born-date').text 
            birth_place = bio_page.find(class_='author-born-location').text 
            description = bio_page.find(class_='author-description').text.strip() 
            authors_info[author] = {
                'date_of_birth': birth_date,  
                'place_of_birth': birth_place[3:],
                'description': description
                } 
            
        raw_tags = rq.find_all(class_='tag') 
        tags = [] 
        for rt in raw_tags: 
            tag_text = rt.text 
            quotes_by_tag[tag_text] = quotes_by_tag.get(tag_text, list()) 
            quotes_by_tag[tag_text].append({quote_text: author}) 
            tags.append(tag_text) 
            if not tag_text in tags_dictionary: 
                tags_dictionary[tag_text] = url + rt['href'] 
        
        quotes.append(
        {
            'text': quote_text,
            'author': author,
            'tags': ", ".join(tags)
        } 
    )

url = 'https://quotes.toscrape.com/' 

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
response.raise_for_status()

page = BeautifulSoup(response.text, 'html.parser') 

parse_page(page) 

next_page_check = page.find(class_='next') 

while next_page_check is not None: 
    next_page_url = url + next_page_check.find('a', href=True)['href'] 
    next_page = requests.get(next_page_url,headers=headers) 
    next_page.raise_for_status() 
    page = BeautifulSoup(next_page.text, 'html.parser') 
    parse_page(page) 
    next_page_check = page.find(class_='next') 

raw_top_tags = page.find(class_='col-md-4 tags-box') 
top_tags_list = [i.text for i in raw_top_tags.find_all(class_='tag')] 
top_tags = {key: value for key, value in enumerate(top_tags_list, 1)} 

with open('quotes_big.json', 'w', encoding='utf-8') as file: 
    for i in quotes, top_tags:
        json.dump(i, file, indent=1)
        file.write('\n\n') 
    for j in tags_dictionary, authors_info, quotes_by_author, quotes_by_tag:
        json.dump(j, file, indent=1, sort_keys=True) 
        file.write('\n\n') 

with open('quotes_big_human_read.json', 'w', encoding='utf-8') as file:
    for i in quotes, top_tags:
        json.dump(i, file, indent=1, ensure_ascii=False) 
        file.write('\n\n') 
    for j in tags_dictionary, authors_info:
        json.dump(j, file, indent=1, ensure_ascii=False, sort_keys=True) 
        file.write('\n\n')

with open('quotes_only.json', 'w', encoding='utf-8') as file:
    json.dump(quotes, file, indent=1)

with open('quotes_only_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes, file, indent=1, ensure_ascii=False)

with open('top_tags.json', 'w', encoding='utf-8') as file:
    json.dump(top_tags, file, indent=1)

with open('tags_dictionary.json', 'w', encoding='utf-8') as file:
    json.dump(tags_dictionary, file, indent=1, sort_keys=True) 

with open('authors_info.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, sort_keys=True)

with open('authors_info_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, ensure_ascii=False, sort_keys=True)

with open('quotes_by_author.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_author, file, indent=1, sort_keys=True)

with open('quotes_by_author_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_author, file, indent=1, ensure_ascii=False, sort_keys=True)

with open('quotes_by_tag.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_tag, file, indent=1, sort_keys=True)

with open('quotes_by_tag_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(quotes_by_tag, file, indent=1, ensure_ascii=False, sort_keys=True)   

for i in quotes:
    authors_info[i['author']]['quotes'] = authors_info[i['author']].get('quotes', list())
    authors_info[i['author']]['quotes'].append(i['text'])

with open('authors_info_with_quotes.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, sort_keys=True)

with open('authors_info_with_quotes_human_read.json', 'w', encoding='utf-8') as file:
    json.dump(authors_info, file, indent=1, ensure_ascii=False, sort_keys=True)