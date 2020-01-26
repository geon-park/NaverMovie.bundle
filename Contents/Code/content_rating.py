# -*- coding: utf-8 -*-

content_ratings = {
    '전체 관람가': {'KMRB': '전체 관람가', 'MPAA': 'G'},
    '12세 관람가': {'KMRB': '12세 관람가', 'MPAA': 'PG'},
    '15세 관람가': {'KMRB': '15세 관람가', 'MPAA': 'PG-13'},
    '청소년 관람불가': {'KMRB': '청소년 관람불가', 'MPAA': 'R'},
    '제한상영가': {'KMRB': '청소년 관람불가', 'MPAA': 'NC-17'},
    '등급보류': {'KMRB': '등급보류', 'MPAA': 'NR'},
    'G': {'KMRB': '전체 관람가', 'MPAA': 'G'},
    'PG': {'KMRB': '12세 관람가', 'MPAA': 'PG'},
    'PG-13': {'KMRB': '15세 관람가', 'MPAA': 'PG-13'},
    'R': {'KMRB': '청소년 관람불가', 'MPAA': 'R'},
    'NC-17': {'KMRB': '청소년 관람불가', 'MPAA': 'NC-17'},
    'X[NC-17]': {'KMRB': '청소년 관람불가', 'MPAA': 'NC-17'},
    'NR': {'KMRB': '등급보류', 'MPAA': 'NR'},
}


def get_content_rating(rating, country='KMRB'):
    return content_ratings[rating][country]
