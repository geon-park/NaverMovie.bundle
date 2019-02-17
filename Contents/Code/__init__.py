# -*- coding: utf-8 -*-

import unicodedata
import urllib
from difflib import SequenceMatcher


MOVIE_SEARCH = 'https://auto-movie.naver.com/ac?q_enc=UTF-8&st=1&r_lt=1&n_ext=1&t_koreng=1&r_format=json&' \
               'r_enc=UTF-8&r_unicode=0&r_escape=1&q=%s'
MOVIE_DETAIL = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code=%s'
MOVIE_PHOTO_MAIN = 'https://movie.naver.com/movie/bi/mi/photoView.nhn?code=%s'
MOVIE_PHOTOS = 'https://movie.naver.com/movie/bi/mi/photoListJson.nhn?movieCode=%s&size=%d&offset=%d'


def Start():
    Log.Info('Naver Movie Agent started.')
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['Accept'] = 'text/html, application/json'


def calculate_match_score(media_name, title, media_year, year):
    score = int(85 * SequenceMatcher(None, media_name, title).ratio())
    if media_year == year:
        score += 15

    return score


# Get Movie List from Naver
def get_movie_list(media_name):
    json_url = MOVIE_SEARCH % urllib.quote(media_name.encode('utf8'))
    return JSON.ObjectFromURL(url=json_url)


# Get detail information for the movie
def get_movie_detail(metadata_id):
    return HTML.ElementFromURL(MOVIE_DETAIL % metadata_id)


# Get photo list for the movie
def get_movie_photos(metadata_id, category):
    html = HTML.ElementFromURL(MOVIE_PHOTO_MAIN % metadata_id)
    try:
        index = int(html.xpath('string(//ul[@id="photoTypeGroup"]/li[@imagetype="%s"]/@photoindex)' % category)) - 1
        size = int(html.xpath('//ul[@id="photoTypeGroup"]/li[@imagetype="%s"]/a/em' % category)[0].text)
    except ValueError:
        return None

    return JSON.ObjectFromURL(url=MOVIE_PHOTOS % (metadata_id, size, index))


def parse_movie_detail(html, metadata, media):
    metadata.title = html.xpath('//div[@class="mv_info"]/h3/a')[0].text
    metadata.original_title = html.xpath('//div[@class="mv_info"]/h3/strong')[0].text.split(',')[0].strip()
    metadata.year = int(html.xpath('//div[@class="mv_info"]/h3/strong')[0].text.split(',')[-1].strip())
    metadata.title_sort = unicodedata.normalize('NFKD', metadata.title[0])[0] + ' ' + metadata.title

    # 평점(관람객 -> 평론가 -> 네티즌)
    if ''.join(html.xpath('//a[@id="actualPointPersentWide"]/div/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('//a[@id="actualPointPersentWide"]/div/descendant::em/text()')))
    elif ''.join(html.xpath('(//a[@class="spc"])[0]/div/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('(//a[@class="spc"])[0]/div/descendant::em/text()')))
    elif ''.join(html.xpath('//a[@id="pointNetizenPersentWide"]/descendant::em/text()')):
        metadata.rating = float(''.join(html.xpath('//a[@id="pointNetizenPersentWide"]/descendant::em/text()')))

    # 장르
    genres = html.xpath('//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "genre")]/text()')
    for genre in genres:
        metadata.genres.add(genre.strip())

    # 국가
    countries = html.xpath(
        '//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "nation")]/text()')
    for country in countries:
        metadata.countries.add(country.strip())

    # 개봉일
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

    # 등급
    grade = ''.join(x.strip() for x in html.xpath(
        '//div[@class="mv_info"]/p[@class="info_spec"]//descendant::a[contains(@href, "grade")][1]/'
        'parent::span//descendant::text()'))

    match = Regex(u'\[국내\]([^\[]+)').search(grade)
    if match:
        metadata.content_rating  = match.group(1)
    elif Regex(u'\[해외\]([^\[]+)').search(grade):
        metadata.content_rating = Regex(u'\[해외\]([^\[]+)').search(grade).group(1)
    else:
        None

    # 줄거리
    summary = '\n'.join(x.strip() for x in html.xpath('//div[@class="story_area"]/h5[@class="h_tx_story"]/text()'))
    summary += '\n\n' + '\n'.join(x.strip() for x in html.xpath('//div[@class="story_area"]/p[@class="con_tx"]/text()'))
    metadata.summary = summary.strip()

    # metadata.duration = None


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

def search_naver_movie(results, media, lang):
    media_name = media.name
    media_name = unicodedata.normalize('NFKC', unicode(media_name)).strip()
    Log.Debug('Filename: %s, Media name: %s, Year: %s' % (media.filename, media_name, media.year))

    data = get_movie_list(media_name=media_name)
    items = data['items'][0]

    for item in items:
        # parse JSON data
        title, movie_id = item[0][0].decode('utf8'), item[5][0].decode('utf8')
        match = Regex(u'(\d{4})(\d{4})?').search(item[1][0].decode('utf8'))
        year = str(match.group(1)) if match else None
        score = calculate_match_score(media_name, title, str(media.year), year)
        Log.Info('media_name: %s, title: %s, id: %s, media_year: %s, year: %s, score: %s ' %
                 (media_name, title, movie_id, media.year, year, str(score)))
        results.Append(MetadataSearchResult(id=movie_id, name=title, year=year, score=score, lang=lang))


def update_naver_movie(metadata, media, lang):
    html = get_movie_detail(metadata.id)
    parse_movie_detail(html, metadata, media)

    for category in ['STILLCUT', 'POSTER']:
        photo_list = get_movie_photos(metadata.id, category)
        if not photo_list:
            continue

        parse_movie_photos(metadata, photo_list)


class NaverMovieAgent(Agent.Movies):
    name = 'Naver Movie Agent'
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang):
        return search_naver_movie(results, media, lang)

    def update(self, metadata, media, lang):
        update_naver_movie(metadata, media, lang)
