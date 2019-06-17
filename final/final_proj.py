import json
import re
import requests
from time import mktime
from datetime import datetime
import pymorphy2
import matplotlib.pyplot as plt
from matplotlib import style
from numpy import polyfit
import numpy as np
from scipy.interpolate import interp1d
from wordcloud import WordCloud


def vk(method, params):
    api_req = 'https://api.vk.com/method/'
    api_req += method + '?'
    j = ['{}={}'.format(key, params[key]) for key in params]
    api_req += '&'.join(j)
    json_raw = requests.get(api_req).text
    return json.loads(json_raw)


def robotdate(s):
    d = mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
    return d


def humandate(udate):
    x = '%Y-%m-%d %H:%M:%S'
    d = datetime.fromtimestamp(udate).strftime(x)
    return d


def get_the_age(bdate):
    td_str = str(datetime.today())
    td_list = td_str[:10].split('-')
    td = [int(td_list[2]), int(td_list[1]), int(td_list[0])]
    bd_list = bdate.split('.')
    bd = [int(bd_list[0]), int(bd_list[1]), int(bd_list[2])]
    if bd[1] > td[1]:
        age = td[2] - bd[2] - 1
    elif bd[1] < td[1]:
        age = td[2] - bd[2]
    else:
        if bd[0] > td[0]:
            age = td[2] - bd[2] - 1
        elif bd[0] <= td[0]:
            age = td[2] - bd[2]
    return age


def wall_dl(base_params, d1, d2):
    m = 'wall.get'
    res = vk(m, base_params)
    if 'response' in res:
        post_amount = res["response"]["count"]
        params = base_params.copy()
        i = 0
        posts = []
        texts = ''
        while i < post_amount:
            params['offset'] = str(i)
            if post_amount - i >= 100:
                count = 100
            else:
                count = post_amount - i
            params['count'] = str(count)
            result = vk(m, params)
            for j in range(count):
                items = result['response']['items'][j]
                date_unix = items['date']
                if date_unix > d1 and date_unix < d2:
                    text = items["text"]
                    post_id = items["id"]
                    posts.append(post_id)
                    texts += text
            i += 100
    else:
        posts = ''
        texts = res['error']['error_msg']
    return posts, texts


def work_with_text(text, morph):
    text = re.sub('[\t\n]', ' ', text)
    text = re.sub('[^А-Яа-яЁёA-Za-z -]', '', text)
    text = re.sub(r'\s+(\s)', r'\1', text)
    text.lower()
    words = text.split()
    freq = {}
    with open('stops.txt', 'r', encoding='utf-8') as f:
        stops = f.read().split('\n')
    for word in words:
        p = morph.parse(word)[0]
        lem = p.normal_form
        if lem not in stops:
            if lem not in freq:
                freq[lem] = 1
            else:
                freq[lem] += 1
    message = []
    for item in sorted(freq, key=freq.get, reverse=True)[:10]:
        mess = [item, freq[item]]
        message.append(mess)
    return message, freq


def snooping(base_params, user_id):
    params = base_params.copy()
    del params['owner_id']
    del params['filter']
    params['user_id'] = user_id
    params['fields'] = 'city,sex,bdate'
    m = 'users.get'
    u_info = vk(m, params)
    if 'response' in u_info:
        info = u_info['response'][0]
        if 'sex' in info:
            if info['sex'] == 1:
                sex = 'Ж'
            elif info['sex'] == 2:
                sex = 'М'
            else:
                sex = ''
        if 'city' in info:
            city = info['city']['title']
        else:
            city = ''
        if 'bdate' in info and info['bdate'].count('.') == 2:
            age = get_the_age(info['bdate'])
        else:
            age = 0
    else:
        sex = ''
        city = ''
        age = ''
    return [sex, city, age]


def comments(base_params, posts):
    u_dict = {}
    m = 'wall.getComments'
    params = base_params.copy()
    del params['filter']
    for post_id in posts:
        params['post_id'] = post_id
        res = vk(m, params)
        c_amount = len(res["response"]['items'])
        i = 0
        while i < c_amount:
            params['offset'] = str(i)
            if c_amount - i >= 100:
                count = 100
            else:
                count = c_amount - i
            params['count'] = c_amount
            result = vk(m, params)
            for j in range(count):
                com_wb = result['response']['items'][j]
                if 'from_id' in com_wb:
                    user_id = com_wb['from_id']
                    user_info = snooping(base_params, user_id)
                    if user_id > 0:
                        if user_id not in u_dict:
                            u_dict[user_id] = [user_info, 1]
                        else:
                            u_dict[user_id][1] += 1
            i += 100
    return u_dict


