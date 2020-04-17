# -*- coding: utf-8 -*-

from .movie_list import search_naver_movie
from .movie_detail import update_naver_movie
from .common_function import is_metadata_available, LibraryType
from .metadata_parser import parse_search_metadata, parse_detail_metadata


def Start():
    Log.Info('Naver Movie Agent started.')
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['Accept'] = 'text/html, application/json'


class NaverMovieAgent(Agent.Movies):
    name = 'Naver Movie Agent'
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang):
        metadata_exists = is_metadata_available(media=media, library_type=LibraryType.MOVIE)
        if metadata_exists:
            parse_search_metadata(media=media, lang=lang, results=results)
        else:
            search_naver_movie(results, media, lang)

    def update(self, metadata, media, lang):
        metadata_exists = is_metadata_available(media=media, library_type=LibraryType.MOVIE)
        if metadata_exists:
            parse_detail_metadata(media=media, metadata=metadata)
        else:
            update_naver_movie(metadata, media, lang)
