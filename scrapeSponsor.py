import concurrent.futures
import requests
from multiprocessing import Pool
import random 
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil import parser
import time
import os
import sys
import subprocess
from __builtin__ import True
from timeit import default_timer as timer

start = timer()
def getPort():
    upper = 499
    lower = 2
    r = (int) (random.random() * (upper - lower)) + lower
    port = ""
    if (r < 10): port = "3000"+str(r)
    elif (r >= 10 and r <= 99): port = "300" + str(r)
    elif (r >= 100 and r <= 249): port = "30" + str(r)
    elif (r >= 250 and r <= 499): 
        r = r + 8
        port = "32" + str(r)
      
    proxies = {
               'http': 'http://127.0.0.1:'+port
               }
    return proxies

def parse(url):
    proxies = getPort()
    #check if port is open
    try:
        #page = requests.get(url, proxies=proxies)
        page = requests.get(url)
    except:
        proxies = getPort()
        #page = requests.get(url, proxies=proxies)
        page = requests.get(url)
    return page.content
        
#fill locs, get timestamp
ts = int(time.time())
ts_str = str(ts)

locs = []
locs.append("la")
locs.append("imperial")
locs.append("washington")
locs.append("upstateca")
locs.append("sfbay")
locs.append("centralcoast")
locs.append("sandiego")
locs.append("oregon")
locs.append("nevada")
locs.append("sanjoaquinvalley")
locs.append("sacramento")
locs.append("newyork")
locs.append("southflorida")
locs.append("burlington")
locs.append("newjersey")
locs.append("maine")
locs.append("northcarolina")
locs.append("daytona")
locs.append("georgia")
locs.append("newhampshire")
locs.append("pennsylvania")
locs.append("westvirginia")
locs.append("southwestflorida")
locs.append("rhodeisland")
locs.append("delaware")
locs.append("michigan")
locs.append("ohio")
locs.append("northwestflorida")
locs.append("massachusetts")
locs.append("northflorida")
locs.append("southcarolina")
locs.append("maryland")
locs.append("connecticut")
locs.append("virginia")
locs.append("dc")
locs.append("indiana")
locs.append("upstateny")
locs.append("southdakota")
locs.append("illinois")
locs.append("northeasttexas")
locs.append("northdakota")
locs.append("southeasttexas")
locs.append("nebraska")
locs.append("wisconsin")
locs.append("iowa")
locs.append("louisiana")
locs.append("kansas")
locs.append("tennessee")
locs.append("arkansas")
locs.append("missouri")
locs.append("kentucky")
locs.append("southtexas")
locs.append("alabama")
locs.append("mississippi")
locs.append("minnesota")
locs.append("centraltexas")
locs.append("oklahoma")
locs.append("arizona")
locs.append("montana")
locs.append("newmexico")
locs.append("westtexas")
locs.append("colorado")
locs.append("wyoming")  
locs.append("idaho")
locs.append("utah")
locs.append("alaska")
locs.append("hawaii")

urls = []
for loc in locs:
    #location subfolder in sponsor subfloder in scrape-ads
    directory = '/scrape-data/sponsor_ads/'+loc+'/'
    try :
        os.makedirs(directory)
    except OSError:
        pass
    subprocess.call(["sudo","chmod","777",directory])
    #the day/timestamp subfolder in location
    os.makedirs(directory+ts_str)
    #log file
    log = open(directory+ts_str+'/log.txt', 'w')
    print loc
    log.write('scraping loc : ')
    log.write(loc)
    log.write("...") 
    urls.append("http://"+loc+".backpage.com/FemaleEscorts/?layout=date")
    urls.append("http://"+loc+".backpage.com/BodyRubs/?layout=date")
    urls.append("http://"+loc+".backpage.com/Strippers/?layout=date")
    urls.append("http://"+loc+".backpage.com/Domination/?layout=date")
    urls.append("http://"+loc+".backpage.com/TranssexualEscorts/?layout=date")
    urls.append("http://"+loc+".backpage.com/MaleEscorts/?layout=date")
    urls.append("http://"+loc+".backpage.com/Datelines/?layout=date")
    urls.append("http://"+loc+".backpage.com/AdultJobs/?layout=date")
    
    #scrape the 8 pages   
    pool = Pool(8)
    results = pool.map(parse, urls)
    log.write('done!')
    log.write("\n")
    print 'done'
    #all 8 files
    log.write('saving files...')
    service = ''
    for i in range(0,7):
        if (i==0) : service = 'escorts'
        elif (i==1) : service = 'bodyrubs'
        elif (i==2) : service = 'strippers'
        elif (i==3) : service = 'domination'
        elif (i==4) : service = 'transescorts'
        elif (i==5) : service = 'maleescorts'
        elif (i==6) : service = 'datelines'
        elif (i==7) : service = 'adultjobs'
        g = open(directory+ts_str+'/'+service+'.txt', 'w')
        g.write(results[i])
        g.close()
    log.write("\n")
    log.write('done!')
    log.write("\n")
    print 'saved'
elapsed_time = timer() - start
log.write("time to run : ")
log.write(str(elapsed_time))
log.write(" seconds")
log.close()
