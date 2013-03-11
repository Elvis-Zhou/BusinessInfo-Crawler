#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#import sys
#from extractor import Extractor, DocBuilder, FsCache
from time import sleep
import urllib ,urllib2
import cookielib
import sqlite3
import re
from bs4 import BeautifulSoup
urllib2.socket.setdefaulttimeout(30)
import chardet
import threading
import sys
sys.path.append("..")
import Google.ContactFinder
finder=Google.ContactFinder.ContactFinder()


class YellSpider():
    def __init__(self):
        self.lock=threading.RLock()
        self.con = sqlite3.connect('../database.db')
        self.cur = self.con.cursor()

        self.soup=""
        self.title=""
        self.originurl = 'http://www.yell.com/ucs/UcsSearchAction.do?'
        self.goalurl=""
        self.seed=""
        self.max=0
        self.url=""
        self.maxitem=0

        self.htmlfile=""
        self.country=""

        self.keywords=[]
        self.urls=[]
        self.titles=[]
        self.countries=[]
        self.names=[]
        self.emails=[]
        self.addresses=[]
        self.tels=[]
        self.rawInformations=[]

        self.filterMails=[]
        self.cj = cookielib.CookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        #self.opener.addheaders = [('User-agent', 'Opera/9.23')]
        self.opener.add_headers=[("User-Agent","Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.35 Safari/537.17")]
        urllib2.install_opener(self.opener)
        self.requset=urllib2.Request(self.url)

    def getpage(self,url):
        if not url.startswith("http"):
            return

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
        try:
            charset=chardet.detect(htmlfile)["encoding"]
            htmlfile=unicode(htmlfile,charset)
        except:
            pass
        return htmlfile


    def dealContactPage(self,url):
        if not url:
            self.lock.acquire()

            self.names.append("")
            self.addresses.append("")
            self.tels.append("")
            self.emails.append("")
            self.rawInformations.append("")

            self.lock.release()
            return

        htmlfile=self.getpage(url)
        #print htmlfile
        soup=BeautifulSoup(htmlfile,'lxml')

        companyFrames=soup.find_all("div",{"class":" vcard padding clearfix"})

        for company in companyFrames:
            namesoup=company.find_all("a",{"class":"fn org"})
            urlsoup=company.find_all("a",{"class":"url"})
            addresssoup=company.find_all("a",{"class":"tabLink expandLink"})
            telsoup=company.find_all("span",{"class":"tel"})
            rawinformation=company.get_text().strip()
            name=""
            address=""
            tel=""
            url=""
            email=""
            contacturl=""
            if namesoup:
                name=namesoup[0].text.strip()
                print "Dealing company: "+name
            if urlsoup:
                try:
                    url=urlsoup[0]["href"]
                    if url[-1]=="/":
                        url=url[:-1]
                    finder.initList()
                    contacturl=finder.findContactPageUrl(url,0)
                    result=finder.dealContactPage(contacturl,0)
                    email=result[2]
                except:
                    pass
            if addresssoup:
                address=addresssoup[0].get_text().strip()
            if telsoup:
                tel=telsoup[0].get_text().strip()
            #无email
            #emails=soup.find_all("a",{"href":re.compile(r"javascript:openMail(.*);",re.DOTALL)})
            self.lock.acquire()

            self.names.append(name)
            self.addresses.append(address)
            self.tels.append(tel)
            self.urls.append(contacturl)
            self.emails.append(email)
            self.rawInformations.append(rawinformation)

            self.lock.release()


    def formTupleList(self):
        tupleList=[]
        #print len(self.keywords),len(self.urls),len(self.names),len(self.countries),len(self.emails),len(self.addresses),len(self.tels),len(self.rawInformations)

        for i in range(0,len(self.keywords)):

            try:
                keyword=self.keywords[i]
            except:
                keyword=""
            try:
                url=self.urls[i]
            except:
                url=""
            try:
                name=self.names[i]
            except:
                name=""
            try:
                country=self.countries[i]
            except:
                country=""
            try:
                email=self.emails[i]
            except:
                email=""
            try:
                address=self.addresses[i]
            except:
                address=""
            try:
                tel=self.tels[i]
            except:
                tel=""
            try:
                rawInformation=self.rawInformations[i]
            except:
                rawInformation=""

            tupleList.append((keyword,
                              url,
                              name,
                              country,
                              email,
                              address,
                              tel,
                              rawInformation)
            )

        return tupleList

    def saveToInformationDB(self,onetuple):
        if self.mailFiltered(onetuple[4]):
            return
        sql='INSERT INTO Information (Keyword,Url,Name,Country,Email,Address,Tel,RawInformation) VALUES(?,?,?,?,?,?,?,?)'
        print onetuple[2]+": "+onetuple[2]+"\n  Address: "+onetuple[5]

        try:
            self.cur.execute(sql,onetuple)
        except BaseException,e:
            print "该数据已存在Information数据库中."

    def saveInforList(self,tupleList):
        count=len(tupleList)
        for i in range(0,count):
            self.saveToInformationDB(tupleList[i])

        try:
            self.con.commit()
        except BaseException,e:
            print "该数据已存在Information数据库中."

    def initList(self):

        self.keywords=[self.word for i in range(15)]
        self.originurls=[]
        self.urls=[]
        self.contacturls=[]
        self.countries=[self.country for i in range(15)]
        self.names=[]
        self.emails=[]
        self.addresses=[]
        self.tels=[]
        self.rawInformations=[]

    def getMax(self):
        htmlfile=self.getpage(self.goalurl+"1")
        soup=BeautifulSoup(htmlfile,'lxml')
        maxresults=soup.find("span",{"class":"results_headercount"})
        if maxresults:
            result=maxresults.get_text().split()[0]
            if result:
                self.maxitem=result


    def getLocals(self):
        f=open("Location.txt",'r')
        locals=f.readlines()
        f.close()
        location=[]
        if len(locals)==0:
            return []
        else:
            for local in locals:
                location.append(local.strip())
            return location


    def mailFiltered(self,url):
        if not self.filterMails:
            f=open("FilterMails.txt",'r')
            self.filterMails=f.readlines()
            f.close()
        for filtermail in self.filterMails:
            if filtermail.rstrip().lower() in url.lower():
                return True
        return False


    def mainGetUrls(self,word="led light bulbs",max=0,local=0):
        if not word:
            word="led light bulbs"

        self.max=max
        self.country="UK"
        self.word=word
        self.page=1
        keyword={
            "keywords":word,
            "pageNum":self.page
        }
        url=self.originurl + urllib.urlencode(keyword)
        self.goalurl=url[0:-1]
        if  local=="1":
            locals=self.getLocals()
            if locals:
                for l in locals:
                    tempLocal={
                        "keywords":word,
                        "pageNum":self.page,
                        "location":l
                    }
                    location=urllib.urlencode(tempLocal)
                    print "正在获取地区："+l
                    self.goalurl=self.originurl+location
                    self.getMax()
                    self.max=int(int(self.maxitem)/15)+1

                    try:
                        if int(max)!=0:
                            if int(max)<self.max :
                                self.max=int(max)
                    except:
                        pass
                    #self.max=2
                    print "there are %s results." % self.maxitem

                    print " 正在获取每一个分页的信息."
                    self.page=1
                    for p in range(1,self.max+1):
                        self.page=p
                        self.initList()
                        print "Dealing page: ",p
                        url=self.goalurl +str(self.page)
                        self.dealContactPage(url)
                        tupleList=self.formTupleList()
                        self.saveInforList(tupleList)

                        print "分页: ",str(p)," 的信息已经处理完毕并写入数据库"
                    print "休息一分钟后继续获取下一个地区"
                    sleep(60)
                print "成功，程序运行完成！"


        else:
            #self.goalurl=url
            self.getMax()
            self.max=int(int(self.maxitem)/15)+1

            try:
                if int(max)!=0:
                    if int(max)<self.max :
                        self.max=int(max)
            except:
                pass
            #self.max=2
            print "there are %s results." % self.maxitem

            print " 正在处理每一个分页的信息."
            self.page=1
            for p in range(1,self.max+1):
                self.page=p
                self.initList()
                print "Dealing page: ",p
                url=self.goalurl +str(self.page)
                self.dealContactPage(url)
                tupleList=self.formTupleList()
                self.saveInforList(tupleList)

            print "成功，程序运行完成！"

    def readKeywords(self):
        print "读取keywords.txt文件中"
        f=open("keywords.txt",'r')
        keys=f.readlines()
        f.close()
        words=[]
        for key in keys:
            words.append(key.rstrip().lower())
        return words

    def main(self,max=0,threadLimit=10,local=0):
        print "程序开始运行："
        keys=self.readKeywords()
        for word in keys:
            print "正在处理的关键词是",word
            self.mainGetUrls(word,max,local)
        print "程序全部运行完毕，成功。"


if __name__ == "__main__":
    yell=YellSpider()
    #yellowpage.main("CONSTRUCTORA RSR")

    #word=raw_input("请输入你要查询的关键词，例如默认为：led light bulbs >>>")
    max=raw_input("请输入你要获取的最大页数，默认值是:0,即可自动获取数并判断最大页 >>>")
    threadLimit=raw_input("请输入你要使用的线程数，此网站强烈建议只采用单线程，默认值为：1 >>>")
    local=raw_input("是否查询Location.txt中的地区，是请输入1，不是请输入0，默认值为：0 >>>")

    yell.main(max,threadLimit,local)