# -*- coding: utf-8 -*-

import json
import os
import unicodedata
import urllib
from os.path import dirname, exists, join
from .content_rating import get_content_rating


def get_search_metadata_path(media):
    metadata_path = join(dirname(urllib.unquote(media.filename).decode('utf-8')), 'metadata.json')
    if exists(metadata_path):
        return metadata_path
    else:
        return None


def is_search_metadata_available(media):
    return True if get_search_metadata_path(media) is not None else False


def parse_search_metadata(media, lang, results):
    metadata_path = join(dirname(urllib.unquote(media.filename).decode('utf-8')), 'metadata.json')
    with os.fdopen(os.open(metadata_path, os.O_RDONLY), 'rt') as f:
        json_data = json.load(f)
        movie_id, title, year, score = json_data['id'], json_data['title'], json_data['year'], 100
        Log.Debug('From JSON metadata id: %s, title: %s, year: %s' % (movie_id, title, year))
        results.Append(MetadataSearchResult(id=movie_id, name=title, year=year, score=score, lang=lang))


def get_detail_metadata_path(media):
    metadata_path = join(dirname(urllib.unquote(media.items[0].parts[0].file).decode('utf-8')), 'metadata.json')
    if exists(metadata_path):
        return metadata_path
    else:
        return None


def is_detail_metadata_available(media):
    metadata_path = get_detail_metadata_path(media=media)
    if metadata_path is None:
        return False

    with os.fdopen(os.open(metadata_path, os.O_RDONLY), 'rt') as f:
        json_data = json.load(f)
        if 'detail' in json_data:
            return True
        else:
            return False


def parse_detail_metadata(media, metadata):
    metadata_path = get_detail_metadata_path(media)
    with os.fdopen(os.open(metadata_path, os.O_RDONLY), 'rt') as f:
        json_data = json.load(f)
        detail = json_data['detail']

        metadata.title = media.title
        metadata.year = int(json_data['year'])
        metadata.title_sort = unicodedata.normalize('NFKD', metadata.title[0])[0] + ' ' + metadata.title

        # Basic Information
        if 'original_title' in detail:
            metadata.original_title = detail['original_title']
        if 'rating' in detail:
            metadata.rating = float(detail['rating'])
        if 'originally_available_at' in detail:
            metadata.originally_available_at = Datetime.ParseDate(detail['originally_available_at']).date()
        if 'content_rating' in detail:
            metadata.content_rating = get_content_rating(detail['content_rating'], Prefs['content_rating'])
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

        # Post & Art
        if 'photos' in detail:
            photo_types = [['posters', Prefs['max_num_posters'], metadata.posters],
                           ['arts', Prefs['max_num_arts'], metadata.art]]
            photos = detail['photos']
            for photo_type in photo_types:
                if photo_type[0] in photos:
                    for photo_url in photos[photo_type[0]]:
                        index = 0
                        try:
                            index += 1
                            url = photo_url
                            photo_type[2][url] = Proxy.Preview(HTTP.Request(url), sort_order=index)
                            if photo_type[1] <= index:
                                break
                        except Exception:
                            Log.Error('Error with photo information: %s (Index: %d)' % (metadata.title, index))

        Log.Debug('Metadata for %s is parsed from JSON' % metadata.title)
