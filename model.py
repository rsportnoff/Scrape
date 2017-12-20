from sklearn import linear_model
import numpy
from features import Features
from values import Values
from io import StringIO
from sklearn.metrics import classification_report
from sklearn import svm
from string import digits

class Model(object):
    
    def __init__(self, C, path):
        self.C = C
        self.path = path
        self.lr = linear_model.LogisticRegression(C=self.C,class_weight={0:1,1:1})
        self.all_names = []
        name_file = open('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/names_uniq.tsv', 'r')
        for line in name_file: self.all_names.append(line.split("\t")[0].lower().rstrip())
        
    def train(self, X, y):
        self.lr.fit(X, y)
        return self.lr

if __name__ == '__main__':
    
    path_to_jars = '/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/groundTruth/FindMatchings/src/'
    
    #initialize the model
    lm = Model(1.0, path_to_jars)
    
    #REBECCA'S ORIGINAL MODEL
    X1 = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_1small.txt')
    X1_titles = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_1_titleFeatssmall.txt')
    X1 = numpy.concatenate((X1, X1_titles), axis = 1)

    y = numpy.empty([7500])
    for i in range(0, 7500):
        if (i <= 4999) : y[i] = 0
        else : y[i] = 1
        
    X2 = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_2small.txt')
    X2_titles = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_2_titleFeatssmall.txt')
    X2 = numpy.concatenate((X2, X2_titles), axis = 1)
    
    X3 = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_3small.txt')
    X3_titles = numpy.loadtxt('/Users/cusgadmin/BackPageStylometry/data-drop-1/extractions/ARFF/go_3_titleFeatssmall.txt')
    X3 = numpy.concatenate((X3, X3_titles), axis = 1)
    
    lr = linear_model.LogisticRegression(penalty = 'l2', dual = False, tol=0.0001, C=10, 
                                         fit_intercept = True, class_weight= {0:1,1:1})
    
    print 'training model...'
    lr.fit(X1, y)
    print 'done'
    
    print 'testing model...'
    y_pred = lr.predict(X2)
    print 'done'

    print "Train 1, Test 2"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc1 = (TP+TN)/float(len(y_pred))
    print acc1
    #print classification_report(y, y_pred)
    fpr1 = FP/float((FP + TN))
    print fpr1
    tpr1 = TP/float((TP + FN))
    print tpr1
    
    print
    print "Train1, Test 3"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    y_pred = lr.predict(X3)
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc2 = (TP+TN)/float(len(y_pred))
    print acc2
    #print classification_report(y, y_pred)
    fpr2 = FP/float((FP + TN))
    print fpr2
    tpr2 = TP/float((TP + FN))
    print tpr2
    
    print
    print "Train2, Test 1"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    lr.fit(X2, y)
    y_pred = lr.predict(X1)
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc3 = (TP+TN)/float(len(y_pred))
    print acc3
    #print classification_report(y, y_pred)
    fpr3 = FP/float((FP + TN))
    print fpr3
    tpr3 = TP/float((TP + FN))
    print tpr3
    
    print
    print "Train2, Test 3"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    y_pred = lr.predict(X3)
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc4 = (TP+TN)/float(len(y_pred))
    print acc4
    #print classification_report(y, y_pred)
    fpr4 = FP/float((FP + TN))
    print fpr4
    tpr4 = TP/float((TP + FN))
    print tpr4
    
    print
    print "Train3, Test 1"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    lr.fit(X3, y)
    y_pred = lr.predict(X1)
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc5 = (TP+TN)/float(len(y_pred))
    print acc5
    #print classification_report(y, y_pred)
    fpr5 = FP/float((FP + TN))
    print fpr5
    tpr5 = TP/float((TP + FN))
    print tpr5
    
    print
    print "Train3, Test 2"
    FP = 0
    TP = 0
    FN = 0
    TN = 0
    y_pred = lr.predict(X2)
    for i in range(0, len(y_pred)):
        if y_pred[i] == y[i]: 
            if y[i] == 1: TP = TP + 1
            if y[i] == 0: TN = TN + 1
        elif y_pred[i] == 1 and y[i] == 0: FP = FP + 1
        elif y_pred[i] == 0 and y[i] == 1: FN = FN + 1
    acc6 = (TP+TN)/float(len(y_pred))
    print acc6
    #print classification_report(y, y_pred)
    fpr6 = FP/float((FP + TN))
    print fpr6
    tpr6 = TP/float((TP + FN))
    print tpr6
    
    print
    print (acc1+acc2+acc3+acc4+acc5+acc6)/6
    print (fpr1+fpr2+fpr3+fpr4+fpr5+fpr6)/6
    print (tpr1+tpr2+tpr3+tpr4+tpr5+tpr6)/6
    
    
    
