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
import traceback
import ssh_ccie13
import ssh_backup1
import codecs
import pickle

start = timer()
count_g = 0
#fill locs, get timestamp
ts = int(time.time())
ts_str = str(ts)
log_master = open('/home/ubuntu/'+ts_str+'_log', 'w')
sys.stdout = open('/home/ubuntu/'+ts_str+'_stdout', 'w')
sys.stderr = open('/home/ubuntu/'+ts_str+'_stderr', 'w')
failed_proxies = []
def getPort():
    upper = 499
    lower = 2
    r = (int) (random.random() * (upper - lower)) + lower
    port = ""
    if (r < 10):
        port = "3000"+str(r)
    elif (r >= 10 and r <= 99):
        port = "300" + str(r)
    elif (r >= 100 and r <= 249):
        port = "30" + str(r)
    elif (r >= 250 and r <= 499):
        r = r + 8
        port = "32" + str(r)
        
    proxies = {
               'http': 'http://127.0.0.1:'+port
               }
    return proxies

#check the length of failed_proxies before calling parse
#if failed_proxies is at max length, then ssh in
def parse(url):

    global failed_proxies
    used_proxies = []
    global log_master
    proxies = getPort()
    headers = {'Accept-Encoding': ''}
    #try twice with pandacat proxy from master
    #if fails, try IP
    #if that fails also, you will ssh into ccie13
    try:
        log_master.write('parse try pandacat ')
        log_master.write(url)
        log_master.write('\n')
        log_master.flush()
        page = requests.get(url, proxies=proxies, headers = headers, timeout=10)
        #print page.headers
        stuff = page.content
    except: 
        log_master.write('had to except ')
        log_master.write(url)
        var = traceback.format_exc()
        log_master.write('\n')
        log_master.write(var)
        log_master.write('\n')
        log_master.flush()
        used_proxies.append(str(proxies))
        failed_proxies.append(str(proxies))
        while (str(proxies) in used_proxies):
            proxies = getPort()
        try:
            log_master.write('parse try pandacat 2 ')
            log_master.write(url)
            log_master.write('\n')
            log_master.flush()
            page = requests.get(url, proxies=proxies, headers = headers, timeout=10)
            stuff = page.content
        except:
            log_master.write('had to except twice ')
            log_master.write(url)
            log_master.write('\n')
            var = traceback.format_exc()
            log_master.write(var)
            log_master.write('\n')
            log_master.flush()
            used_proxies.append(str(proxies))
            failed_proxies.append(str(proxies))
            try:
                #log in using IP
                log_master.write('parse try EC2 IP ')
                log_master.write(url)
                log_master.write('\n')
                log_master.flush()
                page = requests.get(url, headers = headers, timeout=10)
                stuff = page.content
            except:
                log_master.write('error on ')
                log_master.write(url)
                log_master.write(" ")
                var = traceback.format_exc()
                log_master.write(var)
                log_master.write('\n')
                log_master.flush()
                stuff = None

    return stuff

def getLinks(soup):
    ad_links = []
    service = []
    tags = []
    ad_list = soup.findAll('div', attrs={'class': re.compile(r"cat \d.*")})
    #print "# ads :", len(ad_list)
    for ad in ad_list:
        for link in ad.findAll('a',attrs={'href': re.compile(r"\d+$")}):
            ad_links.append(link['href'])
            #print link['href']
        for tag in ad.findAll('a',attrs={'class' : "resultsSectionLabel"}):
            service.append(tag.text)
            #print tag.text
        hastag = False
        for tag in ad.findAll('span',attrs={'class' : "resultsRegionLabel"}):
            tags.append(tag.text)
            hastag = True
        if (hastag == False):
            tags.append('')
            #print tag.text
    return ad_links, service, tags

def getDate(ad):
    if (ad is None):
        return None
    soup = BeautifulSoup(ad,'lxml')
    info = soup.findAll('div', attrs={'class':'adInfo'})
    #print url
    if len(info)<1: 
        print 'no ad'
        return None
    else:
        date = info[0].text.replace('\r\n', '').replace("Posted: ", "").strip().replace(",", "").split(" ",1)[1]
        date_object = parser.parse(date)
        #print date_object
        return date_object

