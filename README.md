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
