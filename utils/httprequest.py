# -*- coding: utf-8 -*-
import logger
import mechanicalsoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cloudscraper import create_scraper
import config

G_USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36'
G_DEFAULT_TIMEOUT = 10
G_DEFAULT_RETRY = 3

#
# 本应用中代理为全局配置，应用层不应关心其是否开启。在本类中自动读取配置文件。
#


def get_network_params():
    proxies = config.variables.G_PROXIES
    cacert_file = config.getStrValue("proxy.cacert_file")
    timeout = config.getIntValue("proxy.timeout")
    retry = config.getIntValue("proxy.retry")

    cacert_file = None if cacert_file == '' else cacert_file
    timeout = G_DEFAULT_TIMEOUT if timeout is None else timeout
    retry = G_DEFAULT_RETRY if retry is None else retry

    return proxies, timeout, retry, cacert_file


def get(url: str, cookies=None, ua: str = None, extra_headers=None, return_type: str = None, encoding: str = None):
    proxies, timeout, retry, verify = get_network_params()
    errors = ""
    headers = {"User-Agent": ua or G_USER_AGENT}
    if extra_headers != None:
        headers.update(extra_headers)
    for i in range(retry):
        try:
            result = requests.get(url, headers=headers, timeout=timeout, proxies=proxies,
                                  verify=verify, cookies=cookies)
            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                result.encoding = encoding or result.apparent_encoding
                return result.text
        except Exception as e:
            logger.info(f"Connect: {url} retry {i + 1}/{retry}")
            errors = str(e)
    
    if "getaddrinfo failed" in errors:
        logger.info("Connect Failed! Please Check your proxy config")
    else:
        logger.info('Connect Failed! Please check your Proxy or Network!')
        
    logger.info(errors)
    raise Exception('Connect Failed')


def post(url: str, data: dict=None, files=None, cookies=None, ua: str=None, return_type: str=None, encoding: str=None):
    proxies, timeout, retry, verify = get_network_params()
    errors = ""
    headers = {"User-Agent": ua or G_USER_AGENT}

    for i in range(retry):
        try:
            result = requests.post(url, data=data, files=files, headers=headers, timeout=timeout, proxies=proxies,
                                   verify=verify, cookies=cookies)
            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                result.encoding = encoding or result.apparent_encoding
                return result
        except Exception as e:
            logger.info(f"Connect: {url} retry {i + 1}/{retry}")
            errors = str(e)
            
        if "getaddrinfo failed" in errors:
            logger.info("Connect Failed! Please Check your proxy config")
        else:
            logger.info('Connect Failed! Please check your Proxy or Network!')
        logger.info(errors)
        raise Exception('Connect Failed')


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = G_DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def request_session(cookies=None, ua: str=None):
    proxies, timeout, retry, verify = get_network_params()
    session = requests.Session()
    retries = Retry(total=retry, connect=retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    if verify:
        session.verify = verify
    if proxies:
        session.proxies = proxies
    session.headers = {"User-Agent": ua or G_USER_AGENT}
    return session


# storyline xcity only
def get_html_by_form(url, form_select: str = None, fields: dict = None, cookies: dict = None, ua: str = None,
                     return_type: str = None, encoding: str = None):
    proxies, timeout, retry, verify = get_network_params()
    session = requests.Session()
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    retries = Retry(total=retry, connect=retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    if verify:
        session.verify = verify
    if proxies:
        session.proxies = proxies
    try:
        browser = mechanicalsoup.StatefulBrowser(user_agent=ua or G_USER_AGENT, session=session)
        result = browser.open(url)
        if not result.ok:
            return None
        form = browser.select_form() if form_select is None else browser.select_form(form_select)
        if isinstance(fields, dict):
            for k, v in fields.items():
                browser[k] = v
        response = browser.submit_selected()

        if return_type == "object":
            return response
        elif return_type == "content":
            return response.content
        elif return_type == "browser":
            return response, browser
        else:
            result.encoding = encoding or "utf-8"
            return response.text
    except requests.exceptions.ProxyError:
        logger.info("[-]get_html_by_form() Proxy error! Please check your Proxy")
    except Exception as e:
        logger.info(f'[-]get_html_by_form() Failed! {e}')
    return None

# storyline javdb only
def get_html_by_scraper(url: str = None, cookies: dict = None, ua: str = None, return_type: str = None, encoding: str = None):
    proxies, timeout, retry, verify = get_network_params()
    session = create_scraper(browser={'custom': ua or G_USER_AGENT, })
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    retries = Retry(total=retry, connect=retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=timeout))
    if verify:
        session.verify = verify
    if proxies:
        session.proxies = proxies
    try:
        if isinstance(url, str) and len(url):
            result = session.get(str(url))
        else:  # 空url参数直接返回可重用scraper对象，无需设置return_type
            return session
        if not result.ok:
            return None
        if return_type == "object":
            return result
        elif return_type == "content":
            return result.content
        elif return_type == "scraper":
            return result, session
        else:
            result.encoding = encoding or "utf-8"
            return result.text
    except requests.exceptions.ProxyError:
        logger.info("get_html_by_scraper() Proxy error! Please check your Proxy")
    except Exception as e:
        logger.info(f"get_html_by_scraper() failed. {e}")
    return None



def download(url, filepath, ua: str = None, extra_headers=None, cookies=None):
    proxies, timeout, retry, verify = get_network_params()
    headers = {"User-Agent": ua or G_USER_AGENT}
    if extra_headers != None:
        headers.update(extra_headers)
    errors = ""
    for i in range(3):
        try:
            r = requests.get(url=url, headers=headers, timeout=timeout, proxies=proxies,
                                  verify=verify, cookies=cookies)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return 
        except Exception as e:
            errors = str(e)
        logger.info(f"Connect: {url} retry {i + 1}/{retry}")
    
    if "getaddrinfo failed" in errors:
        logger.info("Connect Failed! Please Check your proxy config")
    else:
        logger.info('Connect Failed! Please check your Proxy or Network!')
        
    logger.info(errors)
    raise Exception('Connect Failed')