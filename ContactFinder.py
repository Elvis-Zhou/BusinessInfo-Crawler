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
        self.con = sqlite3.connect('./database.db')
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
        if result:
            for i in range(0,limit):
                try:
                    self.keywords.append(result[i][0])
                    self.titles.append(result[i][1])
                    self.originurls.append(result[i][2])
                    self.countries.append(result[i][3])
                except:
                    print "finish!"
                    return False
            return True
        else:
            return False

    def findCompanyNames(self):
        self.names=[]
        for url in self.urls:
            self.names.append(url[url.find(".",0)+1:url.find(".",11)])
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
        self.urls=[]
        for url in self.originurls:
            self.urls.append(self.dealUrl(url))

    def findContactPageUrl(self,url):
        result=""
        if not url:
            self.contacturls.append(result)
            return result
        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')

        support=soup.find("a",{"href":re.compile(r".*?support.*?",re.DOTALL|re.IGNORECASE)})
        if support:
            if support["href"].startswith("/"):
                self.contacturls.append(url+support["href"])
                return url+support["href"]
            elif len(support["href"])<20:
                self.contacturls.append(url+"/"+support["href"])
                return url+"/"+support["href"]
            else:
                self.contacturls.append(support["href"])
                return support["href"]

        contact=soup.find("a",{"href":re.compile(r".*?contact.*?",re.DOTALL|re.IGNORECASE)})
        if contact:
            if contact["href"].startswith("/"):
                self.contacturls.append(url+contact["href"])
                return url+contact["href"]
            elif len(contact["href"])<20:
                self.contacturls.append(url+"/"+contact["href"])
                return url+"/"+contact["href"]
            else:
                self.contacturls.append(contact["href"])
                return contact["href"]

        about=soup.find("a",{"href":re.compile(r".*?about.*?",re.DOTALL|re.IGNORECASE)})
        if about:
            if about["href"].startswith("/"):
                self.contacturls.append(url+about["href"])
                return url+about["href"]
            elif len(about["href"])<20:
                self.contacturls.append(url+"/"+about["href"])
                return url+"/"+about["href"]
            else:
                self.contacturls.append(about["href"])
                return about["href"]

        self.contacturls.append("")
        return ""

    def buildContactUrlList(self):
        self.contacturls=[]
        threads=[]
        for url in self.urls:
            t=threading.Thread(target=self.findContactPageUrl,args=(url,))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def dealContactPage(self,url):
        if not url:
            self.addresses.append("")
            self.tels.append("")
            self.emails.append("")
            self.rawInformations.append("")
            return
            #url="http://www.simplyled.co.uk/Contact"
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
        for t in threads:
            t.join()


    def formTupleList(self):
        tupleList=[]
        print len(self.keywords),len(self.urls),len(self.names),len(self.countries),len(self.emails),len(self.addresses),len(self.tels),len(self.rawInformations)

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
        if self.websiteFiltered(onetuple[1]):
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

    def websiteFiltered(self,url):
        if not self.filterWebs:
            f=open("FilterRegular.txt",'r')
            self.filterWebs=f.readlines()
            f.close()
        for filterweb in self.filterWebs:
            if filterweb.rstrip() in url:
                return True
        return False

    def main(self):
        while self.fetchFromDB():
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
    finder.main()
