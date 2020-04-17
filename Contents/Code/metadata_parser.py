# -*- coding: utf-8 -*-

import json
import os
import unicodedata
import urllib
from os.path import dirname, exists, join
from .common_function import get_metadata_path, set_multimedia_info, LibraryType
from .content_rating import get_content_rating


def parse_search_metadata(media, lang, results):
    metadata_path = get_metadata_path(media=media, library_type=LibraryType.MOVIE)
    json_data = json.loads(Core.storage.load(metadata_path))
    id, title, year, score = json_data['id'], json_data['title'], json_data['year'], 100
    Log.Debug('From JSON metadata id: %s, title: %s, year: %s' % (id, title, year))
    results.Append(MetadataSearchResult(id=id, name=title, year=year, score=score, lang=lang))


def parse_detail_metadata(media, metadata):
    metadata_path = get_metadata_path(media=media, library_type=LibraryType.MOVIE)
    json_data = json.loads(Core.storage.load(metadata_path))

    # Basic Information
    detail = json_data['detail']
    metadata.title = media.title
    metadata.year = int(json_data['year'])
    metadata.title_sort = unicodedata.normalize('NFKD', metadata.title[0])[0] + ' ' + metadata.title
    metadata.original_title = detail['original_title'] if 'original_title' in detail else media.title
    if 'originally_available_at' in detail:
        metadata.originally_available_at = Datetime.ParseDate(detail['originally_available_at']).date()
    if 'studio' in detail:
        metadata.studio = detail['studio']
    if 'content_rating' in detail:
        metadata.content_rating = get_content_rating(detail['content_rating'], Prefs['content_rating'])
    if 'rating' in detail:
        metadata.rating = float(detail['rating'])
    if 'summary' in detail:
        metadata.summary = detail['summary']

    info_types = [['genres', metadata.genres], ['countries', metadata.countries]]
    for info_type in info_types:
        if info_type[0] in detail:
            [info_type[1].add(info) for info in detail[info_type[0]]]

    # Actors
    metadata.roles.clear()
    if 'roles' in detail:
        for info in detail['roles']:
            actor = metadata.roles.new()
            actor.name = info['name'] if 'name' in info else None
            actor.photo = info['photo'] if 'photo' in info else None
            actor.role = info['role'] if 'role' in info else None

    # Directors & Producers & Writers
    person_types = [['directors', metadata.directors], ['producers', metadata.producers],
                    ['writers', metadata.writers]]

    for person_type in person_types:
        if person_type[0] in detail:
            person_type[1].clear()
            for person in detail[person_type[0]]:
                new_person = person_type[1].new()
                new_person.name = person['name']
                new_person.photo = person['photo']

    # Theme
    if 'themes' in json_data:
        set_multimedia_info(metadata_path, metadata.themes, detail['themes'], Prefs['max_num_themes'])

    # Poster & Art
    if 'photos' in detail:
        photo_types = [
            ['posters', Prefs['max_num_posters'], metadata.posters],
            ['art', Prefs['max_num_art'], metadata.art],
            ['banners', Prefs['max_num_banners'], metadata.banners]
        ]

        photos = detail['photos']
        for photo_type in photo_types:
            if photo_type[0] in photos:
                set_multimedia_info(metadata_path, photo_type[2], photos[photo_type[0]], photo_type[1])

    Log.Debug('Metadata for %s is parsed from JSON' % metadata.title)
