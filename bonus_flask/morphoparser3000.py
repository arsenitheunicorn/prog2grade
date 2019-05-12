import pymorphy2
import re
import random
import os

def cleaning(text):
    text = re.sub('[\t\n]', ' ', text)
    text = re.sub('[^А-Яа-яЁё -]', '', text)
    text = re.sub('\s+(\s)', r'\1', text)
    return text

def get_text(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        rtext = f.read()
        text = cleaning(rtext)
        words = text.split(' ')
    return words

def get_lemmas(words, morph):
    lemm_dict = {}
    for token in words:
        p = morph.parse(token)[0]
        lemma = p.normal_form
        tags = str(p.tag)
        if len(tags) <= 4:
            pos = p.tag.POS
            gram = ''
        elif tags[4] == ',':
            pos, rest = tags.split(',', maxsplit=1)
            gram = rest.split(' ')[0]
        elif tags[4] == ' ':
            pos = p.tag.POS
            gram = ''
        if pos in lemm_dict:
            if gram in lemm_dict[pos]:
                lemm_dict[pos][gram].append(lemma)
            else:
                lemm_dict[pos][gram] = [lemma]
        else:
            lemm_dict[pos] = {gram: [lemma]}
    return lemm_dict

def preps(morph):
    text = get_text('grossman.txt')
    lemm_dict = get_lemmas(text, morph)
    return lemm_dict

def parsing_req(sentence, morph):
    text = re.sub('([А-Яа-я0-9])[.,?!:;]+([А-Яа-я0-9Ёё])', r'\1 \2', sentence)
    text = re.sub('[^А-Яа-я0-9Ёё -]', '', text)
    text = re.sub('\s+(\s)', r'\1', text)
    words = text.split(' ')
    commands = []
    for word in words:
        p = morph.parse(word)[0]
        lem = p.normal_form
        tags = str(p.tag)
        if not re.search('[, ]', tags):
            pos = tags
            gram = ''
            flex = ''
        else:
            if tags[4] == ',':
                pos, rest = tags.split(',', maxsplit=1)
                if ' ' in rest:
                    gram, flex = rest.split(' ', maxsplit=1)
                else:
                    gram = rest
                    flex = ''
            else:
                pos, flex = rest.split(' ', maxsplit=1)
                gram = ''
        com = (pos, gram, flex, lem)
        commands.append(com)
    return commands

def answermachine(morph, lemm_dict, commands):
    flex = []
    for item in commands:
        if item[0] in lemm_dict:
            if item[1] in lemm_dict[item[0]]:
                words = lemm_dict[item[0]][item[1]]
            else:
                oth_keys = lemm_dict[item[0]].keys()
                if item[0] in ['NOUN', 'VERB', 'GRND', 'INFN', 'PRTF', 'PRTS']:
                    main_key = item[1].split(',')[1]
                    for gr in oth_keys:
                        if main_key in gr:
                            further_key = gr
                            break
                elif item[0] == 'NPRO':
                    for tag in item[1].split(','):
                        if tag.endswith('per'):
                            main_key = tag
                    for gr in oth_keys:
                        if main_key in gr:
                            further_key = gr
                            break
                elif item[1] <= 4:
                    further_key = random.choice(oth_keys)
                words = lemm_dict[item[0]][further_key]
            eq_words = list(set(words))
            answer = random.choice(eq_words)
            if len(eq_words) > 1:
                while answer == item[3]:
                    answer = random.choice(eq_words)
            elif len(eq_words) == 1:
                answer = random.choice(eq_words)
            else:
                answer = item[3]
            fl = (answer, item[2])
        else:
            fl = (item[3], item[2])
        flex.append(fl)
    finalwords = ''
    for pair in flex:
        p = morph.parse(pair[0])[0]
        gramemes = pair[1].split(',')
        if gramemes[0] != '':
            if p.tag.POS != 'NPRO':
                frz = frozenset(gramemes)
                fin = p.inflect(frz).word
            else:
                fin = pair[0]
        else:
            fin = pair[0]
        finalwords += fin
        finalwords += ' '
    return finalwords.strip()

def main(sentence):
    morph = pymorphy2.MorphAnalyzer()
    lemm_dict = preps(morph)
    commands = parsing_req(sentence, morph)
    answer = answermachine(morph, lemm_dict, commands)
    return answer

if __name__ == '__main__':
    print(os.listdir())