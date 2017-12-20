# -*- coding: utf-8 -*-
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize.stanford import StanfordTokenizer
import re
import pandas
import numpy
import itertools
from values import Values
import math
from sklearn import linear_model
import os

#initializes with two value vectors (one from each ad). call extract_features to get the full feature set
class Features(object):
    
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
    
    def jaccard(self, x, y):
        if len(x) == 0 or len(y) == 0 : return 0.0
        unionXY = list(set(x) | set(y))
        intersectionXY = list(set(x) & set(y))
        return len(intersectionXY) / float(len(unionXY)) 
    
    def cs(self,first,second):
        if len(first) < len(second) :
            for i in range (len(first), len(second)):
                first.append(0.0)
                
        elif len(second) < len(first):  
            for i in range (len(second), len(first)):
                second.append(0.0)
        #print first
        #print second
        
        normA = sum([i*i for i in first])
        normB = sum([i*i for i in second])
        if (normA == 0) or (normB == 0) : return 0.0
        else: return sum([i*j for i,j in zip(first, second)])/(math.sqrt(normA)* math.sqrt(normB))
    
    def cosine_similarity(self,x,y):
        if x[0] != -1.0 and y[0] != -1.0:
            first = sorted(x, reverse=True)
            second = sorted(y, reverse=True)
            f1 = math.fabs(len(x)-len(y));
            #print first
            #print second
            f2 = self.cs(first,second);
        
        elif (x[0]==-1.0 and y[0] == -1.0):
            f1 = 0.0
            f2 = 0.0

        elif (x[0]==-1.0 and y[0] != -1.0):
            f1 = len(y)
            f2 = 0.0

        elif (x[0]!=-1.0 and y[0] == -1.0):
            f1 = len(x)
            f2 = 0.0
        return f1, f2
    
    def extract_feats(self,isTitle):
        v1 = self.v1
        v2 = self.v2
                
        feat_breaklines = self.cosine_similarity(v1.getVals()[0], v2.getVals()[0])
        f1 = feat_breaklines[0]
        f2 = feat_breaklines[1]
        
        f3 = self.jaccard(v1.getVals()[1], v2.getVals()[1])
        f4 = self.jaccard(v1.getVals()[2], v2.getVals()[2])
        
        f5 = self.jaccard(v1.getVals()[3], v2.getVals()[3])
        
        f6 = self.jaccard(v1.getVals()[4], v2.getVals()[4])
        
        pos1 = v1.getVals()[5]
        pos2 = v2.getVals()[5]
        f7 = self.jaccard([i[0] for i in pos1 if i[1] == 'NNP'], [i[0] for i in pos2 if i[1] == 'NNP'])
        f8 = self.jaccard([i[0] for i in pos1 if i[1] == 'JJ'], [i[0] for i in pos2 if i[1] == 'JJ'])
        f9 = self.jaccard([i[0] for i in pos1 if i[1] == 'RB'], [i[0] for i in pos2 if i[1] == 'RB'])
        f10 = self.jaccard([i[0] for i in pos1 if i[1] == 'IN'], [i[0] for i in pos2 if i[1] == 'IN'])
        f11 = self.jaccard([i[0] for i in pos1 if i[1] == 'SYM'], [i[0] for i in pos2 if i[1] == 'SYM'])
        f12 = self.jaccard([i[0] for i in pos1 if i[1] == ':'], [i[0] for i in pos2 if i[1] == ':'])
        
        f13 = self.jaccard(v1.getVals()[6], v2.getVals()[6])
        f14 = self.jaccard(v1.getVals()[7], v2.getVals()[7])
        f15 = self.jaccard(v1.getVals()[8], v2.getVals()[8])        
        
        #print '{0', f1, ',1', f2, ',2', f3,',3', f4,',4', f5,',5', f6,',6', f7,',7', f8,',8', f9,',9', f10, ',10', f11,',11', f12,',12', f13,',13', f14,',14', f15, ',15 same}'
        if (isTitle == True) : return [f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15]
        else: return [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15]
        
        return
    
    #FOR DEBUGGING AND TESTING ONLY
    def extract_features(self,isTitle):
        v1 = self.v1
        v2 = self.v2
        
        feat_breaklines = self.cosine_similarity(v1.extract_breaklines(), v2.extract_breaklines())
        f1 = feat_breaklines[0]
        f2 = feat_breaklines[1]
        
        f3 = self.jaccard(v1.extract_wordgrams(1), v2.extract_wordgrams(1))
        f4 = self.jaccard(v1.extract_wordgrams(2), v2.extract_wordgrams(2))
        
        f5 = self.jaccard(v1.extract_websites(), v2.extract_websites())
        
        f6 = self.jaccard(v1.extract_names(), v2.extract_names())
        
        pos1 = v1.extract_POS()
        pos2 = v2.extract_POS()
        f7 = self.jaccard([i[0] for i in pos1 if i[1] == 'NNP'], [i[0] for i in pos2 if i[1] == 'NNP'])
        f8 = self.jaccard([i[0] for i in pos1 if i[1] == 'JJ'], [i[0] for i in pos2 if i[1] == 'JJ'])
        f9 = self.jaccard([i[0] for i in pos1 if i[1] == 'RB'], [i[0] for i in pos2 if i[1] == 'RB'])
        f10 = self.jaccard([i[0] for i in pos1 if i[1] == 'IN'], [i[0] for i in pos2 if i[1] == 'IN'])
        f11 = self.jaccard([i[0] for i in pos1 if i[1] == 'SYM'], [i[0] for i in pos2 if i[1] == 'SYM'])
        f12 = self.jaccard([i[0] for i in pos1 if i[1] == ':'], [i[0] for i in pos2 if i[1] == ':'])
        
        f13 = self.jaccard(v1.extract_chargrams(1), v2.extract_chargrams(1))
        f14 = self.jaccard(v1.extract_chargrams(2), v2.extract_chargrams(2))
        f15 = self.jaccard(v1.extract_chargrams(3), v2.extract_chargrams(3))        
        
        #print '{0', f1, ',1', f2, ',2', f3,',3', f4,',4', f5,',5', f6,',6', f7,',7', f8,',8', f9,',9', f10, ',10', f11,',11', f12,',12', f13,',13', f14,',14', f15, ',15 same}'
        if (isTitle == True) : return [f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15]
        else: return [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15]
        #print f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15
        #return [f3,f4,f7,f8,f9,f10,f11,f12,f13,f14,f15]
    
    #FOR DEBUGGING AND TESTING ONLY
    def extract_features2(self,k,l):
        v1 = self.v1
        v2 = self.v2
        
        feat_breaklines = self.cosine_similarity(k[0], l[0])
        f1 = feat_breaklines[0]
        f2 = feat_breaklines[1]
        
        f3 = self.jaccard(k[1], l[1])
        f4 = self.jaccard(k[2], l[2])
        
        f5 = self.jaccard(k[3], l[3])
        
        f6 = self.jaccard(k[4], l[4])
        
        f7 = self.jaccard([i[0] for i in k[5] if i[1] == 'NNP'], [i[0] for i in l[5] if i[1] == 'NNP'])
        f8 = self.jaccard([i[0] for i in k[5] if i[1] == 'JJ'], [i[0] for i in l[5] if i[1] == 'JJ'])
        f9 = self.jaccard([i[0] for i in k[5] if i[1] == 'RB'], [i[0] for i in l[5] if i[1] == 'RB'])
        f10 = self.jaccard([i[0] for i in k[5] if i[1] == 'IN'], [i[0] for i in l[5] if i[1] == 'IN'])
        f11 = self.jaccard([i[0] for i in k[5] if i[1] == 'SYM'], [i[0] for i in l[5] if i[1] == 'SYM'])
        f12 = self.jaccard([i[0] for i in k[5] if i[1] == ':'], [i[0] for i in l[5] if i[1] == ':'])
        
        f13 = self.jaccard(k[6], l[6])
        f14 = self.jaccard(k[7], l[7])
        f15 = self.jaccard(k[8], l[8])        
        
        #print '{0', f1, ',1', f2, ',2', f3,',3', f4,',4', f5,',5', f6,',6', f7,',7', f8,',8', f9,',9', f10, ',10', f11,',11', f12,',12', f13,',13', f14,',14', f15, ',15 same}'
        return [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15]

