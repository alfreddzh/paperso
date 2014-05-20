#!../manage/exec-in-virtualenv.sh
# -*- coding: UTF-8 -*-
# File: dbsearch.py
# Date: Tue May 20 14:42:25 2014 +0800
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import operator

from ukdbconn import get_mongo
from uklogger import *
from lib.textutil import title_beautify, levenshtein

def beautify_results():
    def wrap(func):
        def call(query):
            res = func(query.lower())
            for k in res:
                k['title'] = title_beautify(k['title'])
            return res
        return call
    return wrap

@beautify_results()
def search_exact(query):
    db = get_mongo('paper')
    res = list(db.find({'title': query},
                       {'view_cnt': 1, 'download_cnt': 1, 'title': 1}
                      ))
    return res

@beautify_results()
def search_startswith(query):
    db = get_mongo('paper')
    res = list(db.find({'title': {'$regex': '^{0}'.format(query) } },
                       {'view_cnt': 1, 'download_cnt': 1, 'title': 1}
                      ))
    return res

@beautify_results()
def search_regex(regex):
    db = get_mongo('paper')
    res = list(db.find({'title': {'$regex':
                                  '{0}'.format(query) }
                       }, {'view_cnt': 1, 'download_cnt': 1, 'title': 1}
                      ))
    return res

all_titles = []
def similar_search(query):
    """ return one result that is most similar to query"""
    ret = []
    query = query.strip().lower()
    for cand in all_titles:
        dist = levenshtein(query, cand[0])
        if dist < 5:
            ret.append((cand, dist))
    if not ret:
        return None
    res = max(ret, key=operator.itemgetter(1))

    db = get_mongo('paper')
    res = db.find_one({'_id': res[0][1]},
                      {'view_cnt': 1, 'download_cnt': 1, 'title': 1})
    return res


def add_title_for_similar_search(cand):
    """ cand = (title, id) """
    all_titles.append((cand[0].strip().lower(), cand[1]))

def init_title_for_similar_search():
    global all_titles
    all_titles = []
    db = get_mongo('paper')
    itr = db.find({}, {'title': 1})
    for cand in itr:
        add_title_for_similar_search((cand['title'], cand['_id']))

if __name__ == '__main__':
    init_title_for_similar_search()
    print similar_search('test file')
