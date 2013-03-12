#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
主要包含了邮箱过滤以及网站过滤规则
"""
filterMails=[]
filterWebs=[]
def mailFiltered(url):
    global filterMails
    if not filterMails:
        f=open("../InputFiles/FilterMails.txt",'r')
        filterMails=f.readlines()
        f.close()
    for filtermail in filterMails:
        if filtermail.rstrip().lower() in url.lower():
            return True
    return False


def websiteFiltered(url):
    global filterWebs
    if not filterWebs:
        f=open("../InputFiles/FilterRegular.txt",'r')
        filterWebs=f.readlines()
        f.close()
    for filterweb in filterWebs:
        if filterweb.rstrip().lower() in url.lower():
            return True
    return False