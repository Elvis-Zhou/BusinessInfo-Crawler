#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import sys
from time import sleep
import urllib ,urllib2
import cookielib
import sqlite3
from bs4 import BeautifulSoup
urllib2.socket.setdefaulttimeout(30)
import string
from InputModule import Inputs,FliterRegular

class GoogleSpider():
    def __init__(self):
        self.con = sqlite3.connect('../database.db')
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
        requset.add_header('User-agent', 'Opera/9.23')
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
            except BaseException,e:
                #print e
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
            print "warning: ",e

    def saveList(self):
        count=len(self.urls)
        for i in range(0,count):
            self.saveToUrlDB((self.word,self.titles[i],self.urls[i],self.country,"0"))
        self.urls=[]
        self.titles=[]
        try:
            self.con.commit()
        except BaseException,e:
            print "warning: ",e

    def getBestUrl(self,word="led light bulbs",country=""):
        if country:
            keyword={
                "q":word,
                "cr":"country"+country
            }
        else:
            keyword={
                "q":word
            }
        url=self.originurl % (urllib.urlencode(keyword),str(0))
        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')

        tempUrls=soup.find_all("h3",{"class":"r"})

        try:
            tempurl=tempUrls[0].a["href"][7:]
            end=tempurl.find("/",7)
            if end!=-1:
                tempurl=tempurl[0:end]
            return tempurl
        except BaseException:
            return ""

    def main(self):

        max,threadLimit,local,sleeptime=self.showScreenInfor()

        print "Program Begin: "
        keys=Inputs.readKeywords()
        #开始对每个关键词进行处理

        for word in keys:
            print "Now ,the word is:",word,".\nIt is in progress."
            keyword=word.strip()
            self.mainGetUrls(keyword,max,sleeptime,local)

        print "All finish."

    def mainGetUrls(self,word="led light bulbs",max=1000,sleeptime=0,local=0):
        countries=[]
        if local==1:
            countries=Inputs.getCountries()
        if (not max)or max=="0":
            max=1000
        else:
            max=int(max)*10
        if local==1:
            for country in countries:
                print "now dealing country:"+country
                self.max=max
                self.country=country
                self.word=word
                keyword={
                    "q":word,
                    "cr":"country"+country
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
                        print "waiting for :"+str(sleeptime)+" second,then continue"
                        sleep(int(sleeptime))
        else:
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
                    print "waiting for :"+str(sleeptime)+" second,then continue"
                    sleep(int(sleeptime))

    def showScreenInfor(self):
        max=raw_input("Please input the max pages.(default:0),It can automatically get the max pages.  >>>")
        if not max:
            max=0
        else:
            max=string.atoi(max)
        threadLimit=raw_input("Please input the number of threads.(default:10)>>>")
        if not threadLimit:
            threadLimit=10
        else:
            threadLimit=string.atoi(threadLimit)
        local=raw_input("Do you want to query Countries in Country.txt? If True,input 1,else input 0.(default:0) >>>")
        if not local:
            local=0
        else:
            local=string.atoi(local)

        sleeptime=raw_input("Please input the sleep time (second) .(default:5) >>>")
        if not sleeptime:
            sleeptime=0
        else:
            sleeptime=string.atoi(sleeptime)

        return max,threadLimit,local,sleeptime

if __name__ == "__main__":
    google=GoogleSpider()
    #print google.getBestUrl("Abracad Architects")
    google.main()
