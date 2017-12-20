# anti-trafficking-tools

backpage_public_code.ipynb - this is the code to match a Backpage ad with potential Bitcoin transactions. see the code for more details.


RunItAll.java, Timestamp.java, AllForAd.java - this is the code to recreate the price of a Backpage ad.


features.py, model.py, values.py - this is the code to take two ads and output whether they were written by the same author.
(1) The code assumes that you have some file that contains a list of names, "names_uniq.tsv"
(2) This code assumes that you have the stanford NLP jars/toolkit in the folder 'src/'. The exact files it needs are:

models/english-left3words-distsim.tagger
lib/stanford-postagger-3.4.1.jar
lib/stanford-postagger-3.4.1.jar

(3) This is a supervised learning algorithm, which means that it requires training data. If you look at the main method in model.py, it shows an example of running the logistic regression model assuming you already built the features for dataset X1, X2 and X3 (where each is split into the features extracted from the body of the ad and the title of the ad). It trains and tests on all combinations of those three files. It prints out the classification accuracy, FPR, and TPR.

(4) The features.py file actually extracts the features. The values.py file extracts the values necessary to build the features (e.g., values.py gets the n-grams, and features.py calculates the jaccard similarity between two sets of n-grams in two ads).

scrapeAds_everyHour_final.py, scrapeSponsor.py,ssh_backup1.py, ssh_ccie13.py - this is the code to scrape Backpage ads once every hour.
    
    scrapeAds_everyHour_final.py : this is the master code. it runs from the biggest ec2 instance, and assumes that there is a hard drive connected called “scrape-data”. If the master code fails to scrape a page of ads successfully, it tries to run the scrape on a backup. It first tries using cci13, then randomly picks from the backup1 ec2 instances. it also assumes there are multiple tunnel proxies open and available for use.

    ssh_backup1.py: Search on “backups = [“ to find all the ec2 instances that are associated with this backup code in scrapeAds_everyHour_final.py. You should store a copy of ssh_backup1.py in each of those ec2 instances. This is a backup that runs the scraper from a different IP address, and automatically transfers whatever data it got back into the main ec2 instance so it can be processed by scrapeAds_everyHour_final.py.

    ssh_ccie13.py: Only associated with one ec2 instance. You should store a copy of ssh_ccie13.py in that instance. It is the first go-to backup that runs the scraper from a different IP address, and automatically transfers whatever data it got back into the main ec2 instance so it can be processed by scrapeAds_everyHour_final.py

    scrapeSponsor.py: this scrapes the first page of every main listings page in the US, in order to grab all sponsor ads. I ran it locally. 

    Pipeline:
    1) open the tunnels
    2) set up cron job to run scrapeAds_everyHour_final.py once every hour for every location in the US
    e.g.
    0 * * * * python scrapeAds_everyHour_final.py la PST
    will run la every hour, on the 0th minute
    N.B. Make sure to stagger locations! if you run everything on the 0th minute, it will explode.

    e.g.
    0 * * * * python scrapeAds_everyHour_final.py la PST
    2 * * * * python scrapeAds_everyHour_final.py ohio EST
    etc.

    See bottom of the file for all correct timezones.
    3) set up cron job to run scrapeSponsor.py at least once a day

    TIMEZONES
    locs_PST.append("la")
    locs_PST.append("sanjoaquinvalley")
    locs_PST.append("upstateca")
    locs_PST.append("imperial")
    locs_PST.append("sfbay")
    locs_PST.append("sacramento")
    locs_PST.append("sandiego")
    locs_PST.append("centralcoast")
    locs_PST.append("washington")
    locs_PST.append("oregon")
    locs_PST.append("nevada")

    locs_EST.append("ohio")
    locs_EST.append("maine")
    locs_EST.append("maryland")
    locs_EST.append("massachusetts")
    locs_EST.append("pennsylvania")
    locs_EST.append("michigan")
    locs_EST.append("rhodeisland")
    locs_EST.append("southcarolina")
    locs_EST.append("connecticut")
    locs_EST.append("delaware")
    locs_EST.append("dc")
    locs_EST.append("newhampshire")
    locs_EST.append("georgia")
    locs_EST.append("newjersey")
    locs_EST.append("burlington")
    locs_EST.append("virginia")
    locs_EST.append("newyork")
    locs_EST.append("indiana")
    locs_EST.append("northcarolina")
    locs_EST.append("westvirginia")
    locs_EST.append("daytona")
    locs_EST.append("southflorida")
    locs_EST.append("southwestflorida")
    locs_EST.append("northflorida")
    locs_EST.append("northwestflorida")

    locs_CST.append("alabama")
    locs_CST.append("kansas")
    locs_CST.append("kentucky")
    locs_CST.append("louisiana")
    locs_CST.append("oklahoma")
    locs_CST.append("arkansas")
    locs_CST.append("minnesota")
    locs_CST.append("southdakota")
    locs_CST.append("tennessee")
    locs_CST.append("mississippi")
    locs_CST.append("missouri")
    locs_CST.append("nebraska")
    locs_CST.append("illinois")
    locs_CST.append("wisconsin")
    locs_CST.append("northdakota")
    locs_CST.append("iowa")
    locs_CST.append("centraltexas")
    locs_CST.append("southeasttexas")
    locs_CST.append("southtexas")
    locs_CST.append("northeasttexas")

    locs_MST.append("arizona")
    locs_MST.append("colorado")
    locs_MST.append("montana")
    locs_MST.append("utah")
    locs_MST.append("newmexico")
    locs_MST.append("idaho")
    locs_MST.append("wyoming")
    locs_MST.append("westtexas")

    locs_AST.append(“alaska”)

    locs_HST.append(“hawaii”)
    
scrapePriceInfo5_all.java, scrapePriceInfo5_escort.java, scrapeLA.java -  this is the code to scrape the pricing information needed to recreate the price of a Backpage ad

    scrapePriceInfo5_all.java : this will scrape all the pricing info across all regions in the US for all adult entertainment sections

    scrapePriceInfo5_escort.java : this will scrape all the pricing info across all regions in the US for the escort section

    scrapeLA.java : this will scrape all the pricing info in LA for all adult entertainment sections

    regions_$us_edit.txt : list of all the regions in the US

    _all.java should be run at least once a week
    _escort.java should be run at least once a day
    LA.java should be run at least once every 15 minutes (i.e., continuously)

