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
        print "正在从数据库中获取数据"
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
        contactUrl=contactFinder.findContactPageUrl(url)
        result=contactFinder.dealContactPage(contactUrl)
        email=result[2]
        print "找到email: ",result[2]
        self.homepageUrls[i]=url
        self.urls[i]=contactUrl
        self.emails[i]=email

    def buildInformationList(self):
        threads=[]
        for i in range(len(self.names)):
            t=threading.Thread(target=self.getInformation,args=(i,))
            t.setDaemon(True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join(300)

    def updateInformaionDB(self):
        """
        更新数据库中处理过的Informaion公司信息
        """
        for i in range(len(self.names)):
            sql="""UPDATE Informaion SET SearchTimes="1" AND Email=%s WHERE Name="%s" """ % (self.emails[i],self.names[i])
            try:
                self.cur.execute(sql)
                print "更新该条目的信息",self.names[i],"  ",self.emails[i]
            except BaseException,e:
                print e,"无法更新SearchTimes参数 ."
        try:
            self.con.commit()
        except BaseException,e:
            print e,"无法更新SearchTimes参数 ."

    def main(self,threadlimit):
        #获取待补全的队列
        self.threadlimit=threadlimit
        print "程序开始"
        while self.fetchFromDB(threadlimit):
            self.buildInformationList()
            self.updateInformaionDB()
            self.initList()
        print "程序执行完毕"

if __name__=="__main__":
    threadlimit=raw_input("请输入线程数（默认为10），使信息补全程序开始运行：")
    complete=InforCompletion()
    complete.main(int(threadlimit))