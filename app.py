from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re
from markupsafe import escape
import urllib.parse


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

title_text = []
link_text = []
source_text = []
date_text = []
contents_text = []


@app.route('/<location>/<int:sort>/<s_date>/<e_date>')
def hello_world(location, sort, s_date, e_date):

    result = crawler(2, escape(location), escape(sort), escape(s_date), escape(e_date))
    print(result)
    return jsonify(result)


def crawler(maxpage, location, sort, s_date, e_date):
    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    page = 1
    maxpage_t = (int(maxpage)-1)*10+1 # 11= 2페이지 21=3페이지 31=4페이지 ...81=9페이지 , 91=10페이지, 101=11페이지
    urllib.parse.quote(location)

    separate = ''
    if sort == 0:
        separate = 'so%3Ar%2Cp%3Afrom' + s_from + 'to' + e_to + '2Ca%3A'
    elif sort == 1:
        separate = 'so%3add%2Cp%3Afrom' + s_from + 'to' + e_to + '2Ca%3A'
    elif sort == 2:
        separate = 'so%3Ada%2Cp%3Afrom' + s_from + 'to' + e_to + '2Ca%3A'

    while page <= maxpage_t:
        request_parameter = {'where': 'news', 'query': location, 'sort': sort, 'ds': s_date, 'de': e_date, 'nso': separate, 'start': str(page)}
        url = "https://search.naver.com/search.naver"
        response = requests.get(url, params=request_parameter)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        atags = soup.select('._sp_each_title')
        for atag in atags:
            title_text.append(atag.text)
            link_text.append(atag['href'])

        source_lists = soup.select('._sp_each_source')
        for source_list in source_lists:
            source_text.append(source_list.text)

        date_lists = soup.select('.txt_inline')
        for date_list in date_lists:
            test = date_list.text
            date_cleansing(test)

        contents_lists = soup.select('ul.type01 dl')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)

        result = {"date": date_text, "title": title_text, "source": source_text,
                  "contents": contents_text, "link": link_text}
        page += 10
        return result


def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '',
                                      str(contents)).strip()
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '',
                                       first_cleansing_contents).strip()
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)


def date_cleansing(test):
    try:
        pattern = '\d+.(\d+).(\d+).'  # 정규표현식

        r = re.compile(pattern)
        match = r.search(test).group(0)  # 2018.11.05.
        date_text.append(match)

    except AttributeError:
        pattern = '\w* (\d\w*)'  # 정규표현식

        r = re.compile(pattern)
        match = r.search(test).group(1)
        # print(match)
        date_text.append(match)


if __name__ == '__main':
    app.run()
