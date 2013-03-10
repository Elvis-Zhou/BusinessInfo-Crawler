#!/usr/bin/env python

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

class ContactFinder():
    def __init__(self):
        self.con = sqlite3.connect('../database.db')
        self.cur = self.con.cursor()
        self.soup=""
        self.title=""
        self.max=0
        self.url=""

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

        self.filterWebs=[]
        self.filterMails=[]

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
        self.cur.execute("""SELECT * FROM Urls WHERE Dealed=0 Limit %d""" % limit)
        result=self.cur.fetchmany(limit)
        print "正在从数据库获取链接"
        if result:
            for i in range(0,len(result)):
                try:
                    self.keywords[i]=result[i][0]
                    self.titles[i]=result[i][1]
                    self.originurls[i]=result[i][2]
                    self.countries[i]=result[i][3]
                except:
                    print "finish!"
                    return False
            return True
        else:
            return False

    def findCompanyNames(self):
        i=0
        for url in self.urls:
            self.names[i]=url[url.find(".",0)+1:url.find(".",11)]
            i+=1
            #print self.names

    def dealUrl(self,url):
        #url=self.urls[0]
        if not url.startswith("http://"):
            return ""
        end=url.find("/",7)
        url=url[0:end]
        #print url
        return url

    def dealUrlList(self):
        i=0
        for url in self.originurls:
            self.urls[i]=self.dealUrl(url)
            i+=1

    def findContactPageUrl(self,url,i):
        result=""
        if not url:
            self.contacturls[i]=result
            return result
        if not url.startswith("http"):
            self.contacturls[i]=result
            return result
        print "正在链接找寻相关联系方式页面： ",url

        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')

        support=soup.find("a",{"href":re.compile(r".*?support.*?",re.DOTALL|re.IGNORECASE)})
        if support:
            if support["href"].startswith("/"):
                self.contacturls[i]=url+support["href"]
                return url+support["href"]
            elif len(support["href"])<25:
                self.contacturls[i]=url+"/"+support["href"]
                return url+"/"+support["href"]
            else:
                self.contacturls[i]=support["href"]
                return support["href"]

        contact=soup.find("a",{"href":re.compile(r".*?contact.*?",re.DOTALL|re.IGNORECASE)})
        if contact:
            if contact["href"].startswith("/"):
                self.contacturls[i]=url+contact["href"]
                return url+contact["href"]
            elif len(contact["href"])<25:
                self.contacturls[i]=url+"/"+contact["href"]
                return url+"/"+contact["href"]
            else:
                self.contacturls[i]=contact["href"]
                return contact["href"]

        about=soup.find("a",{"href":re.compile(r".*?about.*?",re.DOTALL|re.IGNORECASE)})
        if about:
            if about["href"].startswith("/"):
                self.contacturls[i]=url+about["href"]
                return url+about["href"]
            elif len(about["href"])<25:
                self.contacturls[i]=url+"/"+about["href"]
                return url+"/"+about["href"]
            else:
                self.contacturls[i]=about["href"]
                return about["href"]

        findus=soup.find("a",{"href":re.compile(r".*?find[-]us.*?",re.DOTALL|re.IGNORECASE)})
        if findus:
            if findus["href"].startswith("/"):
                self.contacturls[i]=url+findus["href"]
                return url+findus["href"]
            elif len(findus["href"])<25:
                self.contacturls[i]=url+"/"+findus["href"]
                return url+"/"+findus["href"]
            else:
                self.contacturls[i]=findus["href"]
                return findus["href"]

        #self.contacturls.append("")
        return ""

    def findContactPageUrl(self,url,i):
        result=""
        if not url:
            self.contacturls[i]=result
            return result
        if not url.startswith("http"):
            self.contacturls[i]=result
            return result
        print "正在链接找寻相关联系方式页面： ",url

        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')

        support=soup.find("a",{"href":re.compile(r".*?support.*?",re.DOTALL|re.IGNORECASE)})
        if support:
            if support["href"].startswith("/"):
                self.contacturls[i]=url+support["href"]
                return url+support["href"]
            elif len(support["href"])<25:
                self.contacturls[i]=url+"/"+support["href"]
                return url+"/"+support["href"]
            else:
                self.contacturls[i]=support["href"]

        contact=soup.find("a",{"href":re.compile(r".*?contact.*?",re.DOTALL|re.IGNORECASE)})
        if contact:
            if contact["href"].startswith("/"):
                self.contacturls[i]=url+contact["href"]
                return url+contact["href"]
            elif len(contact["href"])<25:
                self.contacturls[i]=url+"/"+contact["href"]
                return url+"/"+contact["href"]
            else:
                self.contacturls[i]=contact["href"]
                return contact["href"]

        about=soup.find("a",{"href":re.compile(r".*?about.*?",re.DOTALL|re.IGNORECASE)})
        if about:
            if about["href"].startswith("/"):
                self.contacturls[i]=url+about["href"]
                return url+about["href"]
            elif len(about["href"])<25:
                self.contacturls[i]=url+"/"+about["href"]
                return url+"/"+about["href"]
            else:
                self.contacturls[i]=about["href"]
                return about["href"]

        findus=soup.find("a",{"href":re.compile(r".*?find[-]us.*?",re.DOTALL|re.IGNORECASE)})
        if findus:
            if findus["href"].startswith("/"):
                self.contacturls[i]=url+findus["href"]
                return url+findus["href"]
            elif len(findus["href"])<25:
                self.contacturls[i]=url+"/"+findus["href"]
                return url+"/"+findus["href"]
            else:
                self.contacturls[i]=findus["href"]
                return findus["href"]

        #self.contacturls.append("")
        return ""

    def buildContactUrlList(self):

        threads=[]
        index=0
        for url in self.urls:
            t=threading.Thread(target=self.findContactPageUrl,args=(url,index,))
            index+=1
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def dealContactPage(self,url,i):
        if not url:
            return
        print "Analyzing the web page to get the contact information: ",url
        htmlfile=self.getpage(url)
        #print htmlfile
        #address re pattern ([\w\d\s]*,){3,8}([\w\d\s~.]*?.){1,5}
        #(?:[\w\d\s]*,){3,10}(?:[\w\d\s]*\.)
        #([\w\d\s]*,){3,10}([\w\d\s]*\.)
        try:
            addresses=re.findall(r"(?:[\w\d\s]*,){3,10}(?:[\w\d\s]*?\.)",htmlfile,re.DOTALL)
        except:
            addresses=""

        try:
            tels=re.findall(r"\d{2,7}\s+[\d\s]{2,10}\d+",htmlfile,re.DOTALL)
        except:
            tels=""

        try:
            emails=re.findall(r"\w+(?:[-+.]\w+)*@\w+(?:[-.]\w+)*\.\w+(?:[-.]\w+)*",htmlfile,re.DOTALL)
        except:
            emails=""

        if addresses:
            address=addresses[0].strip()
        else:
            address=""

        if tels:
            tel=tels[0].strip()
        else:
            tel=""

        if emails:
            email=emails[0].strip()
        else:
            email=""

        try:
            rawinformation=ExtMainText.main(htmlfile)
        except:
            rawinformation=""


        self.addresses[i]=address
        self.tels[i]=tel
        self.emails[i]=email
        self.rawInformations[i]=rawinformation

        result=(address,tel,email,rawinformation)

        return result

    def buildInformationList(self):
        threads=[]
        index=0
        for url in self.contacturls:
            t=threading.Thread(target=self.dealContactPage,args=(url,index,))
            index+=1
            t.setDaemon(True)
            threads.append(t)
            t.start()
            #self.dealContactPage(url)
        for t in threads:
            t.join()


    def formTupleList(self):
        tupleList=[]
        #print len(self.keywords),len(self.urls),len(self.names),len(self.countries),len(self.emails),len(self.addresses),len(self.tels),len(self.rawInformations)

        for i in range(0,len(self.keywords)):
            try:
                keyword=self.keywords[i]
            except:
                keyword=""
            #原来是url=self.urls[i]
            try:
                url=self.contacturls[i]
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
        if self.websiteFiltered(onetuple[1]):
            return
        if self.mailFiltered(onetuple[4]):
            return
        if not onetuple[1].strip():
            return
        sql='INSERT INTO Information (Keyword,Url,Name,Country,Email,Address,Tel,RawInformation) VALUES(?,?,?,?,?,?,?,?)'
        print onetuple[1]+": "+onetuple[2]+ '  Email: ' +onetuple[4]

        try:
            self.cur.execute(sql,onetuple)
        except BaseException,e:
            print e,"the email is existed."

    def saveList(self,tupleList):
        count=len(tupleList)
        for i in range(0,count):
            self.saveToInformationDB(tupleList[i])

        try:
            self.con.commit()
        except BaseException,e:
            print e,"the email is existed."

    def updateUrlDB(self):
        for url in self.originurls:
            sql="""UPDATE Urls SET Dealed="1" WHERE Url="%s" """ % url
            try:
                self.cur.execute(sql)
            except BaseException,e:
                print e,"cannot update Dealed ."
        try:
            self.con.commit()
        except BaseException,e:
            print e,"cannot update Dealed ."

    def initList(self,threadLimit=10):
        if (not threadLimit)or threadLimit=="0":
            threadLimit=10
        #print "初始化列表中"
        self.keywords=["" for i in range(int(threadLimit))]
        self.originurls=["" for i in range(int(threadLimit))]
        self.urls=["" for i in range(int(threadLimit))]
        self.contacturls=["" for i in range(int(threadLimit))]
        self.titles=["" for i in range(int(threadLimit))]
        self.countries=["" for i in range(int(threadLimit))]
        self.names=["" for i in range(int(threadLimit))]
        self.emails=["" for i in range(int(threadLimit))]
        self.addresses=["" for i in range(int(threadLimit))]
        self.tels=["" for i in range(int(threadLimit))]
        self.rawInformations=["" for i in range(int(threadLimit))]

    def websiteFiltered(self,url):
        if not self.filterWebs:
            f=open("FilterRegular.txt",'r')
            self.filterWebs=f.readlines()
            f.close()
        for filterweb in self.filterWebs:
            if filterweb.rstrip().lower() in url.lower():
                return True
        return False

    def mailFiltered(self,url):
        if not self.filterMails:
            f=open("FilterMails.txt",'r')
            self.filterMails=f.readlines()
            f.close()
        for filtermail in self.filterMails:
            if filtermail.rstrip().lower() in url.lower():
                return True
        return False

    def main(self,threadLimit=10):
        print "程序开始运行"
        self.initList()

        if (not threadLimit)or threadLimit=="0":
            threadLimit=10

        while self.fetchFromDB(int(threadLimit)):
            #self.fetchFromDB()
            self.dealUrlList()
            self.findCompanyNames()
            self.buildContactUrlList()
            self.buildInformationList()
            tupleList=self.formTupleList()
            self.saveList(tupleList)
            self.updateUrlDB()
            #self.con.commit()
            self.initList()
        print "数据库中的链接都处理完成了."

if __name__ == "__main__":
    finder=ContactFinder()

    threadLimit=raw_input("请输入你要使用的线程数，默认值为：10 >>>")
    finder.main(threadLimit)
    #finder.initList()
