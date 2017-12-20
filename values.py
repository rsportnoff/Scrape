# -*- coding: utf-8 -*-
import nltk
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize.stanford import StanfordTokenizer
import re
import numpy
import itertools
from string import punctuation

#initializes with ad text, path to POS jars, and list of all names. call extract_* to get the values
class Values(object):
    
    def __init__(self, data, path, all_names):
        self.data = data
        self.path = path
        self.english_postagger = StanfordPOSTagger(path+'models/english-left3words-distsim.tagger', path+'lib/stanford-postagger-3.4.1.jar', java_options='-Xmx2g')
        self.english_tokenizer = StanfordTokenizer(path+'lib/stanford-postagger-3.4.1.jar', 'utf-8')
        self.all_names = all_names
        self.pos = self.extract_POS() 
        self.nms = self.extract_names()
        self.wg1 = self.extract_wordgrams(1)
        self.wg2 = self.extract_wordgrams(2)
        self.cg1 = self.extract_chargrams(1)
        self.cg2 = self.extract_chargrams(2)
        self.cg3 = self.extract_chargrams(3)
        self.bl = self.extract_breaklines()
        self.ws = self.extract_websites()
    
    def getVals(self):
        return self.bl, self.wg1, self.wg2, self.ws, self.nms, self.pos, self.cg1, self.cg2, self.cg3
        
    def extract_POS(self):
        return self.english_postagger.tag(self.english_tokenizer.tokenize(self.data))
    
    def extract_websites(self):
        websites = []
        result = re.findall('href=\"(.*?)\"', self.data)
        for r in result:
            if (r == 'mailto:') or (r == 'http:///') : continue
            else : websites.append(r)
        return websites
    
    def extract_breaklines(self):
        breaklines = []
        idx_old = 0;
        idx_new = self.data.find('<br>');
        breaklines.append(idx_new - idx_old);
        idx_old = idx_new;
        while idx_old < len(self.data) :
            idx_new = self.data.find('<br>', idx_old+4);
            if (idx_new == -1) : break
            breaklines.append(idx_new - idx_old);
            idx_old = idx_new;
        return breaklines
    
    def extract_chargrams(self,gram_size):
        return [''.join(self.data[i:i+gram_size]) for i in range(len(self.data)-gram_size+1)]
    
    def extract_wordgrams(self, gram_size):
        r = re.compile(r'[\s{}\t\n\r\+\>\<\=\¢\â\$]+'.format(re.escape(punctuation)))
        word_list = r.split(self.data)
        #word_list = re.split('\W+', self.data)
        #word_list = re.split(r'[\p{P} \\t\\n\\r\\+\\>\\<\\=\\¢\\â\\$]+', self.data)
        word_list = filter(None, word_list)
        return [''.join(word_list[i:i+gram_size]) for i in range(len(word_list)-gram_size+1)]
    
    def extract_names(self):
        r = re.compile(r'[\s{}\t\n\r\+\>\<\=\¢\â\$]+'.format(re.escape(punctuation)))
        word_list = r.split(self.data)
        #word_list = re.split('\W+', self.data)
        #word_list = re.split('[\p{P} \\t\\n\\r\\+\\>\\<\\=\\¢\\â\\$]+', self.data)
        word_list = filter(None, word_list)
        word_list = [x.lower() for x in word_list]
        return list(set(word_list) & set(self.all_names))
 
if __name__ == '__main__':

    ad_data = """<b></b><i>My name is Dream & I am an exotic  Armenian, German<br> woman, standing 5'7, 150lbs, all natural busty 36c-28-38,<br> with light blonde hair & blue eyes.<br>
<br>
I offer incall or outcall & I am available 24hrs a day so feel free to<br>
contact me at anytime!<br>
<br> 
<br>
If for some reason I dont answer, please leave a message.<br>
No blocked calls will be answered!<br>
No text messages either boys!<br>
<br>
<u><b>Ready for pleasure<br></b></u>
<br>
CALL ME!!!<br>
<br></i>"""
    path_to_jars = '/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/groundTruth/FindMatchings/src/'
    all_names = []
    name_file = open('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/BackupFiles/names_uniq.tsv', 'r')
    for line in name_file: all_names.append(line.split("\t")[0].lower().rstrip())
    
    v = Values(ad_data, path_to_jars, all_names)
    print v.getVals()
    #for a,b in v.extract_POS():
    #    print a, b
    '''
    print v.extract_POS() 
    print v.extract_names()
    print v.extract_wordgrams(1) #-> jaccard
    print v.extract_chargrams(3) #-> jaccard
    print v.extract_breaklines()
    print v.extract_websites()
    '''
