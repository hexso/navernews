# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from time_control import GetTimeList, GetNowTime
from excel import WriteInfoToCsv, ReadExcel
import requests
import pandas as pd
import os
import time
#csv에 저장하는 함수를 따로 짜자.
#중복체크하는 함수 따로 만들기





class NaverNewsCrawling:

    classCategory = 'a'

    SEARCH_FROM_YEAR = 2020
    SEARCH_FROM_MONTH = 1
    SEARCH_FROM_DAY = 10
    WAIT_SECONDS = 60
    # 259금융, 258증권, 261산업재계, 771중기벤처, 260부동산, 262글로벌경제 310생활경제, 263겨에일반
    # 264청와대, 265국회, 267국방외교,
    #cateGory = [258, 259, 260, 261, 262, 263, 264, 265, 310, 771]
    cateGory = [258]
    #중복 체크를 위한 사전
    last_news = dict()

    def start_class(self):

        #self.CrawlNaverNews()
        self.ContinueGettingNews()


    #실시간으로 업데이트 되는 뉴스를 parsing 한다.
    def ContinueGettingNews(self):
        while 1:
            now_day = GetNowTime()
            for c in self.cateGory:
                url_info = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2={0}&sid1=100&date={1}&page=1".format(c, now_day)
                try:
                    news_url_list = self.ParseNewsURL(url_info)

                    for idx, news_url in enumerate(news_url_list):
                        news_class = self.GetNewsContent(news_url)
                        #중복체크하기
                        if self.CheckLastNews(news_class, idx) == True:
                            print('중복')
                            break

                        #엑셀에 저장하기
                        WriteInfoToCsv(news_class, self.classCategory)

                except Exception as e:
                    print(e)
                    pass
            time.sleep(WAIT_SECONDS)


    #특정날짜부터 현재날짜까지의 뉴스를 찾는다.
    def CrawlNaverNews(self):

        pageNum = 50
        dateTime = GetTimeList(self.SEARCH_FROM_YEAR, self.SEARCH_FROM_MONTH, self.SEARCH_FROM_DAY)
        #sdi 2의 카테고리에 따라서 페이지를 접속한다.
        #sdi 1은 무시되는것 같다.
        for c in self.cateGory:
            for t in dateTime:
                for p in range(1, pageNum, 1):
                    url_info = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2={0}&sid1=100&date={1}&page={2}".format(c,t,p)
                    print(url_info)
                    try:
                         news_url_list = self.ParseNewsURL(url_info)
                         for news_url in news_url_list :
                            news_class = self.GetNewsContent(news_url)
                            WriteInfoToCsv(news_class, self.classCategory)
                    except:
                        pass


    #이 함수의 경우 인자로 url을 받는다
    #뉴스들의 url을 parsing한다.
    def ParseNewsURL(self, url_info):

        response = requests.get(url_info)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        html_newslist = soup.select("#main_content > div.list_body.newsflash_body > ul.type06_headline > li > dl > dt:nth-child(1) > a")
        self.classCategory = soup.select('h3')[1].text
        news_url_list = list()

        for n in html_newslist:
            url_info = n.get('href')
            news_url_list.append(url_info)

        html_newslist = soup.select("#main_content > div.list_body.newsflash_body > ul.type06 > li > dl > dt:nth-child(1) > a")
        for n in html_newslist:
            url_info = n.get('href')
            news_url_list.append(url_info)

        return news_url_list

    #뉴스정보들을 parsing한다.
    #return 값은 사전 형식
    def GetNewsContent(self, url_info):

        news_class = dict()
        response = requests.get(url_info)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        news_class['source'] = soup.find_all('meta')[5].get('content')
        #news_class['category'] = soup.find_all('meta')[6].get('content')
        news_class['category'] = self.classCategory
        news_class['date'] = soup.find_all("span","t11")[0].text
        news_class['title'] = soup.select("#articleTitle")[0].text.encode('euc-kr','ignore').decode('euc-kr')
        news_class['content'] = soup.select("#articleBodyContents")[0].text.encode('euc-kr','ignore').decode('euc-kr')
        news_class['url'] = url_info
        return news_class


    #사전에 카테고리별로 저장해서, 제목이랑 비교한다.
    #중복일 경우는 True를 리턴한다.
    def CheckLastNews(self, news_class, idx):
        if not news_class['category'] in self.last_news:
            self.last_news[news_class['category']] = news_class['title']
            return False

        if self.last_news[news_class['category']] == news_class['title']:
            return True

        # 제일 처음한 뉴스를 중복체크를 위해 저장해놓는다.
        if idx == 0:
            self.last_news[news_class['category']] = news_class['title']
            return False


    #가장 많이 나온 단어찾기



    #해당단어와 연관된 단어들 찾기.

naver =NaverNewsCrawling()
naver.start_class()

