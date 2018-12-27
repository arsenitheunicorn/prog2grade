import os
import sqlite3


def stem_file(path):
    file = 'mystem-' + path
    stem_list = []
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        t_list = text.split('\n')
    for line in t_list:
        if not line.startswith('@'):
            stem_list.append(line)
    stem = '\n'.join(stem_list)
    return stem


def crawling():
    db_dict = dict()
    years = os.listdir('plain')
    for year in years:
        y_path = os.path.join('plain', year)
        months = os.listdir(y_path)
        for month in months:
            m_path = os.path.join(y_path, month)
            titles = os.listdir(m_path)
            for art in titles:
                path = os.path.join(m_path, art)
                clean_t = []
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                t_list = text.split('\n')
                for line in t_list:
                    if line.startswith('@au'):
                        if 'None' in line:
                            author = ''
                        else:
                            author = line[4:]
                    elif line.startswith('@ti'):
                        title = line[4:]
                    elif line.startswith('@url'):
                        url = line[5:]
                    elif not line.startswith('@'):
                        clean_t.append(line)
                c_text = '\n'.join(clean_t)
                stem = stem_file(path)
                row = (url, title, author, c_text, stem)
                key = title + str(month) + ' ' + str(year)
                db_dict[key] = row
    return db_dict


def create_db(db_dict):
    conn = sqlite3.connect('resbash.db')
    c = conn.cursor()
    c.execute("""
CREATE TABLE IF NOT EXISTS paper(url text primary key, title text,
author text, article text, lemmatized_article text)"""
              )
    conn.commit()
    for key in db_dict:
        row = db_dict[key]
        c.execute('INSERT INTO paper VALUES (?, ?, ?, ?, ?)', row)
        conn.commit()
    conn.close()


def construct_base():
    db_dict = crawling()
    create_db(db_dict)


def main():
    if resbash.db not in os.listdir():
        construct_base()


if __name__ == "__main__":
    main()