def stats_for_graphs(u_dict):
    sex = {}
    cities = {}
    ages = {}
    u_freq = {}
    for user in u_dict:
        info = u_dict[user][0]
        s = info[0]
        c = info[1]
        a = info[2]
        if s not in sex:
            sex[s] = 1
        else:
            sex[s] += 1
        if c not in cities:
            cities[c] = 1
        else:
            cities[c] += 1
        if a not in ages:
            ages[a] = 1
        else:
            ages[a] += 1
        u_freq[user] = u_dict[user][1]
    return sex, cities, ages, u_freq


def bars_city(d):
    style.use('dark_background')
    x = []
    y = []
    for item in sorted(d, key=d.get, reverse=True)[:20]:
        if item != "":
            x.append(item)
            y.append(d[item])
        if len(x) >= 15:
            break
    plt.bar(x, y)
    gtitle = "Топ городов комментаторов"
    plt.title(gtitle)
    plt.ylabel("Количество комментаторов из города")
    r = 'vertical'
    plt.tight_layout()
    plt.xticks(range(len(x)), [i for i in x], rotation=r)
    filename = 'static/city.png'
    plt.savefig(filename)
    plt.close()


def bars_sex(d):
    x = []
    y = []
    gtitle = "Количество комментаторов каждого пола"
    for item in d:
        if item != '':
            x.append(item)
            y.append(d[item])
    plt.bar(x, y)
    style.use('dark_background')
    plt.title(gtitle)
    plt.ylabel("Количество человек")
    plt.xticks(range(len(x)), [i for i in x])
    filename = 'static/sex.png'
    plt.savefig(filename)
    plt.close()


def graph_age(d):
    x = []
    y = []
    for item in sorted(d, reverse=False):
        if item != '':
            x.append(item)
            y.append(d[item])
    coefficients = polyfit(x, y, 4)
    p = np.poly1d(coefficients)
    x_p = np.linspace(0, max(x), 1000)
    style.use('dark_background')
    plt.plot(x_p, p(x_p), c='red')
    gtitle = "Количество комментаторов по возрастам"
    plt.title(gtitle)
    plt.scatter(x, y)
    xname = 'Возраст'
    yname = 'Количество'
    plt.xlabel(xname)
    plt.ylabel(yname)
    filename = 'static/age.png'
    plt.savefig(filename, dpi=300)
    plt.close()


def top_comments(d, base_params):
    mt = 'users.get'
    params = base_params.copy()
    del params['owner_id']
    del params['filter']
    userids = []
    comms = []
    for user in sorted(d, key=d.get, reverse=True)[:5]:
        userids.append(str(user))
        comms.append(d[user])
    params['user_ids'] = ','.join(userids)
    params['fields'] = 'bdate,city'
    params['name_case'] = 'Nom'
    j = vk(mt, params)
    ml = []
    r = 'комментари'
    for i, u in enumerate(j['response']):
        fn = u['first_name']
        ln = u['last_name']
        n = fn + ' ' + ln
        if 'bdate' in u:
            bd = u['bdate']
        else:
            bd = '00.0'
        if 'city' in u:
            ct = u['city']['title']
        else:
            ct = 'Город N'
        c = comms[i]
        ya = [2, 3, 4]
        if c % 10 == 1:
            f = "ий"
        elif c % 10 in ya:
            f = 'я'
        else:
            f = "ев"
#        m = '%s,\t%s,\t%s:\t%s %s%s' % (n, bd, ct, c, r, f)
        crf = str(c) + ' ' + r + f
        m = [n, bd, ct, crf]
        ml.append(m)
    return ml


def make_cloud(freq):
    text = ''
    for word in freq:
        k = freq[word]
        wl = [word for i in range(k)]
        text += ' '.join(wl)
    cloud = WordCloud(background_color="white", max_words=150)
    cloud.generate(text)
    plt.imshow(cloud, interpolation='bilinear')
    cloud.to_file("static/cloud.png")
    plt.close()


def almain(vkid, rd1, rd2):
    f = open('tok.txt', 'r')
    tok = f.read()
    d1 = robotdate(rd1)
    d2 = robotdate(rd2)
    base_params = {'access_token': tok,
                  'v': '5.95', 'owner_id': vkid,
                  'filter': 'owner'}
    posts, text = wall_dl(base_params, d1, d2)
    return posts, text, base_params


def main(posts, text, base_params):
    morph = pymorphy2.MorphAnalyzer()
    message, freq = work_with_text(text, morph)
    u_dict = comments(base_params, posts)
    g_sex, g_city, g_age, u_freq = stats_for_graphs(u_dict)
    bars_city(g_city)
    bars_sex(g_sex)
    graph_age(g_age)
    mes = top_comments(u_freq, base_params)
    make_cloud(freq)
    return message, mes
