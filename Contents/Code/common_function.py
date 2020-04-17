# -*- coding: utf-8 -*-

import json
import os
import urlparse

METADATA_URL = 'http://127.0.0.1:32400/library/metadata/%s'


class LibraryType:
    def __init__(self):
        pass

    MOVIE = 0
    TV = 1


def get_library_metadata(id):
    HTTP.Headers['Accept'] = 'text/html, application/json'
    return JSON.ObjectFromURL(url=METADATA_URL % id)


def get_metadata_path(media, library_type):
    metadata = get_library_metadata(media.id)
    if library_type == LibraryType.TV:
        media_path = metadata['MediaContainer']['Metadata'][0]['Location'][0]['path']
    else:
        media_path = os.path.dirname(metadata['MediaContainer']['Metadata'][0]['Media'][0]['Part'][0]['file'])
    metadata_path = os.path.join(media_path, 'metadata.json')
    if os.path.exists(metadata_path):
        return metadata_path
    else:
        return None


def is_search_metadata_available(media, library_type):
    return True if get_metadata_path(media, library_type) is not None else False


def is_detail_metadata_available(media, library_type):
    metadata_path = get_metadata_path(media, library_type)
    if not metadata_path:
        return False
    json_data = json.loads(Core.storage.load(metadata_path))
    return True if 'detail' in json_data else False


def check_url_path(path):
    if urlparse.urlparse(path).scheme in ('http', 'https'):
        return True
    else:
        return False


def load_multimedia_data(url, index):
    if check_url_path(url):
        result = Proxy.Preview(HTTP.Request(url), sort_order=index)
        Log.Debug('Photo (%s) is loaded from URL' % url)
    else:
        result = Proxy.Media(Core.storage.load(url), sort_order=index)
        Log.Debug('Photo (%s) is loaded from File' % url)
    return result


def set_multimedia_info(metadata_path, metadata, url_list, max_num):
    index = 0
    for url in url_list:
        try:
            index += 1
            if not check_url_path(url):
                url = os.path.join(os.path.dirname(metadata_path), url)
            metadata[url] = load_multimedia_data(url=url, index=index)
            if max_num <= index:
                break
        except Exception:
            Log.Error('Error with media information: %s (Index: %d)' % (url, index))
