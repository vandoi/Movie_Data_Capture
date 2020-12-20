import sys
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
from datetime import datetime

# BaDoinkVR has shared structure, just change these arugments would be ok
studio_name='BaDoinkVR'
source_name='badoinkvr.py'
root_url='https://badoinkvr.com'
search_url='https://badoinkvr.com/vrpornvideos/search/'

def getTitle(a): # OK
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath("//h1[contains(@class, 'video-title')]/text()")[0]
    return result
def getRuntime(a): #OK
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    raw_time = html.xpath('//p[contains(@class, "video-duration")]/text()')[0]
    results = re.findall("Duration: ([0-9]+) min", raw_time)
    return results[0]
def getOutline(htmlcode): #OK
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = html.xpath('//p[contains(@class, "video-description")]/@content')[0]
    return result
def getActor(a): #OK @return ['actor1', 'actor2']
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    results = html.xpath('//a[contains(@class, "video-actor-link")]/text()')
    return results
def getRelease(a): #OK
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    raw_release = html.xpath('//p[contains(@class, "video-upload-date")]/text()')[0]
    date_str = raw_release.split(':')[1].strip() # e.g.: Uploaded: December 09, 2019
    # print(date_str)
    try:
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        release_str = date_obj.strftime('%Y-%m-%d')
    except Exception as err:
        print("[-]Unable to parse release: {}".format(str(err)))
    return release_str
def getYear(getRelease): #OK
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease
def getTag(a): #OK
    html = etree.fromstring(a, etree.HTMLParser())
    results = html.xpath('//a[contains(@class, "video-tag")]/text()')
    return results
def getCover(htmlcode): #OK
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    # e.g. [' https://img2.badoink.com/content/scenes/324863/the-penis-game-324863.jpg?q=80&w=920 920w', ' https://img2.badoink.com/content/scenes/324863/the-penis-game-324863.jpg?q=80&w=960 960w']
    imgs = html.xpath("//a[contains(@class, 'video-image-container')]/picture/source/@srcset")[0].split(',')
    # get the largest image as cover, which is the last one
    cover_url = imgs[-1].strip().split(' ')[0]
    return cover_url
def getCover_small(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    # e.g. [' https://img2.badoink.com/content/scenes/324863/the-penis-game-324863.jpg?q=80&w=920 920w', ' https://img2.badoink.com/content/scenes/324863/the-penis-game-324863.jpg?q=80&w=960 960w']
    imgs = html.xpath("//a[contains(@class, 'video-image-container')]/picture/source/@srcset")[0].split(',')
    # get the largest image as cover, which is the last one
    try:
        cover_url = imgs[24].strip().split(' ')[0] # 24-th is 500w
    except Exception as err:
        cover_url = imgs[-1].strip().split(' ')[0] # if 24-th not exists, use the largest one
    return cover_url

def getActorPhoto(a): #//*[@id="star_qdt"]/li/a/img
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    actor_name = html.xpath('//a[contains(@class, "video-actor-link")]/text()')
    actor_url = html.xpath('//a[contains(@class, "video-actor-link")]/@href')

    d = {}
    for name, url in zip(actor_name, actor_url):
        target_url = root_url + url
        query = get_html(target_url)
        html = etree.fromstring(query, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        imgs = html.xpath("//div[contains(@class, 'girl-details-photo-content')]/picture/source/@srcset")[0].split(',')
        # get the largest image as actor image, which is the last one
        cover_url = imgs[-1].strip().split(' ')[0]
        p={name:cover_url}
        d.update(p)
    return d

# def getNum(a):
#     html = etree.fromstring(a, etree.HTMLParser())
#     result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
#     result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
#     return str(result2 + result1).strip('+')
## Below information doesn't provided in BadoinkVR website
# def getStudio(a):
#     html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
#     result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
#     result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
#     return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
# def getLabel(a):
#     html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
#     result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
#     result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
#     return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
# def getDirector(a):
#     html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
#     result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
#     result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
#     return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
# def getSeries(a):
#     #/html/body/section/div/div[3]/div[2]/nav/div[7]/span/a
#     html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
#     result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
#     result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
#     return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')

def main(keyword):
    # replace spacebar with %20 in keyword
    html_keyword = keyword.replace(' ', '%20')
    try:
        # number = number.upper()
        try:
            target_url = search_url + html_keyword
            # print(target_url)
            query_result = get_html(target_url)
        except Error as err:
            print("[-]Unable to retrieve page from url {}".format(target_url))

        # with open(html_keyword + ".html", 'w') as f:
        #     f.write(query_result)

        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        # print(html)

        # badoink sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls=html.xpath('//*[contains(@class, "video-card")]/a/@href')
        ids=html.xpath('//*[contains(@class, "video-card")]/@data-video-card-scene-id')
        # print("urls: {}".format(urls))
        # print("ids: {}".format(ids))

        # we just assume the first one is the one we want
        correct_index = 0
        correct_url = urls[correct_index]
        number = ids[correct_index]
        detail_page = get_html(root_url + correct_url)

        # with open(html_keyword + "_detail.html", 'w') as f:
        #     f.write(detail_page)

        # # no cut image by default
        # imagecut = 3
        # # If gray image exists ,then replace with normal cover
        # cover_small = getCover_small(query_result, index=ids.index(number))
        # if 'placeholder' in cover_small:
        #     # replace wit normal cover and cut it
        #     imagecut = 1
        #     cover_small = getCover(detail_page)

        # number = getNum(detail_page)
        # title = getTitle(detail_page)
        # if title and number:
        #     # remove duplicate title
        #     title = title.replace(number, '').strip()

        dic = {
            'number': number,
            'actor': getActor(detail_page),
            'actor_photo': getActorPhoto(detail_page),
            'title': getTitle(detail_page),
            'outline': getOutline(detail_page),
            'runtime': getRuntime(detail_page),
            'release': getRelease(detail_page),
            'year': getYear(getRelease(detail_page)),
            'tag': getTag(detail_page),
            'cover': getCover(detail_page),
            'cover_small': getCover_small(detail_page),
            'website': search_url + correct_url,
            'source': source_name,
            'studio': studio_name,
            'imagecut': 3, # don't cut
            'director': "",
            'label': "",
            'series': "",
        }
        print(dic)
    except Exception as e:
        print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js
    # return

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    print(main('ipx-292'))
