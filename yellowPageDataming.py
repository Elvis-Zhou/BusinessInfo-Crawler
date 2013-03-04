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
import ExtMainText
import threading

class YellowPageSpider():
    def __init__(self):
        self.con = sqlite3.connect('./database.db')
        self.cur = self.con.cursor()
        #self.con.text_factory=str
        self.soup=""
        self.title=""
        self.originurl = 'http://www.amarillas.cl/buscar/'
        self.goalurl=""
        self.seed=""
        self.max=0
        self.url=""
        self.maxitem=0

        self.htmlfile=""
        self.country=""

        self.keywords=[]
        self.originurls=[]
        self.urls=[]
        self.contacturls=[]
        self.titles=[]
        self.countries=[]
        self.names=[]
        self.emails=[]
        self.addresses=[]
        self.tels=[]
        self.rawInformations=[]

        self.cj = cookielib.CookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-agent', 'Opera/9.23')]
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

    def fetchFromDB(self,limit=10):
        self.cur.execute("""SELECT * FROM Urls_Amarillas WHERE Dealed=0 Limit %d""" % limit)
        result=self.cur.fetchmany(limit)
        if result:
            for i in range(0,limit):
                try:
                    self.keywords.append(result[i][0])
                    #self.titles.append(result[i][1])
                    self.urls.append(result[i][2])
                    self.contacturls.append(result[i][2])
                    self.countries.append(result[i][3])
                except:
                    print "finish!"
                    return False
            return True
        else:
            return False

    def buildContactUrlList(self):
        self.contacturls=[]
        threads=[]
        for url in self.urls:
            t=threading.Thread(target=self.getPageUrls,args=(url,))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def dealContactPage(self,url):
        if not url:
            self.names.append("")
            self.addresses.append("")
            self.tels.append("")
            self.emails.append("")
            self.rawInformations.append("")
            return

        htmlfile=self.getpage(url)
        #print htmlfile
        soup=BeautifulSoup(htmlfile,'lxml')

        companyname=soup.find_all("h2",{"class":"fn org"})

        emails=soup.find_all("a",{"href":re.compile(r"javascript:openMail(.*);",re.DOTALL)})
        addresses=soup.find_all("address",{"class":"street"})
        tels=soup.find_all("span",{"class":"phoneSpan"})

        name=""
        if companyname:
            name=companyname[0].a.text.strip()

        address=""
        if addresses:
            address=addresses[0]["title"].strip()

        email=""
        if emails:
            maillist=re.findall(r"\w+(?:[-+.]\w+)*@\w+(?:[-.]\w+)*\.\w+(?:[-.]\w+)*",emails[0]["href"],re.DOTALL)
            if maillist:
                email=maillist[0]

        tel=""
        if tels:
            tel=tels[0].text.replace("&nbsp;"," ").strip()


        #try:
        #rawinformation=ExtMainText.main(htmlfile)
        #except:
        rawinformation=""

        self.names.append(name)
        self.addresses.append(address)
        self.tels.append(tel)
        self.emails.append(email)
        self.rawInformations.append(rawinformation)

    def buildInformationList(self):
        threads=[]
        for url in self.contacturls:
            t=threading.Thread(target=self.dealContactPage,args=(url,))
            t.setDaemon(True)
            threads.append(t)
            t.start()
            #self.dealContactPage(url)
        print "开始从数据库获取Url并获取具体公司信息中."
        for t in threads:
            t.join(300)
        print "成功获得这部分公司信息了。"

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

    def saveToUrlDB(self,onetuple):
        sql='INSERT INTO Urls_Amarillas (Keyword,Title,Url,Country,Dealed) VALUES(?,?,?,?,?)'
        print "saving "+ onetuple[2]

        try:
            self.cur.execute(sql,onetuple)
        except BaseException,e:
            print e,"该数据已经存在数据库中"


    def saveUrlList(self):
        count=len(self.contacturls)
        for i in range(0,count):
            self.saveToUrlDB((buffer(self.word),"",self.contacturls[i],self.country,"0"))
        try:
            self.con.commit()
        except:
            print "该数据已经存在数据库中"

    def saveToInformationDB(self,onetuple):

        sql='INSERT INTO Information (Keyword,Url,Name,Country,Email,Address,Tel,RawInformation) VALUES(?,?,?,?,?,?,?,?)'
        print onetuple[1]+": "+onetuple[2]+"  Email: "+onetuple[4]

        try:
            self.cur.execute(sql,onetuple)
        except BaseException,e:
            print e,"该数据已存在Information数据库中."

    def saveInforList(self,tupleList):
        count=len(tupleList)
        for i in range(0,count):
            self.saveToInformationDB(tupleList[i])

        try:
            self.con.commit()
        except BaseException,e:
            print e,"该数据已存在Information数据库中."

    def updateUrlDB(self):
        for url in self.urls:
            sql="""UPDATE Urls_Amarillas SET Dealed="1" WHERE Url="%s" """ % url
            try:
                self.cur.execute(sql)
            except BaseException,e:
                print e,"无法更新Dealed参数 ."
        try:
            self.con.commit()
        except BaseException,e:
            print e,"无法更新Dealed参数 ."

    def initList(self):
        self.keywords=[]
        self.originurls=[]
        self.urls=[]
        self.contacturls=[]
        self.titles=[]
        self.countries=[]
        self.names=[]
        self.emails=[]
        self.addresses=[]
        self.tels=[]
        self.rawInformations=[]

    def getseed(self):
        htmlfile=self.getpage(self.goalurl)
        soup=BeautifulSoup(htmlfile,'lxml')
        pages=soup.find("a",{"class":"border"})
        seed=""
        if pages:
            strseed=pages["href"]
            seed=strseed[strseed.find("?seed=")+6:strseed.find("&")]
            self.seed=seed
        #print seed
        maxresults=soup.find("div",{"class":"resultHeader"})
        if maxresults:
            result=maxresults.span.get_text()
            result=re.findall(r"\d+",result,re.DOTALL)
            if result:
                self.maxitem=result[0]


    def getPageUrls(self,url):
        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')
        infourls=soup.find_all("a",{"class":"more urchin gaf"})
        if infourls:
            for infourl in infourls:
                self.contacturls.append(infourl["href"])

    def mainGetUrls(self,word="INGENIERÍA DE PROYECTOS",max=50):
        self.max=max
        self.country="CL"
        self.word=word
        keyword={
            "":word
        }
        url=self.originurl + urllib.urlencode(keyword)[1:]+"/"
        self.goalurl=url
        self.getseed()
        self.max=int(int(self.maxitem)/35)+1
        #self.max=2
        print "there are %s results." % self.maxitem

        print " 正在获取每一个分页的信息."
        self.page=1
        for p in range(2,self.max+1):
            self.page=p
            print "Dealing page: ",p
            url=self.goalurl + "?seed=" + str(self.seed) + "&page=" + str(self.page)
            self.getPageUrls(url)
        print "已经获得了所有分页信息，准备写入Url数据库."

        self.saveUrlList()
        self.contacturls=[]

    def mainMiningInfor(self):
        #self.fetchFromDB(30)
        #self.dealContactPage("http://www.amarillas.cl/empresa/naser_ingenieria_ltda-301309390/")
        while self.fetchFromDB(10):
            self.buildInformationList()
            tupleList=self.formTupleList()
            self.saveInforList(tupleList)
            self.updateUrlDB()
            self.initList()

    def main(self,word="INGENIERÍA DE PROYECTOS",max=50):

        print "程序开始运行："
        self.mainGetUrls(word,max)
        self.mainMiningInfor()
        print "程序全部运行完毕，成功。"


if __name__ == "__main__":
    yellowpage=YellowPageSpider()
    yellowpage.main("Searle Cia Arquitectos Edmundo")
