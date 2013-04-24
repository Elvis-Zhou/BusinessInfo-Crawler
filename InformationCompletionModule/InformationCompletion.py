#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
补全Information数据库中缺失的信息
"""
import sqlite3,threading
import sys
sys.path.append("..")
from WebSearchModule import ContactInforFinder,UrlFinder
import string
from time import sleep
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
        self.formUrls=[]
        self.ids=[]
        self.countries=[]

    def fetchFromDB(self,limit=10,database="Form6"):
        print "Getting information from Database."

        self.cur.execute("""SELECT id FROM %s WHERE SearchTimes=0 Limit %d""" % (database,limit))
        result=self.cur.fetchmany(limit)
        if len(result)==1:
            return False

        if result:
            for id in result:
                try:
                    self.cur.execute("""SELECT * FROM Form1 WHERE id=%s""" % id[0])
                    one=self.cur.fetchone()

                    if one:
                        #one=one[0]
                        id,name,country=one
                        self.names.append(name)
                        self.ids.append(id)
                        self.countries.append(country)
                except BaseException,e:
                    print "warning: ",e
            return True
        else:
            return False

    def initList(self):
        self.names=[]
        self.ids=[]
        self.countries=[]
        self.homepageUrls=["" for x in range(self.threadlimit)]
        self.urls=["" for x in range(self.threadlimit)]
        self.emails=["" for x in range(self.threadlimit)]
        self.formUrls=["" for x in range(self.threadlimit)]

    def getInformation(self,i):
        name=self.names[i]
        if not name:
            return
        url=urlFinder.getBestUrl(name)
        if not url:
            return

        contactUrl=contactFinder.findContactPageUrl(url)
        if contactUrl:
            result=contactFinder.dealContactPage(contactUrl)
        else:
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
            t.join()

    def updateInformaionDB(self):
        """
        更新数据库中处理过的Informaion公司信息
        """
        for i in range(len(self.names)):
            name=self.names[i]
            if not name:
                continue

            #插入form3,email
            sql=""
            try:
                #插入表3，email
                emails=self.emails[i].split("\n")
                if len(emails)>1:
                    for email in emails:
                        sql='INSERT INTO Form3 (id,Email) VALUES(%s,"%s")' % (self.ids[i],email)
                        self.cur.execute(sql)
                else:
                    sql='INSERT INTO Form3 (id,Email) VALUES(%s,"%s")' % (self.ids[i],self.emails[i])
                    self.cur.execute(sql)
            except sqlite3.ProgrammingError,e:
                sleep(1)
                self.cur.execute(sql)
                print e,"sleep 1s"
            except BaseException,e:
                print "warning:",e

            #更新form6
            sql="""UPDATE Form6 SET SearchTimes=1 WHERE id=%s """ % (self.ids[i])
            try:
                self.cur.execute(sql)
            except BaseException,e:
                print "warning:",e

            #更新form5
            sql="""UPDATE Form5 SET Url="%s",Homepage="%s",Formurl="%s" WHERE id=%s """ % (self.urls[i],self.homepageUrls[i],self.formUrls[i],self.ids[i])
            try:
                self.cur.execute(sql)
                print "update information",self.names[i],"  ",self.emails[i]
            except BaseException,e:
                print "warning:",e

        try:
            self.con.commit()
            print "Successfully updated!"
        except BaseException,e:
            print "warning:",e

    def main(self,threadlimit):
        #获取待补全的队列
        self.threadlimit=threadlimit
        print "Program Begin:"
        self.initList()
        while self.fetchFromDB(threadlimit):
            self.buildInformationList()
            self.updateInformaionDB()
            self.initList()
        print "Program Finish!"

if __name__=="__main__":
    threadlimit=raw_input("Please input the number of threads.(default:10),then it will start. >>>")
    if not threadlimit:
        threadlimit=10
    else:
        threadlimit=string.atoi(threadlimit)
    complete=InforCompletion()
    complete.main(threadlimit)