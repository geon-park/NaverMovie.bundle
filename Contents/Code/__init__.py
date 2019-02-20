# -*- coding: utf-8 -*-

import unicodedata
import urllib
from difflib import SequenceMatcher

MOVIE_SEARCH = 'https://movie.naver.com/movie/search/result.nhn?section=movie&query=%s'
MOVIE_DETAIL = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code=%s'
MOVIE_PHOTO_MAIN = 'https://movie.naver.com/movie/bi/mi/photoView.nhn?code=%s'
MOVIE_PHOTOS = 'https://movie.naver.com/movie/bi/mi/photoListJson.nhn?movieCode=%s&size=%d&offset=%d'
MOVIE_CAST = 'https://movie.naver.com/movie/bi/mi/detail.nhn?code=%s'


def Start():
    Log.Info('Naver Movie Agent started.')
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['Accept'] = 'text/html, application/json'


def calculate_match_score(media_name, title, media_year, year):
    score = int(85 * SequenceMatcher(None, media_name, title).ratio())
    return score + 15 if media_year == year else score


# Get Movie List from Naver
def get_movie_list(media_name):
    return HTML.ElementFromURL(MOVIE_SEARCH % urllib.quote(media_name.encode('euc_kr')))


# Get detail information for the movie
def get_movie_detail(metadata_id):
    return HTML.ElementFromURL(MOVIE_DETAIL % metadata_id)


# Get photo list for the movie
def get_movie_photos(metadata_id, category):
    html = HTML.ElementFromURL(MOVIE_PHOTO_MAIN % metadata_id)
    try:
        index = int(html.xpath('string(//ul[@id="photoTypeGroup"]/li[@imagetype="%s"]/@photoindex)' % category)) - 1
        size = int(html.xpath('//ul[@id="photoTypeGroup"]/li[@imagetype="%s"]/a/em' % category)[0].text)
    except Exception:
        return None

    return JSON.ObjectFromURL(url=MOVIE_PHOTOS % (metadata_id, size, index))


# Get Actors, Directors, Producers, Writers information
def get_movie_cast(metadata_id):
    return HTML.ElementFromURL(url=MOVIE_CAST % metadata_id)