if __name__ == '__main__':
    
    path = 'src/'
    all_names = []
    name_file = open('names_uniq.tsv', 'r')
    for line in name_file: all_names.append(line.split("\t")[0].lower().rstrip())
    
    ad_data = """Visiting today and tomorrow until 2p.m.<br>
<b></b><b></b><br>
Are you looking for a great time? Iâ€™m the woman youâ€™ve FANTASIZED about but didnâ€™t know where to find her. I will rock your socks off and have you leaving with a smile! <br>
I am available 24/7 at my private and discreet incall location in S.F (in the Civic Center area). <br>
My photos are 100% real. <br>
<br>
~200/half hr, ~300/hr <br>
<br>
Incall only! <br>
Serious & Discreet clients only <br>
No blocked calls! <br>
<br>
<a target="_blank" href="mailto:"></a> <br>
*82  <br>
<br>
XOXO, Tessa"""

    ad_data2 = """<b></b><i>My name is Dream & I am an exotic  Armenian, German<br> woman, standing 5'7, 150lbs, all natural busty 36c-28-38,<br> with light blonde hair & blue eyes.<br>
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
<br></i>
"""
    
    v1 = Values(ad_data, path, all_names)
    v2 = Values(ad_data2, path, all_names)
    f = Features(v1, v2)
    print f.extract_feats(False)
    

