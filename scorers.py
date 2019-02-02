from collections import Counter
from math import log10

class ngram_score(object):
    def __init__(self,ngramfile,sep=' '):
        ''' load a file containing ngrams and counts, calculate log probabilities '''
        self.ngrams = {}
        with open(ngramfile) as file:
            for line in file:
                key,count = line.split(sep) 
                self.ngrams[key] = int(count)
                #print (key,count)

        self.L = len(key)
        self.N = sum(self.ngrams.values())
        #calculate log probabilities
        for key in self.ngrams.keys():
            self.ngrams[key] = log10(float(self.ngrams[key])/self.N)
        self.floor = log10(0.01/self.N)

    def score(self,text):
        ''' compute the score of text (n-gram) '''
        score = 0
        ngrams = self.ngrams.__getitem__
        for i in range(len(text)-self.L+1):
            if text[i:i+self.L] in self.ngrams: score += ngrams(text[i:i+self.L])
            else: score += self.floor
        return score

    def icscore(self,text):
        ''' compute the score of text (Index of Coincidence) '''
        icscore=0

        temp=Counter(text)
        
        for key,value in temp.items():
            icscore+=value*(value-1)
  
        icscore=icscore/((len(text))*(len(text)-1))

        return icscore
