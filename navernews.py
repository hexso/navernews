# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from time_control import GetTimeList, GetNowTime
from treatfile import WriteInfoToCsv, ReadExcel, CsvToTxtWithEdit, FixWithKomoran
import requests
import pandas as pd
import os
import time
import glob
import re
from gensim.models import Word2Vec
#csv에 저장하는 함수를 따로 짜자.
#중복체크하는 함수 따로 만들기





class NaverNewsCrawling:

    classCategory = 'a'

    SEARCH_FROM_YEAR = 2020
    SEARCH_FROM_MONTH = 1
    SEARCH_FROM_DAY = 1
    WAIT_SECONDS = 60
    PAGENUM = 50

    RELATEDVECTORFILE = "./word2vec/related_word2vec.model"

    STOCKFOLDER = "증권"
    # 259금융, 258증권, 261산업재계, 771중기벤처, 260부동산, 262글로벌경제 310생활경제, 263겨에일반
    # 264청와대, 265국회, 267국방외교,
    #cateGory = [258, 259, 260, 261, 262, 263, 264, 265, 310, 771]
    cateGory = [258,259]
    #중복 체크를 위한 사전
    last_news = dict()

    def start_class(self):

        #self.CrawlNaverNews()
        #self.ContinueGettingNews()
        self.MakeKomoranFile()
        #self.MakeRelatedVector()
        #self.SeekRealtedWords()

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
            time.sleep(self.WAIT_SECONDS)


    #특정날짜부터 현재날짜까지의 뉴스를 찾는다.
    def CrawlNaverNews(self):

        pageNum = self.PAGENUM
        dateTime = GetTimeList(self.SEARCH_FROM_YEAR, self.SEARCH_FROM_MONTH, self.SEARCH_FROM_DAY)
        #sdi 2의 카테고리에 따라서 페이지를 접속한다.
        #sdi 1은 무시되는것 같다.
        for c in self.cateGory:
            for t in dateTime:
                for p in range(1, pageNum, 1):
                    i=0
                    url_info = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2={0}&sid1=100&date={1}&page={2}".format(c,t,p)
                    print(url_info)
                    try:
                        news_url_list = self.ParseNewsURL(url_info)
                        for news_url in news_url_list :
                            news_class = self.GetNewsContent(news_url)
                            if self.CheckLastNews(news_class, i) == True:
                                i=-1
                                break
                            WriteInfoToCsv(news_class, self.classCategory)
                            i +=1
                        if i == -1:
                            break
                    except Exception as ex:
                        print(ex)
                        pass


    #이 함수의 경우 인자로 url을 받는다
    #뉴스페이지에서 뉴스의 url을 parsing한다.
    def ParseNewsURL(self, url_info):

        response = requests.get(url_info)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        html_newslist = soup.select("#main_content > div.list_body.newsflash_body > ul.type06_headline > li > dl > dt:nth-of-type(1) > a")
        self.classCategory = soup.select('h3')[1].text
        news_url_list = list()

        for n in html_newslist:
            url_info = n.get('href')
            news_url_list.append(url_info)

        html_newslist = soup.select("#main_content > div.list_body.newsflash_body > ul.type06 > li > dl > dt:nth-of-type(1) > a")
        for n in html_newslist:
            url_info = n.get('href')
            news_url_list.append(url_info)

        return news_url_list

    #뉴스정보들을 parsing한다.
    #return 값은 사전 형식
    def GetNewsContent(self, url_info):

        news_class = dict()
        response = requests.get(url_info)
        time.sleep(0.1)
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


    #사전에 카테고리별로 찾은 뉴스의 제목중 제일 최근것을 저장한다.
    #저장한 값과, 인자값을 비교해서 같은지를 비교한다.
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
    #리스트로 출력
    def MakeRelatedVector(self, refresh=0):

        if not refresh == 0 :
            files = list()
            files.append(refresh)
        else :
            files = glob.glob("*/*_komoran.txt",recursive=True)

        data_array = list()
        print(files)
        #글자를 정리해서 txt파일로 먼저 만든다.
        #형태소 분석기를 통해 txt파일을 만든다.
        for file in files:
            f = open(file, 'r', encoding='euc-kr')
            data_list = f.readlines()

            for data in data_list : 
                data = data.replace('\n', '')
                data = data.split(',')
                data_array.append(data)
        
        if not refresh == 0:
            new_model = Word2Vec.load(self.RELATEDVECTORFILE)
            new_model.build_vocab(data_array, update = True)
            new_model.train(data_array, epochs=new_model.iter, total_examples=new_model.corpus_count)
            new_model.save(self.RELATEDVECTORFILE)
        else :
            model = Word2Vec(data_array, size=100, window=10, min_count=50, iter=50,sg=1)
            model.save(self.RELATEDVECTORFILE)


    #csv파일들을 정리해서 txt파일과 _komoran txt파일로만든다.
    def MakeKomoranFile(self) :

        files = glob.glob("*/*.csv", recursive=True)
        data_array = list()
        print(files)
        #글자를 정리해서 txt파일로 먼저 만든다.
        #형태소 분석기를 통해 txt파일을 만든다.
        txt_list = CsvToTxtWithEdit(files)
        file_name = FixWithKomoran()


    #word2vec을 이용해서 유사단어 찾기
    def SeekRealtedWords(self, num = 10) : 
        a = input("what word do you want?  ")
        model = Word2Vec.load(self.RELATEDVECTORFILE)
        try :
            result = model.wv.most_similar(a)
            print(result)
        except Exception as e:
            print(e)

    #가장많이 언급된 단어를 찾는다.
    #파일 리스트를 한꺼번에 받아서 거기서 읽어서 처리한다.
    #input: file list(file contents is distinguished by ',' '\n')
    #output : descending frequent word dictonary
    def FindFrequentWords(self, file_list, num=10) :
        word_list = list()
        word_dict = list()

        #파일 읽어서 리스트로 정리
        #속도를 개선할 방법 필요
        for file in file_list :
            f = open(file)
            data = f.read()
            for word in re.split('\W+', data) :
                if word in word_dict :
                    word_dict[word] +=1
                else :
                    word_dict[word] = 1

        word_list = sorted(word_dict.items(), key=lambda x:x[1], reverse=True)
        return word_list[:num+1]

    #해당 단어가 있는 파일 이름을 찾는다.
    #input: word, file_list
    #output: file_list
    def FindDataRelatedWord(self, keyword, file_list) :
        date_list = list()

        for file in file_list :
            f = open(file)
            data = f.read()
            if keyword in data:
                date_list.append(file)
            f.close()

        return date_list

    #해당 키워드와 연관된 주식들을 찾는다.
    #input: keyword
    #output: stock_list
    def FindRelatedStock(self, keyword) :
        files = glob.glob("*/????????.txt", recursive=True)
        date_file_list = self.FindDateRelatedWord(keyword, files)
        keyword_list = self.FindFrequentWords(date_file_list, 10)
        return keyword_list

naver =NaverNewsCrawling()
naver.start_class()

