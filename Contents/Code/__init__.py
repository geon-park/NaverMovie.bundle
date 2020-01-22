# -*- coding: utf-8 -*-

from .movie_list import search_naver_movie
from .movie_detail import update_naver_movie
from .metadata_parser import is_search_metadata_available, parse_search_metadata, \
    is_detail_metadata_available, parse_detail_metadata


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
        metadata_exists = is_search_metadata_available(media=media)
        if metadata_exists:
            return parse_search_metadata(media=media, lang=lang, results=results)
        else:
            return search_naver_movie(results, media, lang)

    def update(self, metadata, media, lang):
        metadata_exists = is_detail_metadata_available(media=media)
        if metadata_exists:
            parse_detail_metadata(media=media, metadata=metadata)
        else:
            update_naver_movie(metadata, media, lang)
