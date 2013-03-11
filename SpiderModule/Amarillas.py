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

class YellowPageSpider():
    def __init__(self):
        #多线程
        self.lock=threading.RLock()
        #数据库连接
        self.con = sqlite3.connect('../database.db')
        self.cur = self.con.cursor()
        #基本属性
        self.htmlfile=""
        self.soup=""
        self.country=""
        self.title=""
        self.url=""
        self.originurl = ''
        self.goalurl=""
        self.seed=""
        self.max=0
        self.maxitem=0
        #要存入的参数
        self.keywords=[]
        self.homepageUrls=[]
        self.urls=[]
        self.contacturls=[]
        #self.titles=[]
        self.countries=[]
        self.names=[]
        self.emails=[]
        self.addresses=[]
        self.tels=[]
        self.rawInformations=[]
        #self.filterMails=[]

        #浏览器伪装
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
            for i in range(0,len(result)):
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

        companyname=soup.find_all("h2",{"class":"fn org"})
        emails=soup.find_all("a",{"href":re.compile(r"javascript:openMail(.*);",re.DOTALL)})
        addresses=soup.find_all("address",{"class":"street"})
        tels=soup.find_all("span",{"class":"phoneSpan"})
        rawinformations=soup.find_all("ul",{"id":"descriptionTools"})

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

        if tels:
            tel=tels[0].text.replace("&nbsp;"," ").strip()

        rawinformation=""
        if rawinformations:
            rawinformation=rawinformations[0].get_text().strip()

        self.lock.acquire()

        self.names.append(name)
        self.addresses.append(address)
        self.tels.append(tel)
        self.emails.append(email)
        self.rawInformations.append(rawinformation)

        self.lock.release()

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
        if self.mailFiltered(onetuple[4]):
            return
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
        self.homepageUrls=[]
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


    def mainGetUrls(self,word="INGENIERÍA DE PROYECTOS",max=0,local=0):
        if not word:
            word="INGENIERÍA DE PROYECTOS"

        self.max=max
        self.country="CL"
        self.word=word
        keyword={
            "":word
        }
        url=self.originurl + urllib.urlencode(keyword)[1:]+"/"

        if (not local) and (not local=="1"):
            locals=self.getLocals()
            if locals:
                for l in locals:
                    tempLocal={
                        "":l
                    }
                    location=urllib.urlencode(tempLocal)[1:]+"/"
                    print "正在获取地区："+l
                    self.goalurl=url+location
                    self.getseed()
                    self.max=int(int(self.maxitem)/35)+1

                    if max!=0:
                        if max<self.max :
                            self.max=max

                    #self.max=2
                    print "there are %s results." % self.maxitem

                    print " 正在获取每一个分页的信息."
                    self.page=1
                    for p in range(1,self.max+1):
                        self.page=p
                        print "Dealing page: ",p
                        url=self.goalurl + "?seed=" + str(self.seed) + "&page=" + str(self.page)
                        self.getPageUrls(url)
                    print "已经获得了所有分页信息，准备写入Url数据库."

                    self.saveUrlList()
                    self.contacturls=[]
        else:
            self.goalurl=url
            self.getseed()
            self.max=int(int(self.maxitem)/35)+1

            if max!=0:
                if max<self.max :
                    self.max=max

            #self.max=2
            print "there are %s results." % self.maxitem

            print " 正在获取每一个分页的信息."
            self.page=1
            for p in range(1,self.max+1):
                self.page=p
                print "Dealing page: ",p
                url=self.goalurl + "?seed=" + str(self.seed) + "&page=" + str(self.page)
                self.getPageUrls(url)
            print "已经获得了所有分页信息，准备写入Url数据库."

            self.saveUrlList()
            self.contacturls=[]

    def mainMiningInfor(self,threadLimit=10):
        #self.fetchFromDB(30)
        #self.dealContactPage("http://www.amarillas.cl/empresa/naser_ingenieria_ltda-301309390/")
        if (not threadLimit)or threadLimit=="0":
            threadLimit=10
        while self.fetchFromDB(threadLimit):
            self.buildInformationList()
            tupleList=self.formTupleList()
            self.saveInforList(tupleList)
            self.updateUrlDB()
            self.initList()

    def main(self,word="INGENIERÍA DE PROYECTOS",max=0,threadLimit=10,local=0):

        print "程序开始运行："
        self.mainGetUrls(word,max,local)
        self.mainMiningInfor(threadLimit)
        print "程序全部运行完毕，成功。"


if __name__ == "__main__":
    yellowpage=YellowPageSpider()
    #yellowpage.main("CONSTRUCTORA RSR")

    word=raw_input("请输入你要查询的关键词，例如默认为：INGENIERÍA DE PROYECTOS >>>")
    max=raw_input("请输入你要获取的最大页数，默认值是:0,即可自动获取数并判断最大页 >>>")
    threadLimit=raw_input("请输入你要使用的线程数，默认值为：10 >>>")
    local=raw_input("是否查询Location.txt中的地区，是请输入1，不是请输入0，默认值为：0 >>>")

    yellowpage.main(word,int(max),int(threadLimit),int(local))