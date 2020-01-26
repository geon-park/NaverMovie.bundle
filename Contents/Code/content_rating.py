# -*- coding: utf-8 -*-

content_ratings = {
    u'전체 관람가': {u'KMRB': u'전체 관람가', u'MPAA': u'G'},
    u'12세 관람가': {u'KMRB': u'12세 관람가', u'MPAA': u'PG'},
    u'15세 관람가': {u'KMRB': u'15세 관람가', u'MPAA': u'PG-13'},
    u'청소년 관람불가': {u'KMRB': u'청소년 관람불가', u'MPAA': u'R'},
    u'제한상영가': {u'KMRB': u'청소년 관람불가', u'MPAA': u'NC-17'},
    u'등급보류': {u'KMRB': u'등급보류', u'MPAA': u'NR'},
    u'G': {u'KMRB': u'전체 관람가', u'MPAA': u'G'},
    u'PG': {u'KMRB': u'12세 관람가', u'MPAA': u'PG'},
    u'PG-13': {u'KMRB': u'15세 관람가', u'MPAA': u'PG-13'},
    u'R': {u'KMRB': u'청소년 관람불가', u'MPAA': u'R'},
    u'NC-17': {u'KMRB': u'청소년 관람불가', u'MPAA': u'NC-17'},
    u'X[NC-17]': {u'KMRB': u'청소년 관람불가', u'MPAA': u'NC-17'},
    u'NR': {u'KMRB': u'등급보류', u'MPAA': u'NR'},
}


def get_content_rating(rating, country='KMRB'):
    return content_ratings[rating][country]