def storeAds(ad,url,c,now,oneHourAgo,loc,ts_str,ad_next,url_next,g):
    global count_g
    if (ad == None):
        #try one more time
        headers = {'Accept-Encoding': ''}
        try:
            page = requests.get(url, headers = headers, timeout=10)
            ad = page.content
        except:
            log_master.write("failed last backup ")
            log_master.write(url)
            log_master.write("\n")
        if (ad == None):
            g.write(url)
            g.write(" ")
            g.write("failed to get")
            g.write("\n")
            g.flush()
            return True, None
    date_object = getDate(ad)
    #print url
    #print date_object
    if (date_object == None):
        #try one more time
        date_object = getDate(ad)
        if (date_object == None):
            index = url.rfind('/')
            id = str(url[index+1:len(url)])
            #f = open('/Users/cusgadmin/BackPageStylometry/PriceExtraction/ads/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
            f = open('/scrape-data/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
            f.write(ad)
            f.flush()
            f.close()
            g.write(url)
            g.write(" ")
            g.write("date object empty")
            g.write("\n")
            g.flush()
            return True, None
    #print the date
    else :
        index = url.rfind('/')
        id = str(url[index+1:len(url)])
        #f = open('/Users/cusgadmin/BackPageStylometry/PriceExtraction/ads/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
        f = open('/scrape-data/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
        t = tags[c].encode('utf-8')
        s = service[c].encode('utf-8')
        substring = "<div style=\"padding-left:2em;\">"#+"\n"+"&bull; Location:"
        start = ad.index(substring) + len(substring)
        end = ad.index("</div>", start)
        locs = ad[start:end]
        f.write(ad)
        f.write(t)
        f.write(s)
        f.flush()
        f.close()
        g.write(url)
        count_g = count_g + 1
        g.write(" ")
        g.write(str(date_object))
        g.write(" ")
        g.write(t)
        g.write(" ")
        g.write(locs.replace("&bull; Location:","").strip())
        t_edit = t[1:len(t)-1]
        if (t_edit not in locs.replace("&bull; Location:","").strip()):
            g.write(" non-matching locs")
        g.write("\n")
        g.flush()
        return True, date_object
    '''
    #if ((now >= date_object) and (oneHourAgo <= date_object)):
    elif (oneHourAgo <= date_object):
        index = url.rfind('/')
        id = str(url[index+1:len(url)])
        #f = open('/Users/cusgadmin/BackPageStylometry/PriceExtraction/ads/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
        f = open('/scrape-data/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
        t = tags[c].encode('utf-8')
        s = service[c].encode('utf-8')
        substring = "<div style=\"padding-left:2em;\">"#+"\n"+"&bull; Location:"
        start = ad.index(substring) + len(substring)
        end = ad.index("</div>", start)
        locs = ad[start:end]
        f.write(ad)
        f.write(t)
        f.write(s)
        f.close()
        g.write(url)
        count_g = count_g + 1
        g.write(" ")
        g.write(str(date_object))
        g.write(" ")
        g.write(t)
        g.write(" ")
        g.write(locs.replace("&bull; Location:","").strip())
        g.write("\n")
        return True
    else : 
        if c == 299 : return True
        date_next = getDate(ad_next)
        if (date_next == None): 
            #try one more time
            date_next = getDate(ad_next)
            if (date_next == None):
                return True
        #check if the one below it is within
        #if ((now >= date_next) and (oneHourAgo <= date_next)):
        elif (oneHourAgo <= date_next):
            index = url_next.rfind('/')
            id = str(url_next[index+1:len(url_next)])
            #f = open('/Users/cusgadmin/BackPageStylometry/PriceExtraction/ads/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
            f = open('/scrape-data/'+loc+'/'+ts_str+'/'+id+'.txt', 'w')
            t = tags[c+1].encode('utf-8')
            s = service[c+1].encode('utf-8')
            substring = "<div style=\"padding-left:2em;\">"#+"\n"+"&bull; Location:"
            start = ad.index(substring) + len(substring)
            end = ad.index("</div>", start)
            locs = ad[start:end]
            f.write(ad)
            f.write(t)
            f.write(s)
            f.close()
            g.write(url)
            count_g = count_g + 1
            g.write(" ")
            g.write(str(date_object))
            g.write(" ")
            g.write(t)
            g.write(" ")
            g.write(locs.replace("&bull; Location:","").strip())
            g.write("\n")
            return True
        else : return False
        '''

def run_ccie13(links,line):
    log_master.write(line)
    log_master.write("\n")
    ssh_ccie13.do(links)
    r = pickle.load(open('/home/ubuntu/results', 'rb'))
    temp_log = open('/home/ubuntu/ccie13_log', 'r').read()
    log_master.write(temp_log)
    log_master.flush()
    return r

def run_backup1(links, chosen, line):
    log_master.write(line)
    log_master.write(chosen)
    log_master.write("\n")
    ssh_backup1.do(links, chosen)
    r = pickle.load(open('/home/ubuntu/results_bu1', 'rb'))
    temp_log = open('/home/ubuntu/bu1_log', 'r').read()
    log_master.write(temp_log)
    log_master.flush()
    return r

#get current time
now = datetime.now()
now = now.replace(second=0, microsecond=0)

locs = []
locs.append(sys.argv[2])
timezone = sys.argv[1]
if (timezone == 'EST'):
    now = now + timedelta(hours=3)
elif (timezone == 'CST'):
    now = now + timedelta(hours=2)
elif (timezone == 'MST'):
    now = now + timedelta(hours=1)
elif (timezone == 'AST'):
    now = now - timedelta(hours=1)
elif (timezone == 'HST'):
    now = now - timedelta(hours=2)
oneHourAgo = now - timedelta(hours=2)
print now
print oneHourAgo

urls = []
for loc in locs:
    '''
    if (num_pages[loc]) == 6:
        print 'getting first 6 pages of ' + loc + '...'
        urls.append("http://"+loc+".backpage.com/adult/?layout=date")
        urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=2")
        urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=3")
        urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=4")
        urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=5")
        urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=6")
    elif (num_pages[loc]) == 4:
    '''
    print 'getting first 5 pages of ' + loc + '...'
    urls.append("http://"+loc+".backpage.com/adult/?layout=date")
    urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=2")
    urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=3")
    urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=4")
    urls.append("http://"+loc+".backpage.com/adult/?layout=date&page=5")
    
#scrape the first, second and third pages for all locs    
pool = Pool(8)
#check that panda cat is open, or use EC2 IP's
results = pool.map(parse, urls)
#if tried all of them and first page failed, first try ccie13
#then try the other backups
if (len(results) == 0):
    results = run_ccie13(urls, "pages switch to ccie13 len0 ")
elif (results[0] is None):
    results = run_ccie13(urls, "pages switch to ccie13 firstNone ")

backups = ['ec2-xx-xx-xxx']
prev_chose = None
while (len(results) == 0):
    if (prev_chose is None): chosen = random.choice(backups)
    else:
        while (chosen == prev_chose):
            chosen = random.choice(backups)
    prev_chose = chosen
    results = run_backup1(urls, chosen, "pages switch to backup len0 ")
prev_chose = None
while (results[0] is None):
    if (prev_chose is None): chosen = random.choice(backups)
    else:
        while (chosen == prev_chose):
            chosen = random.choice(backups)
    prev_chose = chosen
    results = run_backup1(urls, chosen, "pages switch to backup firstNone ")
print 'done!'

i = 0
for loc in locs:  
    backups = ['ec2-xx-xx-xxx']
    #make necessary directories
    directory= '/scrape-data/'+loc+'/'
    
    try : 
        os.makedirs(directory)
        #subprocess.call(["sudo", "mkdir", directory])
    except OSError:
        pass

    subprocess.call(["sudo","chmod","777",directory])
    os.makedirs(directory+ts_str)
    subprocess.call(["sudo","chmod","777",directory+ts_str])
    
    #make file for listing of link, timestamps for this location
    g = open(directory+ts_str+'/ads.txt', 'w')

    #make log file
    log = open(directory+ts_str+'/log.txt', 'w')
    log.write(str(now))
    log.write("\n")
    log.write(str(oneHourAgo))
    log.write("\n")
    log.write("loc : ")
    log.write(loc)
    log.write("\n")
    
    #if nothing in the first page, first try ccie13
    if (results[i] is None):
        link = ["http://"+loc+".backpage.com/adult/?layout=date"]
        r = run_ccie13(link, "page 1 missing! try again with ccie13 ")
        results[i] = r[0]
    #then try backup
    prev_chose = None
    while (results[i] is None):
        link = ["http://"+loc+".backpage.com/adult/?layout=date"]
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(link, chosen, "page 1 missing! try again with ")
        results[i] = r[0]

    #get ads from first page
    soup = BeautifulSoup(results[i],'lxml')
    ad_links, service, tags = getLinks(soup)

    log.write('# tags ')
    log.write(str(len(tags)))
    log.write("\n")
    log.write('# services ')
    log.write(str(len(service)))
    log.write("\n")
    log.write('# ad links ')
    log.write(str(len(ad_links)))
    log.write("\n")
    
    #if ad_links is empty, first try ccie13
    if (len(ad_links) == 0):
        link = ["http://"+loc+".backpage.com/adult/?layout=date"]
        r = run_ccie13(link, "no ad links found page 1! try again with ccie13 ")
        results[i] = r[0]
        if results[i] is not None:
            soup = BeautifulSoup(results[i],'lxml')
            ad_links, service, tags = getLinks(soup)
    #then try backup
    prev_chose = None
    while (len(ad_links) == 0):
        link = ["http://"+loc+".backpage.com/adult/?layout=date"]
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(link, chosen, "no ad links found page 1! try again with ")
        results[i] = r[0]
        if results[i] is not None:
            soup = BeautifulSoup(results[i],'lxml')
            ad_links, service, tags = getLinks(soup)
        
    log.write('# tags ')
    log.write(str(len(tags)))
    log.write("\n")
    log.write('# services ')
    log.write(str(len(service)))
    log.write("\n")
    log.write('# ad links ')
    log.write(str(len(ad_links)))
    log.write("\n")

    #for each ad grab all the html
    log.write('grabbing all ads pg 1...')
    log.write("\n")
    A = ad_links[:len(ad_links)/2]
    log.write(str(A))
    log.write("\n")
    B = ad_links[len(ad_links)/2:]
    log.write(str(B))
    log.write("\n")
    page_resultsA = pool.map(parse, A)
    #if tried all of them and failed, first try ccie13
    #then try backup
    if (len(page_resultsA) == 0):
        r = run_ccie13(A, "pg1A switch to ccie13 len0 ")
        page_resultsA = r
    prev_chose = None
    while (len(page_resultsA) == 0):
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(A, chosen, "pg1A switch to backup len0 ")
        page_resultsA = r
    if (page_resultsA[0] is None):
        r = run_ccie13(A, "pg1A switch to ccie13 len0 ")
        page_resultsA = r
    prev_chose = None
    while (page_resultsA[0] is None):
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(A, chosen, "pg1A switch to backup len0 ")
        page_resultsA = r
        
    log.write('a grabbed')
    log.write('\n')
    page_resultsB = pool.map(parse, B)
    #if tried all of them and failed, first try ccie13
    #then try backup
    if (len(page_resultsB) == 0):
        r = run_ccie13(B, "pg1B switch to ccie13 len0 ")
        page_resultsB = r
    prev_chose = None
    while (len(page_resultsB) == 0):
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(B, chosen, "pg1B switch to backup len0 ")
        page_resultsB = r
    if (page_resultsB[0] is None):
        r = run_ccie13(B, "pg1B switch to ccie13 len0 ")
        page_resultsB = r
    prev_chose = None
    while (page_resultsB[0] is None):
        if (prev_chose is None): chosen = random.choice(backups)
        else:
            while (chosen == prev_chose):
                chosen = random.choice(backups)
        prev_chose = chosen
        r = run_backup1(B, chosen, "pg1B switch to backup len0 ")
        page_resultsB = r
        
    log.write('b grabbed')
    log.write('\n')
    page_results = page_resultsA + page_resultsB
    log.write('done')
    log.write('\n')
    #for each ad store if within the hour
    c = 0
    last_dates = []
    for url in ad_links:
        if (c % 10 == 0) :
            log.write("on ad ")
            log.write(str(c))
            log.write("\n")
        if (c == len(ad_links) - 1) :
            log.write("on ad ")
            log.write(str(c))
            log.write("\n")
        if (c<len(ad_links)-1):
            more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,page_results[c+1],ad_links[c+1],g)
            last_dates.append(date)
        else :
             more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,None,None,g)
             last_dates.append(date)
        if (more == True) : c = c + 1
        else : break
    
    cycle = len(page_results)-1
    while (True and cycle >= 0):
        last_date = last_dates[cycle]
        if (last_date is None): 
            cycle = cycle - 1
            continue
        else: break
    
    log.write('last date : ')    
    log.write(str(last_date))
    log.write('\n')
    #if more to go, then do with page 2
    #if ((now >= last_date) and (oneHourAgo <= last_date)):
    if (oneHourAgo <= last_date):
        #if nothing in the second page, first try ccie13
        if (results[i+1] is None):
            link = ["http://"+loc+".backpage.com/adult/?layout=date&page=2"]
            r = run_ccie13(link, "page 2 missing! try again with ccie13 ")
            results[i+1] = r[0]
        #then try backup
        prev_chose = None
        while (results[i+1] is None):
            link = ["http://"+loc+".backpage.com/adult/?layout=date&page=2"]
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(link, chosen, "page 2 missing! try again with ")
            results[i+1] = r[0]

        soup = BeautifulSoup(results[i+1],'lxml')
        ad_links, service, tags = getLinks(soup)
        log.write('# tags ')
        log.write(str(len(tags)))
        log.write("\n")
        log.write('# services ')
        log.write(str(len(service)))
        log.write("\n")
        log.write('# ad links ')
        log.write(str(len(ad_links)))
        log.write("\n")
            
        #if ad_links is empty, first try ccie13
        if (len(ad_links) == 0):
            link = ["http://"+loc+".backpage.com/adult/?layout=date&page=2"]
            r = run_ccie13(link, "no ad links found page 2! try again with ccie13 ")
            results[i+1] = r[0]
            if results[i+1] is not None:
                soup = BeautifulSoup(results[i+1],'lxml')
                ad_links, service, tags = getLinks(soup)
        #then try backup
        prev_chose = None
        while (len(ad_links) == 0):
            link = ["http://"+loc+".backpage.com/adult/?layout=date&page=2"]
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(link, chosen, "no ad links found page 2! try again with ")
            results[i+1] = r[0]
            if results[i+1] is not None:
                soup = BeautifulSoup(results[i+1],'lxml')
                ad_links, service, tags = getLinks(soup)
            
        log.write('# tags ')
        log.write(str(len(tags)))
        log.write("\n")
        log.write('# services ')
        log.write(str(len(service)))
        log.write("\n")
        log.write('# ad links ')
        log.write(str(len(ad_links)))
        log.write("\n")

        #for each ad grab all the html
        log.write('grabbing all ads pg 2...')
        log.write("\n")
        A = ad_links[:len(ad_links)/2]
        log.write(str(A))
        log.write("\n")
        B = ad_links[len(ad_links)/2:]
        log.write(str(B))
        log.write("\n")
        page_resultsA = pool.map(parse, A)

        #if tried all of them and failed, first try ccie13
        #then try backup
        if (len(page_resultsA) == 0):
            r = run_ccie13(A, "pg2A switch to ccie13 len0 ")
            page_resultsA = r
        prev_chose = None
        while (len(page_resultsA) == 0):
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(A, chosen, "pg2A switch to backup len0 ")
            page_resultsA = r
        if (page_resultsA[0] is None):
            r = run_ccie13(A, "pg2A switch to ccie13 len0 ")
            page_resultsA = r
        prev_chose = None
        while (page_resultsA[0] is None):
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(A, chosen, "pg2A switch to backup len0 ")
            page_resultsA = r
            
        log.write('a grabbed')
        log.write('\n')
        page_resultsB = pool.map(parse, B)
        #if tried all of them and failed, first try ccie13
        #then try backup
        if (len(page_resultsB) == 0):
            r = run_ccie13(B, "pg2B switch to ccie13 len0 ")
            page_resultsB = r
        prev_chose = None
        while (len(page_resultsB) == 0):
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(B, chosen, "pg2B switch to backup len0 ")
            page_resultsB = r
        if (page_resultsB[0] is None):
            r = run_ccie13(B, "pg2B switch to ccie13 len0 ")
            page_resultsB = r
        prev_chose = None
        while (page_resultsB[0] is None):
            if (prev_chose is None): chosen = random.choice(backups)
            else:
                while (chosen == prev_chose):
                    chosen = random.choice(backups)
            prev_chose = chosen
            r = run_backup1(B, chosen, "pg2B switch to backup len0 ")
            page_resultsB = r
            
        log.write('b grabbed')
        log.write('\n')
        page_results = page_resultsA + page_resultsB
        log.write('done')
        log.write('\n')

        #for each ad store if within the hour
        c = 0
        last_dates = []
        for url in ad_links:
            if (c % 10 == 0) :
                log.write("on ad ")
                log.write(str(c))
                log.write("\n")
            if (c == len(ad_links) - 1) :
                log.write("on ad ")
                log.write(str(c))
                log.write("\n")
            if (c<len(ad_links) - 1):
                more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,page_results[c+1],ad_links[c+1],g)
                last_dates.append(date)
            else :
                more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,None,None,g)
                last_dates.append(date)
            if (more == True) : c = c + 1
            else : break
        
        cycle = len(page_results)-1
        while (True and cycle >= 0):
            last_date = last_dates[cycle]
            if (last_date is None): 
                cycle = cycle - 1
                continue
            else: break
        log.write('last date : ')    
        log.write(str(last_date))
        log.write('\n')
        #if more to go, then do with page 3
        #if ((now >= last_date) and (oneHourAgo <= last_date)):
        if (oneHourAgo <= last_date):
            #if nothing in the third page, first try ccie13
            if (results[i+2] is None):
                link = ["http://"+loc+".backpage.com/adult/?layout=date&page=3"]
                r = run_ccie13(link, "page 3 missing! try again with ccie13 ")
                results[i+2] = r[0]
            #then try backup
            prev_chose = None
            while (results[i+2] is None):
                link = ["http://"+loc+".backpage.com/adult/?layout=date&page=3"]
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(link, chosen, "page 3 missing! try again with ")
                results[i+2] = r[0]

            soup = BeautifulSoup(results[i+2],'lxml')
            ad_links, service, tags = getLinks(soup)
            log.write('# tags ')
            log.write(str(len(tags)))
            log.write("\n")
            log.write('# services ')
            log.write(str(len(service)))
            log.write("\n")
            log.write('# ad links ')
            log.write(str(len(ad_links)))
            log.write("\n")
            
            #if ad_links is empty, first try ccie13
            if (len(ad_links) == 0):
                link = ["http://"+loc+".backpage.com/adult/?layout=date&page=3"]
                r = run_ccie13(link, "no ad links found page 3! try again with ccie13 ")
                results[i+2] = r[0]
                if results[i+2] is not None:
                    soup = BeautifulSoup(results[i+2],'lxml')
                    ad_links, service, tags = getLinks(soup)
            #then try backup
            prev_chose = None
            while (len(ad_links) == 0):
                link = ["http://"+loc+".backpage.com/adult/?layout=date&page=3"]
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(link, chosen, "no ad links found page 3! try again with ")
                results[i+2] = r[0]
                if results[i+2] is not None:
                    soup = BeautifulSoup(results[i+2],'lxml')
                    ad_links, service, tags = getLinks(soup)
                
            log.write('# tags ')
            log.write(str(len(tags)))
            log.write("\n")
            log.write('# services ')
            log.write(str(len(service)))
            log.write("\n")
            log.write('# ad links ')
            log.write(str(len(ad_links)))
            log.write("\n")

            #for each ad grab all the html
            log.write('grabbing all ads pg 3...')
            log.write("\n")
            A = ad_links[:len(ad_links)/2]
            log.write(str(A))
            log.write("\n")
            B = ad_links[len(ad_links)/2:]
            log.write(str(B))
            log.write("\n")
            page_resultsA = pool.map(parse, A)
            #if tried all of them and failed, first try ccie13
            #then try backup
            if (len(page_resultsA) == 0):
                r = run_ccie13(A, "pg3A switch to ccie13 len0 ")
                page_resultsA = r
            prev_chose = None
            while (len(page_resultsA) == 0):
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(A, chosen, "pg3A switch to backup len0 ")
                page_resultsA = r
            if (page_resultsA[0] is None):
                r = run_ccie13(A, "pg3A switch to ccie13 len0 ")
                page_resultsA = r
            prev_chose = None
            while (page_resultsA[0] is None):
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(A, chosen, "pg3A switch to backup len0 ")
                page_resultsA = r
                
            log.write('a grabbed')
            log.write('\n')
            page_resultsB = pool.map(parse, B)
            #if tried all of them and failed, first try ccie13
            #then try backup
            if (len(page_resultsB) == 0):
                r = run_ccie13(B, "pg3B switch to ccie13 len0 ")
                page_resultsB = r
            prev_chose = None
            while (len(page_resultsB) == 0):
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(B, chosen, "pg3B switch to backup len0 ")
                page_resultsB = r
            if (page_resultsB[0] is None):
                r = run_ccie13(B, "pg3B switch to ccie13 len0 ")
                page_resultsB = r
            prev_chose = None
            while (page_resultsB[0] is None):
                if (prev_chose is None): chosen = random.choice(backups)
                else:
                    while (chosen == prev_chose):
                        chosen = random.choice(backups)
                prev_chose = chosen
                r = run_backup1(B, chosen, "pg3B switch to backup len0 ")
                page_resultsB = r
                
            log.write('b grabbed')
            log.write('\n')
            page_results = page_resultsA + page_resultsB
            log.write('done')
            log.write('\n')

            #for each ad store if within the hour
            c = 0
            last_dates = []
            for url in ad_links:
                if (c % 10 == 0) :
                    log.write("on ad ")
                    log.write(str(c))
                    log.write("\n")
                if (c == len(ad_links) - 1) :
                    log.write("on ad ")
                    log.write(str(c))
                    log.write("\n")
                if (c<len(ad_links) - 1):
                    more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,page_results[c+1],ad_links[c+1],g)
                    last_dates.append(date)
                else :
                    more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,None,None,g)
                    last_dates.append(date)
                if (more == True) : c = c + 1
                else : break

            cycle = len(page_results)-1
            while (True and cycle >= 0):
                last_date = last_dates[cycle]
                if (last_date is None): 
                    cycle = cycle - 1
                    continue
                else: break
            log.write('last date : ')    
            log.write(str(last_date))
            log.write('\n')

            #if more to go, then do with page 4
            #if ((now >= last_date) and (oneHourAgo <= last_date)):
            if (oneHourAgo <= last_date):
                #if nothing in the fourth page, first try ccie13
                if (results[i+3] is None):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=4"]
                    r = run_ccie13(link, "page 4 missing! try again with ccie13 ")
                    results[i+3] = r[0]
                #then try backup
                prev_chose = None
                while (results[i+3] is None):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=4"]
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(link, chosen, "page 4 missing! try again with ")
                    results[i+3] = r[0]

                soup = BeautifulSoup(results[i+3],'lxml')
                ad_links, service, tags = getLinks(soup)
                log.write('# tags ')
                log.write(str(len(tags)))
                log.write("\n")
                log.write('# services ')
                log.write(str(len(service)))
                log.write("\n")
                log.write('# ad links ')
                log.write(str(len(ad_links)))
                log.write("\n")
                
                #if ad_links is empty, first try ccie13
                if (len(ad_links) == 0):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=4"]
                    r = run_ccie13(link, "no ad links found page 4! try again with ccie13 ")
                    results[i+3] = r[0]
                    if results[i+3] is not None:
                        soup = BeautifulSoup(results[i+3],'lxml')
                        ad_links, service, tags = getLinks(soup)
                #then try backup
                prev_chose = None
                while (len(ad_links) == 0):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=4"]
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(link, chosen, "no ad links found page 4! try again with ")
                    results[i+3] = r[0]
                    if results[i+3] is not None:
                        soup = BeautifulSoup(results[i+3],'lxml')
                        ad_links, service, tags = getLinks(soup)
                    
                log.write('# tags ')
                log.write(str(len(tags)))
                log.write("\n")
                log.write('# services ')
                log.write(str(len(service)))
                log.write("\n")
                log.write('# ad links ')
                log.write(str(len(ad_links)))
                log.write("\n")

                #for each ad grab all the html
                log.write('grabbing all ads pg 4...')
                log.write("\n")
                A = ad_links[:len(ad_links)/2]
                log.write(str(A))
                log.write("\n")
                B = ad_links[len(ad_links)/2:]
                log.write(str(B))
                log.write("\n")
                page_resultsA = pool.map(parse, A)
                #if tried all of them and failed, first try ccie13
                #then try backup
                if (len(page_resultsA) == 0):
                    r = run_ccie13(A, "pg4A switch to ccie13 len0 ")
                    page_resultsA = r
                prev_chose = None
                while (len(page_resultsA) == 0):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(A, chosen, "pg4A switch to backup len0 ")
                    page_resultsA = r
                if (page_resultsA[0] is None):
                    r = run_ccie13(A, "pg4A switch to ccie13 len0 ")
                    page_resultsA = r
                prev_chose = None
                while (page_resultsA[0] is None):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(A, chosen, "pg4A switch to backup len0 ")
                    page_resultsA = r
                    
                log.write('a grabbed')
                log.write('\n')
                page_resultsB = pool.map(parse, B)
                #if tried all of them and failed, first try ccie13
                #then try backup
                if (len(page_resultsB) == 0):
                    r = run_ccie13(B, "pg4B switch to ccie13 len0 ")
                    page_resultsB = r
                prev_chose = None
                while (len(page_resultsB) == 0):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(B, chosen, "pg4B switch to backup len0 ")
                    page_resultsB = r
                if (page_resultsB[0] is None):
                    r = run_ccie13(B, "pg4B switch to ccie13 len0 ")
                    page_resultsB = r
                prev_chose = None
                while (page_resultsB[0] is None):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(B, chosen, "pg4B switch to backup len0 ")
                    page_resultsB = r
                    
                log.write('b grabbed')
                log.write('\n')
                page_results = page_resultsA + page_resultsB
                log.write('done')
                log.write('\n')

                #for each ad store if within the hour
                c = 0
                last_dates = []
                for url in ad_links:
                    if (c % 10 == 0) :
                        log.write("on ad ")
                        log.write(str(c))
                        log.write("\n")
                    if (c == len(ad_links) - 1) :
                        log.write("on ad ")
                        log.write(str(c))
                        log.write("\n")
                    if (c<len(ad_links) - 1):
                        more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,page_results[c+1],ad_links[c+1],g)
                        last_dates.append(date)
                    else :
                        more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,None,None,g)
                        last_dates.append(date)
                    if (more == True) : c = c + 1
                    else : break
                
            cycle = len(page_results)-1
            while (True and cycle >= 0):
                last_date = last_dates[cycle]
                if (last_date is None): 
                    cycle = cycle - 1
                    continue
                else: break
            log.write('last date : ')    
            log.write(str(last_date))
            log.write('\n')

            #if more to go, then do with page 5
            #if ((now >= last_date) and (oneHourAgo <= last_date)):
            if (oneHourAgo <= last_date):
                #if nothing in the fifth page, first try ccie13
                if (results[i+4] is None):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=5"]
                    r = run_ccie13(link, "page 5 missing! try again with ccie13 ")
                    results[i+4] = r[0]
                #then try backup
                prev_chose = None
                while (results[i+4] is None):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=5"]
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(link, chosen, "page 5 missing! try again with ")
                    results[i+4] = r[0]

                soup = BeautifulSoup(results[i+4],'lxml')
                ad_links, service, tags = getLinks(soup)
                log.write('# tags ')
                log.write(str(len(tags)))
                log.write("\n")
                log.write('# services ')
                log.write(str(len(service)))
                log.write("\n")
                log.write('# ad links ')
                log.write(str(len(ad_links)))
                log.write("\n")
                
                #if ad_links is empty, first try ccie13
                if (len(ad_links) == 0):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=5"]
                    r = run_ccie13(link, "no ad links found page 5! try again with ccie13 ")
                    results[i+4] = r[0]
                    if results[i+4] is not None:
                        soup = BeautifulSoup(results[i+4],'lxml')
                        ad_links, service, tags = getLinks(soup)
                #then try backup
                prev_chose = None
                while (len(ad_links) == 0):
                    link = ["http://"+loc+".backpage.com/adult/?layout=date&page=5"]
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(link, chosen, "no ad links found page 5! try again with ")
                    results[i+4] = r[0]
                    if results[i+4] is not None:
                        soup = BeautifulSoup(results[i+4],'lxml')
                        ad_links, service, tags = getLinks(soup)
                    
                log.write('# tags ')
                log.write(str(len(tags)))
                log.write("\n")
                log.write('# services ')
                log.write(str(len(service)))
                log.write("\n")
                log.write('# ad links ')
                log.write(str(len(ad_links)))
                log.write("\n")

                #for each ad grab all the html
                log.write('grabbing all ads pg 5...')
                log.write("\n")
                A = ad_links[:len(ad_links)/2]
                log.write(str(A))
                log.write("\n")
                B = ad_links[len(ad_links)/2:]
                log.write(str(B))
                log.write("\n")
                page_resultsA = pool.map(parse, A)
                #if tried all of them and failed, first try ccie13
                #then try backup
                if (len(page_resultsA) == 0):
                    r = run_ccie13(A, "pg5A switch to ccie13 len0 ")
                    page_resultsA = r
                prev_chose = None
                while (len(page_resultsA) == 0):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(A, chosen, "pg5A switch to backup len0 ")
                    page_resultsA = r
                if (page_resultsA[0] is None):
                    r = run_ccie13(A, "pg5A switch to ccie13 len0 ")
                    page_resultsA = r
                prev_chose = None
                while (page_resultsA[0] is None):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(A, chosen, "pg5A switch to backup len0 ")
                    page_resultsA = r
                    
                log.write('a grabbed')
                log.write('\n')
                page_resultsB = pool.map(parse, B)
                #if tried all of them and failed, first try ccie13
                #then try backup
                if (len(page_resultsB) == 0):
                    r = run_ccie13(B, "pg5B switch to ccie13 len0 ")
                    page_resultsB = r
                prev_chose = None
                while (len(page_resultsB) == 0):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(B, chosen, "pg5B switch to backup len0 ")
                    page_resultsB = r
                if (page_resultsB[0] is None):
                    r = run_ccie13(B, "pg5B switch to ccie13 len0 ")
                    page_resultsB = r
                prev_chose = None
                while (page_resultsB[0] is None):
                    if (prev_chose is None): chosen = random.choice(backups)
                    else:
                        while (chosen == prev_chose):
                            chosen = random.choice(backups)
                    prev_chose = chosen
                    r = run_backup1(B, chosen, "pg5B switch to backup len0 ")
                    page_resultsB = r
                    
                log.write('b grabbed')
                log.write('\n')
                page_results = page_resultsA + page_resultsB
                log.write('done')
                log.write('\n')
                #for each ad store if within the hour
                c = 0
                for url in ad_links:
                    if (c % 10 == 0) :
                        log.write("on ad ")
                        log.write(str(c))
                        log.write("\n")
                    if (c == len(ad_links) - 1) :
                        log.write("on ad ")
                        log.write(str(c))
                        log.write("\n")
                    if (c<len(ad_links) - 1):
                        more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,page_results[c+1],ad_links[c+1],g)
                    else :
                        more, date = storeAds(page_results[c],url,c,now,oneHourAgo,loc,ts_str,None,None,g)
                    if (more == True) : c = c + 1
                    else : break
    log.write('total ads in ')
    log.write(loc)
    log.write(' ')
    log.write(str(count_g))
    log.write('\n')
    g.close()
    log.close()
    i = i + 4
global log_master
log_master.write("total ads in ")
log_master.write(timezone)
log_master.write(": ")
log_master.write(str(count_g))
log_master.write("\n")
elapsed_time = timer() - start
log_master.write("time to run : ")
log_master.write(str(elapsed_time))
log_master.write(" seconds")
log_master.write("\n")
log_master.close()
