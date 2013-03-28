#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
补全Information数据库中缺失的信息
"""
import sqlite3,threading
import sys
sys.path.append("..")
from WebSearchModule import ContactInforFinder,UrlFinder
urlFinder=UrlFinder.GoogleSpider()
contactFinder=ContactInforFinder.ContactFinder()


class InforCompletion():
    def __init__(self):
        #数据库连接
        self.con = sqlite3.connect('../database.db')
        self.cur = self.con.cursor()

        self.threadlimit=10
        #要补全的参数
        self.homepageUrls=[]
        self.urls=[]
        self.names=[]
        self.emails=[]

    def fetchFromDB(self,limit=10,database="Information"):
        print "Getting information from Database."
        self.cur.execute("""SELECT * FROM %s WHERE SearchTimes=0 AND Email="" Limit %d""" % (database,limit))
        result=self.cur.fetchmany(limit)
        if result:
            for i in range(0,len(result)):
                try:
                    self.names.append(result[i][4])
                except:
                    print "finish!"
                    return False
            return True
        else:
            return False

    def initList(self):
        self.names=[]
        self.homepageUrls=["" for x in range(self.threadlimit)]
        self.urls=["" for x in range(self.threadlimit)]
        self.emails=["" for x in range(self.threadlimit)]

    def getInformation(self,i):
        name=self.names[i]
        url=urlFinder.getBestUrl(name)
        if not url:
            return
        contactUrl=contactFinder.findContactPageUrl(url)
        if contactUrl:
            result=contactFinder.dealContactPage(contactUrl)
        else :
            result=""
        if result:
            email=result[2]
            if email:
                print "got email: ",result[2]
                self.emails[i]=email

        self.homepageUrls[i]=url
        self.urls[i]=contactUrl


    def buildInformationList(self):
        threads=[]
        for i in range(len(self.names)):
            t=threading.Thread(target=self.getInformation,args=(i,))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join(60)

    def updateInformaionDB(self):
        """
        更新数据库中处理过的Informaion公司信息
        """
        for i in range(len(self.names)):
            sql="""UPDATE Information SET SearchTimes="1",Email="%s",Homepage="%s" WHERE Name="%s" """ % (self.emails[i],self.names[i],self.homepageUrls[i])
            try:
                self.cur.execute(sql)
                print "update information",self.names[i],"  ",self.emails[i]
            except BaseException,e:
                print "warning:",e
        try:
            self.con.commit()
        except BaseException,e:
            print "warning:",e

    def main(self,threadlimit):
        #获取待补全的队列
        self.threadlimit=threadlimit
        print "Program Begin:"

        while self.fetchFromDB(threadlimit):

            self.buildInformationList()
            self.updateInformaionDB()
            self.initList()
        print "Program Finish!"

if __name__=="__main__":
    threadlimit=raw_input("Please input the number of threads.(default:10),then it will start. >>>")
    complete=InforCompletion()
    complete.main(int(threadlimit))