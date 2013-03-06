#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import sys
from time import sleep
import urllib ,urllib2
import cookielib
import sqlite3
from bs4 import BeautifulSoup
urllib2.socket.setdefaulttimeout(30)

class GoogleSpider():
    def __init__(self):
        self.con = sqlite3.connect('./database.db')
        self.cur = self.con.cursor()
        self.soup=""
        self.title=""
        self.titles=[]
        self.originurl = 'http://www.google.co.uk/search?sourceid=chrome&;ie=UTF-8&%s&start=%s'
        self.max=0
        self.url=""
        self.urls=[]
        self.htmlfile=""
        self.country=""
        self.page=0

        self.cj = cookielib.CookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-agent', 'Opera/9.23')]
        urllib2.install_opener(self.opener)
        self.requset=urllib2.Request(self.url)

    def getpage(self,url):
        requset=urllib2.Request(url)
        i=0
        t=0
        htmlfile=""
        while t==0:
            try:
                htmlfile=urllib2.urlopen(requset).read()
                if htmlfile:
                    t=1
                    break
                else:
                    i+=1
                    #continue
            except :
                i+=1
            if i>=5:break
        #self.htmlfile=htmlfile
        #print self.htmlfile
        return htmlfile


    def findTitleAndUrl(self,htmlfile):
        soup=BeautifulSoup(htmlfile,'lxml')
        self.urls=[]
        self.titles=[]
        tempUrls=soup.find_all("h3",{"class":"r"})

        for url in tempUrls:
            self.titles.append(url.text)
            tempurl=url.a["href"][7:]
            end=tempurl.find("/",7)
            tempurl=tempurl[0:end+1]
            self.urls.append(tempurl)

    def saveToUrlDB(self,onetuple):
        #onetuple=("", "apple", "broccoli" ,"0")
        strtuple='","'.join(onetuple)
        sql='INSERT INTO Urls (Keyword,Title,Url,Country,Dealed) VALUES("%s")'% strtuple
        print onetuple[1]

        try:
            self.cur.execute(sql)
        except BaseException,e:
            print e,"该数据已经存在数据库中"

    def saveList(self):
        count=len(self.urls)
        for i in range(0,count):
            self.saveToUrlDB((self.word,self.titles[i],self.urls[i],self.country,"0"))
        self.urls=[]
        self.titles=[]
        try:
            self.con.commit()
        except:
            print "该数据已经存在数据库中"

    def main(self,word="led light bulbs",max=1000,sleeptime=0):
        if not word:
            word="led light bulbs"
        if (not max)or max=="0":
            max=1000
        else:
            max=int(max)*10
        self.max=max
        self.country="UK"
        self.word=word
        keyword={
            "q":word
        }
        for i in range(0,self.max,10):
            self.page=i
            print "page:",i/10,"item:",i
            url=self.originurl % (urllib.urlencode(keyword),str(self.page))
            htmlfile=self.getpage(url)
            self.findTitleAndUrl(htmlfile)
            self.saveList()
            if (not sleeptime)or sleeptime=="0":
                sleeptime=5
            if sleeptime:
                print "程序自动休息:"+str(sleeptime)+" 秒后继续"
                sleep(int(sleeptime))
        print "程序运行结束."

if __name__ == "__main__":
    google=GoogleSpider()
    word=raw_input("请输入你要查询的关键词，例如默认为：led light bulbs >>>")
    max=raw_input("请输入你要获取的最大页数，默认值是:100页 >>>")
    sleeptime=raw_input("请输入爬取完一页后休息的时间（秒），默认值为：5 >>>")

    google.main(word,max,sleeptime)

