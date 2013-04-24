#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
主要包含了Keywords.txt以及Location.txt的文件输入
"""

def readKeywords():
    print "Reading keywords.txt file"
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

def getCountries():
    f=open("../InputFiles/Country.txt",'r')
    country=f.readlines()
    f.close()
    countries=[]
    if len(country)==0:
        return []
    else:
        for onecountry in country:
            countries.append(onecountry.strip())
        return countries

def contactPageRegular():
    f=open("../InputFiles/contactPageRegular.txt",'r')
    keys=f.readlines()
    f.close()
    words=[]
    for key in keys:
        words.append(key.rstrip().lower())
    return words

def formPageRegular():
    f=open("../InputFiles/formPageRegular.txt",'r')
    keys=f.readlines()
    f.close()
    words=[]
    for key in keys:
        words.append(key.rstrip().lower())
    return words