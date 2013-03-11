#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
主要包含了Keywords.txt以及Location.txt的文件输入
"""

def readKeywords():
    print "读取keywords.txt文件中"
    f=open("../InputFiles/keywords.txt",'r')
    keys=f.readlines()
    f.close()
    words=[]
    for key in keys:
        words.append(key.rstrip().lower())
    return words

def getLocals():
    f=open("../InputFiles/Location.txt",'r')
    locals=f.readlines()
    f.close()
    location=[]
    if len(locals)==0:
        return []
    else:
        for local in locals:
            location.append(local.strip())
        return location
