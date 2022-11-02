from time import time
import requests
import aiohttp
import hmac
import hashlib
import urllib3
from configs.config import SYSTEM_PROXY, Config
from urllib.parse import urlencode
try:
    import ujson as json
except:
    import json

nonce = "b1ab87b4800d4d4590a11701b8551afa"
api_key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
secret_key = r"~d}$Q7$eIni=V)9\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
base = "https://picaapi.picacomic.com"
categories = ["重口地帶","Cosplay","歐美","禁書目錄","WEBTOON","東方","Fate","SAO 刀劍神域","Love Live","艦隊收藏","非人類","強暴","NTR","人妻","足の恋","性轉換","SM","妹妹系","姐姐系","扶他樂園","後宮閃光","偽娘哲學","耽美花園","百合花園","純愛","生肉","英語 ENG","CG雜圖","碧藍幻想","圓神領域","短篇","長篇","全彩","嗶咔漢化"]
orders = {"ua":"默认","dd":"新到旧","da":"旧到新","ld":"最多爱心","vd":"最多指名"}
token_me = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1ZmU0ZDE5MzM4MTcyOTQzOTFmZGNmOTAiLCJlbWFpbCI6IjExNDcwMzY5OTEiLCJyb2xlIjoibWVtYmVyIiwibmFtZSI6IkNDeWVsbG93c3RhciIsInZlcnNpb24iOiIyLjIuMS4yLjMuMyIsImJ1aWxkVmVyc2lvbiI6IjQ0IiwicGxhdGZvcm0iOiJhbmRyb2lkIiwiaWF0IjoxNjY3MzA1MDk2LCJleHAiOjE2Njc5MDk4OTZ9.k5dfLmsNQBt-u4Fk-eKR8yVr-YdYtHp5KjWpmNwFKiU"
init = True
urllib3.disable_warnings()
proxy = SYSTEM_PROXY
pica_account = Config.get_config("zhenxun_plugin_pica", "pica_account")
pica_password = Config.get_config("zhenxun_plugin_pica", "pica_password")
class Pica:
    Order_Default = "ua"  # 默认
    Order_Latest = "dd"  # 新到旧
    Order_Oldest = "da"  # 旧到新
    Order_Loved = "ld"  # 最多爱心
    Order_Point = "vd"  # 最多指名

    def __init__(self) -> None:
        self.__s = requests.session()
        self.__s.proxies = "http://127.0.0.1:10809"
                            
        self.__s.verify = False
        self.headers = {
            "api-key":           api_key,
            "accept":            "application/vnd.picacomic.com.v1+json",
            "app-channel":       "2",
            "nonce":             nonce,
            "app-version":       "2.2.1.2.3.3",
            "app-uuid":          "defaultUuid",
            "app-platform":      "android",
            "app-build-version": "44",
            "Content-Type":      "application/json; charset=UTF-8",
            "User-Agent":        "okhttp/3.8.1",
            "image-quality":     "original",
            "time":              int(time()),
        }

    async def http_do(self, method, url, json=""):
        try:
            await self.login(pica_account, pica_password)
            init = False
        except Exception as e:
            init = True
            raise Exception(f"登录失败！{e}")
        header = self.headers.copy()
        ts = str(int(time()))
        raw = url.replace("https://picaapi.picacomic.com/",
                          "") + str(ts) + nonce + method + api_key
        raw = raw.lower()
        hc = hmac.new(secret_key.encode(), digestmod=hashlib.sha256)
        hc.update(raw.encode())
        header["signature"] = hc.hexdigest()
        header["time"] = ts
        print(header)
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                rs = await session.get(url=url, proxy=self.__s.proxies, headers=header, allow_redirects=True, verify_ssl=False, timeout=30)
            if method == "POST":
                if json == "":
                    rs = await session.post(url=url, proxy=self.__s.proxies, headers=header, allow_redirects=True, verify_ssl=False, timeout=30)
                else:
                    rs = await session.post(url=url, proxy=self.__s.proxies, headers=header, data=json, allow_redirects=True, verify_ssl=False, timeout=30)
        return rs

    async def http_do2(self, method, url, json):

        header = self.headers.copy()
        ts = str(int(time()))
        raw = url.replace("https://picaapi.picacomic.com/",
                          "") + str(ts) + nonce + method + api_key
        raw = raw.lower()
        hc = hmac.new(secret_key.encode(), digestmod=hashlib.sha256)
        hc.update(raw.encode())
        header["signature"] = hc.hexdigest()
        header["time"] = ts

        async with aiohttp.ClientSession() as session:
            if method == "GET":
                rs = await session.get(url=url, headers=header, proxy=self.__s.proxies, allow_redirects=True, verify_ssl=False, timeout=30)
            if method == "POST":
                rs = await session.post(url=url, proxy=self.__s.proxies, headers=header, data=json, allow_redirects=True, verify_ssl=False, timeout=30)
        return rs       

    async def login(self, email, password):
        api = "/auth/sign-in"
        url = base + api
        send = {"email": str(email), "password": str(password)}
        print(send)
        try:
            __a = await self.http_do2(method="POST", url=url, json=json.dumps(send))
            __a =await __a.text()
            print(__a)
            self.headers["authorization"] = json.loads(__a)["data"]["token"]

            init = False
        except Exception as e:
            raise Exception(f"登录失败！{e}")
        return self.headers["authorization"]

    async def comics(self, block="", tag="", order="", page=1):
        args = []
        if len(block) > 0:
            args.append(("c", block))
        if len(tag) > 0:
            args.append(("t", tag))
        if len(order) > 0:
            args.append(("s", order))
        if page > 0:
            args.append(("page", str(page)))
        params = urlencode(args)
        url = f"{base}/comics?{params}"
        res = await self.http_do(method="GET", url=url)
        print(await res.json())
        return await res.json()

    async def comic_info(self, book_id):
        url = f"{base}/comics/{book_id}"
        return await self.http_do(method="GET", url=url)

    async def episodes(self, book_id, page=1):
        url = f"{base}/comics/{book_id}/eps?page={page}"
        return await self.http_do(method="GET", url=url)

    async def picture(self, book_id, ep_id=1, page=1):
        url = f"{base}/comics/{book_id}/order/{ep_id}/pages?page={page}"
        return await self.http_do(method="GET", url=url)

    async def recomm(self, book_id):
        url = f"{base}/comics/{book_id}/recommendation"
        return await self.http_do(method="GET", url=url)

    async def keyword(self):
        url = f"{base}/keywords"
        return await self.http_do(method="GET", url=url)

    async def search(self, keyword, categories=[], sort=Order_Default, page=1):
        jso={
            "categories": categories,
            "keyword": keyword,
            "sort": sort,
        }
        url = f"{base}/comics/advanced-search?page={page}"
        return await self.http_do(method="POST", url=url, json=json.dumps(jso))

    async def like(self, book_id):
        url = f"{base}/comics/{book_id}/like"
        return await self.http_do(method="POST", url=url)

    async def get_comment(self, book_id, page=1):
        url = f"{base}/comics/{book_id}/comments?page={page}"
        return await self.http_do(method="GET", url=url)

    async def favourite(self, book_id):
        url = f"{base}/comics/{book_id}/favourite"
        return await self.http_do(method="POST", url=url)

    async def my_favourite(self, page=1, order=Order_Default):
        url = f"{base}/users/favourite?s={order}&page={page:1}"
        return await self.http_do(method="GET", url=url)

    async def categories(self):
        url = "https://picaapi.picacomic.com/categories"
        return await self.http_do(method="GET", url=url)

'''
if __name__ == "__main__":
    p = Pica()
    p.login("sagiri233.remain.1", "Aa123456")
    p.comics(order=Pica.Order_Latest)
    p.comic_info("62b6932c9b7955744875c8b7")
    p.episodes("62b6932c9b7955744875c8b7", 1)
    p.picture("62b6932c9b7955744875c8b7", 1, 1)
    p.recomm("62b6932c9b7955744875c8b7")
    p.keyword()
    p.search("loli")
    p.like("62b6932c9b7955744875c8b7") # 喜欢
    p.like("62b6932c9b7955744875c8b7") # 取消喜欢
    p.get_comment("62b6932c9b7955744875c8b7")
    p.favourite("62b6932c9b7955744875c8b7") # 收藏
    p.favourite("62b6932c9b7955744875c8b7") # 取消收藏
    p.favourite("62b6932c9b7955744875c8b7")
    p.my_favourite()
'''
