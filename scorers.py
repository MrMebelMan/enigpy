from collections import Counter
from math import log10

class ngram_score(object):

    ngrams = {}
    L=0
    floor=0
    # careful you dumbass! it won't work with multiple files!

    def __init__(self,ngramfile,sep=' '):
        ''' load a file containing ngrams and counts, calculate log probabilities and keep them in memory '''
        if not ngram_score.ngrams:
            with open(ngramfile) as file:
                for line in file:
                    key,count = line.split(sep) 
                    ngram_score.ngrams[key] = int(count)

            ngram_score.L = len(key)
            self.N = sum(ngram_score.ngrams.values())

            #calculate log probabilities
            for key in ngram_score.ngrams.keys():
                ngram_score.ngrams[key] = log10(float(ngram_score.ngrams[key])/self.N)
            ngram_score.floor = log10(0.01/self.N)

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