def parse_movie_detail(html, metadata):
    metadata.title = html.xpath('//div[@class="mv_info"]/h3/a')[0].text
    metadata.original_title = html.xpath('//div[@class="mv_info"]/h3/strong')[0].text.split(',')[0].strip()
    metadata.year = int(html.xpath('//div[@class="mv_info"]/h3/strong')[0].text.split(',')[-1].strip())
    metadata.title_sort = unicodedata.normalize('NFKD', metadata.title[0])[0] + ' ' + metadata.title

    # Rating (actualPointPersent -> spc -> pointNetizenPersent)
    if ''.join(html.xpath('//a[@id="actualPointPersentWide"]/div/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('//a[@id="actualPointPersentWide"]/div/descendant::em/text()')))
    elif ''.join(html.xpath('(//a[@class="spc"])[0]/div/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('(//a[@class="spc"])[0]/div/descendant::em/text()')))
    elif ''.join(html.xpath('//a[@id="pointNetizenPersentWide"]/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('//a[@id="pointNetizenPersentWide"]/descendant::em/text()')))

    # Genres
    genres = html.xpath('//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "genre")]/text()')
    for genre in genres:
        metadata.genres.add(genre.strip())

    # Countries
    countries = html.xpath(
        '//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "nation")]/text()')
    for country in countries:
        metadata.countries.add(country.strip())

    # Release date
    originally_available_at = ''.join(x.strip() for x in html.xpath(
        '//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "open")][1]/'
        'parent::span//descendant::text()'))
    match = Regex(u'(\d{4}\.\d{2}\.\d{2})\s*개봉').search(originally_available_at)
    if match:
        metadata.originally_available_at = Datetime.ParseDate(match.group(1)).date()
    elif Regex(u'(\d{4}\.\d{2}\.\d{2})\s*재개봉').search(originally_available_at):
        match = Regex(u'(\d{4}\.\d{2}\.\d{2})\s*재개봉').search(originally_available_at)
        metadata.originally_available_at = Datetime.ParseDate(match.group(1)).date()
    else:
        metadata.originally_available_at = None

    # Film rating
    content_rating = ''.join(x.strip() for x in html.xpath(
        '//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "grade")][1]/'
        'parent::span//descendant::text()'))

    match = Regex(u'\[국내\]([^\[]+)').search(content_rating)
    if match:
        metadata.content_rating = match.group(1)
    elif Regex(u'\[해외\]([^\[]+)').search(content_rating):
        metadata.content_rating = Regex(u'\[해외\]([^\[]+)').search(content_rating).group(1)
    else:
        None

    # Story
    summary = '\n'.join(x.strip() for x in html.xpath('//div[@class="story_area"]/h5[@class="h_tx_story"]/text()'))
    summary += '\n\n' + '\n'.join(x.strip() for x in html.xpath('//div[@class="story_area"]/p[@class="con_tx"]/text()'))
    metadata.summary = summary.strip()

    # Duration
    # metadata.duration = 0


def parse_movie_photos(metadata, photo_list):
    photo_info = {'STILLCUT': [5, metadata.art], 'POSTER': [5, metadata.posters]}
    items = photo_list['lists']
    index = 0
    for item in items:
        try:
            index += 1
            url = item['fullImageUrl']
            photo_info[category][1][url] = Proxy.Preview(HTTP.Request(url), sort_order=index)
            if photo_info[category][0] == index:
                break
        except Exception:
            pass


def parse_movie_cast(html, metadata):
    # Actors
    metadata.roles.clear()
    xpath_base = '//div[@class="made_people"]//ul[@class="lst_people"]/li'
    num_of_actors = html.xpath('count(%s)' % xpath_base)
    for i in range(1, int(num_of_actors) + 1):
        actor = metadata.roles.new()
        name = html.xpath(xpath_base + '[' + str(i) + ']/div[@class="p_info"]/a[@class="k_name"]/text()')
        actor.name = name[0].decode('utf8') if len(name) != 0 else None
        photo = html.xpath(xpath_base + '[' + str(i) + ']/p[@class="p_thumb"]//img/@src')
        actor.photo = photo[0] if len(photo) != 0 else None
        role = html.xpath(xpath_base + '[' + str(i) + ']/div[@class="p_info"]//p[@class="pe_cmt"]/span/text()')
        actor.role = role[0].decode('utf8') if len(role) != 0 else None
        Log.Info('Actor Info: %s, %s, %s' % (actor.name, actor.photo, actor.role))
    # Directors
    metadata.directors.clear()
    xpath_base = '//div[@class="director"]//div[@class="dir_obj"]'
    num_of_directors = html.xpath('count(%s)' % xpath_base)
    for i in range(1, int(num_of_directors) + 1):
        director = metadata.directors.new()
        name = html.xpath(xpath_base + '[' + str(i) + ']/p[@class="thumb_dir"]//img/@alt')
        director.name = name[0].decode('utf8') if len(name) != 0 else None
        photo = html.xpath(xpath_base + '[' + str(i) + ']/p[@class="thumb_dir"]//img/@src')
        director.photo = photo[0] if len(photo) != 0 else None
        Log.Info('Director Info: %s, %s' % (director.name, director.photo))
    # Producers
    metadata.producers.clear()
    xpath_base = u'//table[@class="staff_lst"]/tbody//img[@alt="제작"]/parent::th/following-sibling::td/span'
    num_of_producer = html.xpath(u'count(%s)' % xpath_base)
    for i in range(1, int(num_of_producer) + 1):
        producer = metadata.producers.new()
        name = html.xpath('%s[%d]/a/text()' % (xpath_base, i))
        producer.name = name[0].decode('utf8') if len(name) != 0 else None
        Log.Info('Producer Info: %s, %s' % (producer.name, producer.photo))
    # Writers
    metadata.writers.clear()
    xpath_base = u'//table[@class="staff_lst"]/tbody//img[@alt="각본"]/parent::th/following-sibling::td/span'
    num_of_writer = html.xpath(u'count(%s)' % xpath_base)
    for i in range(1, int(num_of_writer) + 1):
        writer = metadata.writers.new()
        name = html.xpath('%s[%d]/a/text()' % (xpath_base, i))
        writer.name = name[0].decode('utf8') if len(name) != 0 else None
        Log.Info('Writer Info: %s, %s' % (writer.name, writer.photo))


def search_naver_movie(results, media, lang):
    media_name = media.name
    media_name = unicodedata.normalize('NFKC', unicode(media_name)).strip()
    Log.Debug('Filename: %s, Media name: %s, Year: %s' % (media.filename, media_name, media.year))

    html = get_movie_list(media_name=media_name)
    num_of_movies = html.xpath('count(//ul[@class="search_list_1"]/li)')
    for i in range(1, int(num_of_movies) + 1):
        title = ''.join(x.decode('utf8') for x in html.xpath(
            '//ul[@class="search_list_1"]/li[' + str(i) + ']/dl/dt//text()')).strip()

        # Remove the original name part
        num_of_brackets = 0
        if title[-1] == ')':
            for index, c in enumerate(reversed(title)):
                if c == ')':
                    num_of_brackets = num_of_brackets + 1
                elif c == '(':
                    num_of_brackets = num_of_brackets - 1
                if num_of_brackets <= 0:
                    title = title[:-index - 1].strip()
                    break

        movie_id = html.xpath('substring-after(//ul[@class="search_list_1"]/li[' + str(i) + ']/dl/dt/a/@href, "code=")')
        year = html.xpath('//ul[@class="search_list_1"]/li[' + str(i) + ']//a[contains(@href, "year")]/text()')[0]
        year = year if year else None
        score = calculate_match_score(media_name, title, str(media.year), year)
        Log.Info('media_name: %s, title: %s, id: %s, media_year: %s, year: %s, score: %d ' %
                 (media_name, title, movie_id, media.year, year, score))
        results.Append(MetadataSearchResult(id=movie_id, name=title, year=year, score=score, lang=lang))


def update_naver_movie(metadata, media, lang):
    html = get_movie_detail(metadata.id)
    parse_movie_detail(html, metadata)

    for category in ['STILLCUT', 'POSTER']:
        photo_list = get_movie_photos(metadata.id, category)
        if not photo_list:
            continue
        parse_movie_photos(metadata, photo_list)

    html = get_movie_cast(metadata_id=metadata.id)
    parse_movie_cast(html, metadata)


class NaverMovieAgent(Agent.Movies):
    name = 'Naver Movie Agent'
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang):
        return search_naver_movie(results, media, lang)

    def update(self, metadata, media, lang):
        update_naver_movie(metadata, media, lang)
