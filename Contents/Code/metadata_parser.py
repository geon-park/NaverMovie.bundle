# -*- coding: utf-8 -*-

import json
import os
import urllib
from os.path import dirname, exists, join


def get_metadata_path(media):
    metadata_path = join(dirname(urllib.unquote(media.filename).decode('utf-8')), 'metadata.json')
    if exists(metadata_path):
        return metadata_path
    else:
        return None


def parse_metadata(results, lang, metadata_path):
    fd = os.open(metadata_path, os.O_RDONLY)
    f = os.fdopen(fd, 'rt')
    metadata = json.load(f)
    movie_id, title, year, score = metadata['id'], metadata['title'], metadata['year'], 100
    Log.Debug('From JSON metadata id: %s, title: %s, year: %s' % (movie_id, title, year))
    results.Append(MetadataSearchResult(id=movie_id, name=title, year=year, score=score, lang=lang))
