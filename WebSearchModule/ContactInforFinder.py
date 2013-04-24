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
import sys
sys.path.append("..")
from InputModule import Inputs,FliterRegular
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
        self.formUrls=[]
        self.categories=[]

        self.filterWebs=[]
        self.filterMails=[]

        self.contactPageRegular=[]
        self.formPageUrlRegular=[]

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
            except :
                i+=1
            if i>=5:break
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
        print "Fetch urls from Database"
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

    def dealUrl(self,url):
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

    def findContactPageUrlIndex(self,url,i):
        result=""
        if not url:
            self.contacturls[i]=result
            return result
        if not url.startswith("http"):
            self.contacturls[i]=result
            return result
        if FliterRegular.websiteFiltered(url):
            return result
        print "Dealing the url to get the contact page:",url

        self.contactPageRegular=Inputs.contactPageRegular()

        htmlfile=self.getpage(url)
        soup=BeautifulSoup(htmlfile,'lxml')

        shortUrllength=25

        for regular in self.contactPageRegular:
            contact=soup.find("a",{"href":re.compile(r".*?%s.*?" % regular,re.DOTALL|re.IGNORECASE)})
            if contact:
                if contact["href"].startswith("/"):
                    self.contacturls[i]=url+contact["href"]
                    return url+contact["href"]
                elif len(contact["href"])<shortUrllength:
                    self.contacturls[i]=url+"/"+contact["href"]
                    return url+"/"+contact["href"]
                else:
                    self.contacturls[i]=contact["href"]
                    return contact["href"]
        return ""

    def findContactPageUrl(self,url):
        result=""
        if not url:
            return result
        if not url.startswith("http"):
            return result
        if FliterRegular.websiteFiltered(url):
            return
        print "Dealing the url to get the contact page:",url

        self.contactPageRegular=Inputs.contactPageRegular()
        shortUrllength=25

        htmlfile=self.getpage(url)
        try:
            soup=BeautifulSoup(htmlfile,'lxml')
        except BaseException:
            return ""

        for regular in self.contactPageRegular:
            contact=soup.find("a",{"href":re.compile(r".*?%s.*?" % regular,re.DOTALL|re.IGNORECASE)})
            if contact:
                if contact["href"].startswith("/"):
                    #print url+contact["href"]
                    return url+contact["href"]
                elif len(contact["href"])<shortUrllength:
                    #print url+"/"+contact["href"]
                    return url+"/"+contact["href"]
                else:
                    #print contact["href"]
                    return contact["href"]
        return ""

    def buildContactUrlList(self):
        threads=[]
        index=0
        for url in self.urls:
            t=threading.Thread(target=self.findContactPageUrlIndex,args=(url,index,))
            index+=1
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def dealContactPageIndex(self,url,i):
        result=("","","","")
        if not url:
            return result
        if not url.startswith("http"):
            return result
        print "Analyzing the web page to get the contact information: ",url

        htmlfile=self.getpage(url)
        if not htmlfile:
            t=("","","","")
            return t
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

    def dealContactPage(self,url):
        result=("","","","")
        if not url:
            return result
        if not url.startswith("http"):
            return result
        print "Analyzing the web page to get the contact information: ",url
        htmlfile=self.getpage(url)

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

        address=""
        if addresses:
            address=addresses[0].strip()

        tel=""
        if tels:
            tel=tels[0].strip()

        email=""
        if emails:
            tempemails=[]
            for e in emails:
                tempemails.append(e.strip())
            email="\n".join(tempemails)


        try:
            rawinformation=ExtMainText.main(htmlfile)
        except:
            rawinformation=""

        result=(address,tel,email,rawinformation)

        return result

    def buildInformationList(self):
        threads=[]
        index=0
        for url in self.contacturls:
            t=threading.Thread(target=self.dealContactPageIndex,args=(url,index,))
            index+=1
            t.setDaemon(True)
            threads.append(t)
            t.start()
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
            try:
                category=self.categories[i]
            except:
                category=""

            try:
                url=self.contacturls[i]
            except:
                url=""

            try:
                homepage=self.urls[i]
            except:
                homepage=""

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
            searchTimes=0
            formUrl=""
            tupleList.append((keyword,
                              category,
                              url,
                              homepage,
                              name,
                              country,
                              email,
                              address,
                              tel,
                              rawInformation,
                              searchTimes,
                              formUrl)
            )

        return tupleList

    def saveToInformationDB(self,onetuple):
        """
        把单条的页面中的公司信息保存到数据库
        不需要外部调用
        """
        if FliterRegular.websiteFiltered(onetuple[2]):
            return
        if not onetuple[2].strip():
            return
        if FliterRegular.mailFiltered(onetuple[6]):
            return
        sql='SELECT ID FROM Form1 WHERE Name="%s" AND Country="%s"' % (onetuple[4],onetuple[5])
        self.cur.execute(sql)
        result=self.cur.fetchone()
        if result:
            return

        nowid=0
        try:
            #插入ID
            sql='INSERT INTO ID (id) VALUES(NULL)'
            self.cur.execute(sql)
            self.con.commit()
            sql='SELECT max(id) FROM ID '
            self.cur.execute(sql)
            nowid=self.cur.fetchone()
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e
        if not nowid:
            return
        else:
            nowid=nowid[0]

        try:
            #插入表1,name
            sql='INSERT INTO Form1 (id,Name,Country) VALUES(%s,"%s","%s")' % (nowid,onetuple[4],onetuple[5])
            self.cur.execute(sql)
            self.con.commit()
            print "Finish the company: " ,onetuple[4],"   ",onetuple[5]
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

        try:
            #插入表2,address
            sql='INSERT INTO Form2 (id,Address,Information) VALUES(%s,"%s","%s")' % (nowid,onetuple[7],onetuple[9])
            self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

        try:
            #插入表3，email
            emails=onetuple[6].split("\n")
            if len(emails)>1:
                for email in emails:
                    sql='INSERT INTO Form3 (id,Email) VALUES(%s,"%s")' % (nowid,email)
                    self.cur.execute(sql)
            else:
                sql='INSERT INTO Form3 (id,Email) VALUES(%s,"%s")' % (nowid,onetuple[6])
                self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

        try:
            #插入表4，tel
            tels=onetuple[8].split("\n")
            if len(tels)>1:
                for tel in tels:
                    sql='INSERT INTO Form4 (id,Tel) VALUES(%s,"%s")' % (nowid,tel)
                    self.cur.execute(sql)
            else:
                sql='INSERT INTO Form4 (id,Tel) VALUES(%s,"%s")' % (nowid,onetuple[8])
                self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

        try:
            #插入表5,urls
            sql='INSERT INTO Form5 (id,Homepage,Url,Formurl) VALUES(%s,"%s","%s","%s")' % (nowid,onetuple[3],onetuple[2],onetuple[11])
            self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

        try:
            #插入表6,searchtimes
            sql='INSERT INTO Form6 (id,SearchTimes) VALUES(%s,"%s")' % (nowid,onetuple[10])
            self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e


        try:
            #插入表7,keyword
            sql='INSERT INTO Form7 (id,Keyword,Category) VALUES(%s,"%s","%s")' % (nowid,onetuple[0],onetuple[1])
            self.cur.execute(sql)
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.cur.execute(sql)
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e


        try:
            self.con.commit()
        except sqlite3.ProgrammingError,e:
            sleep(1)
            self.con.commit()
            print e,"sleep 1s"
        except BaseException,e:
            print "warning:",e

    def saveList(self,tupleList):
        count=len(tupleList)
        for i in range(0,count):
            self.saveToInformationDB(tupleList[i])

        try:
            self.con.commit()
        except BaseException,e:
            print "warning",e

    def updateUrlDB(self):
        for url in self.originurls:
            sql="""UPDATE Urls SET Dealed="1" WHERE Url="%s" """ % url
            try:
                self.cur.execute(sql)
            except BaseException,e:
                print "warning",e,"cannot update Dealed ."
        try:
            self.con.commit()
        except BaseException,e:
            print "warning",e,"cannot update Dealed ."

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
        self.formUrls=["" for i in range(int(threadLimit))]
        self.categories=["" for i in range(int(threadLimit))]

    def main(self,threadLimit=10):
        print "Program Begin:"
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
        print "All finish."

if __name__ == "__main__":
    finder=ContactFinder()

    threadLimit=raw_input("please input the number of threads ,default: 10 >>>")
    finder.main(threadLimit)
    #finder.initList()
