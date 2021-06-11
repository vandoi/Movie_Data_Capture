import os
import requests
from lxml import etree
from hanziconv import HanziConv

import config
from urllib.parse import urljoin

SUPPORT_PROXY_TYPE = ("http", "socks5", "socks5h")

conf = config.Config()
dict_gen = dict()
if os.path.exists(conf.translate_dict_path()):
    with open(conf.translate_dict_path(), "r") as f:
        lines = f.readlines() 
        for line in lines:
            res = line.split(',')
            dict_gen[res[0]] = res[1]

def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True


def getXpathSingle(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1


def get_proxy(proxy: str, proxytype: str = None) -> dict:
    ''' 获得代理参数，默认http代理
    '''
    if proxy:
        if proxytype in SUPPORT_PROXY_TYPE:
            proxies = {"http": proxytype + "://" + proxy, "https": proxytype + "://" + proxy}
        else:
            proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    else:
        proxies = {}

    return proxies


# 网页请求核心
def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None):
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    if ua is None:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"} # noqa
    else:
        headers = {"User-Agent": ua}

    for i in range(retry_count):
        try:
            if switch == '1' or switch == 1:
                result = requests.get(str(url), headers=headers, timeout=timeout, proxies=proxies, cookies=cookies)
            else:
                result = requests.get(str(url), headers=headers, timeout=timeout, cookies=cookies)

            result.encoding = "utf-8"

            if return_type == "object":
                return result
            else:
                return result.text

        except Exception as e:
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
            print("[-]" + str(e))
    print('[-]Connect Failed! Please check your Proxy or Network!')


def post_html(url: str, query: dict) -> requests.Response:
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"}

    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                result = requests.post(url, data=query, proxies=proxies,headers=headers, timeout=timeout)
            else:
                result = requests.post(url, data=query, headers=headers, timeout=timeout)
            return result
        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i+1, retry_count))
    print("[-]Connect Failed! Please check your Proxy or Network!")


def get_javlib_cookie() -> [dict, str]:
    import cloudscraper
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    raw_cookie = {}
    user_agent = ""

    # Get __cfduid/cf_clearance and user-agent
    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                raw_cookie, user_agent = cloudscraper.get_cookie_string(
                    "http://www.m45e.com/",
                    proxies=proxies
                )
            else:
                raw_cookie, user_agent = cloudscraper.get_cookie_string(
                    "http://www.m45e.com/"
                )
        except requests.exceptions.ProxyError:
            print("[-] ProxyError, retry {}/{}".format(i+1, retry_count))
        except cloudscraper.exceptions.CloudflareIUAMError:
            print("[-] IUAMError, retry {}/{}".format(i+1, retry_count))

    return raw_cookie, user_agent

def translateTag(tag):
    if conf.translate_to_tc():
        return translateTag_to_tc(tag)
    elif conf.translate_to_sc():
        return translateTag_to_sc(tag)
    else:
        return tag

def translateTag_to_tc(tag):   
    try:
        return dict_gen[tag]
    except:
        return tag

def translateTag_to_sc(tag):
    return HanziConv.toSimplified(translateTag_to_tc(tag, conf))

if __name__ == "__main__":
    print(translateTag("足コキ"))

def translate(src:str,target_language:str="zh_cn"):
    url = "https://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl=" + target_language + "&q=" + src
    result = get_html(url=url,return_type="object")

    translate_list = [i["trans"] for i in result.json()["sentences"]]

    return "".join(translate_list)

# 文件修改时间距此时的天数
def file_modification_days(filename) -> int:
    mfile = pathlib.Path(filename)
    if not mfile.exists():
        return 9999
    mtime = int(mfile.stat().st_mtime)
    now = int(time.time())
    days = int((now - mtime) / (24 * 60 * 60))
    if days < 0:
        return 9999
    return days

# 检查文件是否是链接
def is_link(filename: str):
    if os.path.islink(filename):
        return True # symlink
    elif os.stat(filename).st_nlink > 1:
        return True # hard link Linux MAC OSX Windows NTFS
    return False

# URL相对路径转绝对路径
def abs_url(base_url: str, href: str) -> str:
    if href.startswith('http'):
        return href
    return urljoin(base_url, href)
