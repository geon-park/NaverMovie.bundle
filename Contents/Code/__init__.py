# -*- coding: utf-8 -*-

import unicodedata
from .movie_list import search_naver_movie
from .movie_detail import update_naver_movie


def Start():
    Log.Info('Naver Movie Agent started.')
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'


class NaverMovieAgent(Agent.Movies):
    name = 'Naver Movie Agent'
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang):
        return search_naver_movie(results, media, lang)

    def update(self, metadata, media, lang):
        update_naver_movie(metadata, media, lang)
