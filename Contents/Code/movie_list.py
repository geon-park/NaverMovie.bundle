from difflib import SequenceMatcher
import unicodedata
import urllib

MOVIE_SEARCH = 'https://movie.naver.com/movie/search/result.nhn?section=movie&query=%s&ie=utf8'


def calculate_match_score(media_name, title, media_year, year):
    score = int(60 * SequenceMatcher(None, media_name, title).ratio())
    return score + 40 if media_year == year else score


def get_movie_list(media_name):
    return HTML.ElementFromURL(MOVIE_SEARCH % urllib.quote(media_name.encode('utf8')), encoding='ms949')


def search_naver_movie(results, media, lang):
    media_name = media.name.upper()
    media_name = unicodedata.normalize('NFKC', unicode(media_name)).strip()
    Log.Debug('Filename: %s, Media name: %s, Year: %s' % (media.filename, media_name, media.year))

    html = get_movie_list(media_name=media_name)
    num_of_movies = html.xpath('count(//ul[@class="search_list_1"]/li)')
    for i in range(1, int(num_of_movies) + 1):
        title = ''.join(html.xpath('//ul[@class="search_list_1"]/li[' + str(i) + ']/dl/dt//text()'))

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

        movie_id = html.xpath(
            'substring-after(//ul[@class="search_list_1"]/li[' + str(i) + ']/dl/dt/a/@href, "code=")')
        year = html.xpath('//ul[@class="search_list_1"]/li[' + str(i) + ']//a[contains(@href, "year")]/text()')
        year = year[0] if len(year) != 0 else None
        score = calculate_match_score(media_name, title.upper(), str(media.year), year)
        Log.Info('media_name: %s, title: %s, id: %s, media_year: %s, year: %s, score: %d' %
                 (media_name, title, movie_id, media.year, year, score))
        results.Append(MetadataSearchResult(id=movie_id, name=title, year=year, score=score, lang=lang))
