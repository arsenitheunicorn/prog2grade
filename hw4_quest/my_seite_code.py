import json
import urllib.request
import csv
from flask import Flask
from flask import render_template, request

app = Flask(__name__)
metatable = 'results_dag.csv'
tags = ['name', 'age', 'town', 'lang']
for i in range(1, 6):
    word = 'word' + str(i)
    tags.append(word)

@app.route(r'/')
def startseite():
    return render_template('startseite.html')

@app.route(r'/results',  methods=['POST'])
def results():
    if request.method == 'POST':
        name = request.form[tags[0]]
        age = request.form[tags[1]]
        town = request.form[tags[2]]
        lang = request.form[tags[3]]
        word1 = request.form[tags[4]]
        word2 = request.form[tags[5]]
        word3 = request.form[tags[6]]
        word4 = request.form[tags[7]]
        word5 = request.form[tags[8]]
        final = 'Баркала, '
        items = [name, age, town, lang, word1, word2, word3, word4, word5]
        row_dict = {}
        for i in range(0, len(items)):
            row_dict[tags[i]] = items[i]
        with open(metatable, 'a+', encoding='utf-8') as tabfile:
            writer = csv.DictWriter(tabfile, fieldnames=tags)
            writer.writerow(row_dict)
        final += name + '!'
        return render_template('results.html', final=final)

@app.route(r'/stats')
def stats():
    with open(metatable, 'r', encoding='utf-8') as content:
        content = csv.reader(content)
        return render_template('stats.html', content=content)

@app.route(r'/json')
def jsonpage():
    dict_csv = {}
    with open(metatable, 'r+', encoding='utf-8') as tabfile:
        reader = csv.DictReader(tabfile, fieldnames=tags)
        for row in reader:
            person = row['name'] + row['age'] + '_' + row['town']
            dict_csv[person] = json.loads(json.dumps(row))
    return render_template('json.html', json=dict_csv)

@app.route(r'/search')
def suche():
    return render_template('search.html')

@app.route(r'/found', methods=['POST'])
def found():
    dict_freq = {}
    if request.method == 'POST':
        lang = request.form['lang_search']
        f_word = request.form['word_search']
        with open(metatable, 'r', encoding='utf-8') as tabfile:
            reader = csv.DictReader(tabfile, fieldnames=tags)
            for row in reader:
                if row['lang'] == lang:
                    if row[f_word] != '0':
                        if row[f_word] in dict_freq:
                            dict_freq[row[f_word]] += 1
                        else:
                            dict_freq[row[f_word]] = 1
        lang_dict = {'az': 'азербайджанском', "rus": "русском",
                     "agul": "агульском", "lezg": "лезгинском",
                     "drgw": "даргвинском", "tab": "табасаранском"}
        w_dict = {"word1": "Гусеница", "word2": "Желток",
                  "word3": "Молния", "word4": "Палец ноги",
                  "word5": "Паутина"}
        haupt = "Результат поиска слова " + w_dict[f_word] + " в "
        haupt += lang_dict[lang] + " языке:"
        return render_template('found.html', haupt=haupt, found=dict_freq)

if __name__ == '__main__':
    app.run(debug=True)
