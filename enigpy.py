import itertools
import multiprocessing
from datetime import datetime
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
        ''' compute the score of text '''
        score = 0
        ngrams = self.ngrams.__getitem__
        for i in range(len(text)-self.L+1):
            if text[i:i+self.L] in self.ngrams: score += ngrams(text[i:i+self.L])
            else: score += self.floor
        return score

class enigma():
    mapping = {}
    
    def __init__(self,rotor1,rotor2,rotor3,reflectori,plugboardi):
        self.rotor1=rotor1
        self.rotor2=rotor2
        self.rotor3=rotor3
        self.reflector=reflectori
        self.plugboard=plugboardi
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pomi=0
        for letter in pomlist:
            self.mapping.update({letter:pomi})
            pomi+=1
            
    def EDcrypt(self, text):
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        r1pos=self.rotor1.grund
        r2pos=self.rotor2.grund
        r3pos=self.rotor3.grund
        scrambled=""

        
        for letter in text:
            onecipher=""
            enc=0
            r3pos+=1
            
            
            if ((self.rotor2.step==12 and r2pos==12)
                and
                (self.rotor2.number=="VI"
                or self.rotor2.number=="VII"
                or self.rotor2.number=="VIII")):
                
                self.rotor2.step=25
            
            if (r3pos==self.rotor3.step) or (r2pos+1==self.rotor2.step): # or (double stepping of middle rotor)
                r2pos+=1
                #print("stepping middle")
                #print(r2pos)
                #print(r3pos)
                if r2pos==self.rotor2.step:
                    #print("stepping slow")
                    r1pos+=1

            if ((self.rotor3.step==12 and r3pos==12) and 
                (self.rotor3.number=="VI" 
                 or self.rotor3.number=="VII" 
                 or self.rotor3.number=="VIII")):
                self.rotor3.step=25
            
            if r3pos>25:
                r3pos=0
            
            if r2pos>25:
                r2pos=0
                
            if r1pos>25:
                r1pos=0

            onecipher=letter
            #print ("KEYP %s" % onecipher)
            
            #stecker
            if onecipher in self.plugboard.pairs:
                onecipher=self.plugboard.pairs.get(onecipher)
            
            onecipher=self.rotor3.wiring[((pomlist.index(onecipher)+r3pos)%26)]
            onecipher=pomlist[pomlist.index(onecipher)] #out - rotor3.ring  offset ringstellung
            onecipher=self.rotor2.wiring[((self.mapping.get(onecipher)-r3pos+r2pos)%26)]
            onecipher=self.rotor1.wiring[((self.mapping.get(onecipher)-r2pos+r1pos)%26)]
            onecipher=self.reflector.setting[((self.mapping.get(onecipher)-r1pos)%26)]
            onecipher=pomlist[((pomlist.index(onecipher)+r1pos)%26)]
            onecipher=pomlist[((self.rotor1.wiring.index(onecipher))%26)]
            onecipher=pomlist[((pomlist.index(onecipher)+r2pos-r1pos)%26)]
            onecipher=pomlist[((self.rotor2.wiring.index(onecipher))%26)]             
            onecipher=pomlist[((pomlist.index(onecipher)+r3pos-r2pos)%26)]
            onecipher=pomlist[pomlist.index(onecipher)] 
            onecipher=pomlist[self.rotor3.wiring.index(onecipher)]
            onecipher=pomlist[((pomlist.index(onecipher)-r3pos)%26)]

            if onecipher in self.plugboard.pairs:
                onecipher=self.plugboard.pairs.get(onecipher)
            #print ("STOU %s" % onecipher)
            
            #print ("DISP %s" %onecipher)
            #print ("\n")
            scrambled+=onecipher
        return scrambled

class rotor():
    options = {
                     #ABCDEFGHIJKLMNOPQRSTUVWXYZ
            "I"    : "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
            "II"   : "AJDKSIRUXBLHWTMCQGZNPYFVOE",
            "III"  : "BDFHJLCPRTXVZNYEIWGAKMUSQO",
            "IV"   : "ESOVPZJAYQUIRHXLNFTGKDCMWB",
            "V"    : "VZBRGITYUPSDNHLXAWMJQOFECK",
            "VI"   : "JPGVOUMFYQBENHZRDKASXLICTW",
            "VII"  : "NZJHGRCXMYSWBOUFAIVLPEKQDT",
            "VIII" : "FKQHTLXOCBJSPDZRAMEWNIUYGV"
            }
    
    stepoptions = {
                     #12345678901234567890123456
                     #ABCDEFGHIJKLMNOPQRSTUVWXYZ
            "I"    : 17, #Q
            "II"   : 5, #E
            "III"  : 22, #V
            "IV"   : 10, #J
            "V"    : 26, #Z
            "VI"   : 13, #Z+M 12+25
            "VII"  : 13, #Z+M 12+25
            "VIII" : 13  #Z+M 12+25
            }

    def __init__(self,walzen,ringstellung,grundstellung):
        self.number=walzen
        self.ring=ringstellung
        self.grund=grundstellung 
        self.step=self.stepoptions.get(walzen,"")
        self.wiring=self.options.get(walzen,"")
        self.wiring=self.setWiring()
        
    def setWiring(self):
        if (self.ring>0):
            pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            pom=""
            index=0
            #put wires in the right spot
            pom+=self.wiring[-self.ring:]
            pom+=self.wiring[:26-self.ring]
            self.wiring=pom
            pom=""
            #adjust the letter + self.ring
            for letter in self.wiring:         
                
                pom+=pomlist[(pomlist.index(letter)+self.ring)%26]

                index+=1
                
            #print ("new wiring %s" % pom)
        else:
            pom=self.wiring
            #print ("old wiring %s" % pom)
        return pom
        
class reflector():
    options = {
                  #ABCDEFGHIJKLMNOPQRSTUVWXYZ
            "B" : "YRUHQSLDPXNGOKMIEBFZCWVJAT",
            "Bt": "ENKQAUYWJICOPBLMDXZVFTHRGS",
            "C" : "FVPJIAOYEDRZXWGCTKUQSBNMHL",
            "Ct": "RDOBJNTKVEHMLFCWZAXGYIPSUQ"
            }

    def __init__(self,umkehrwalze):
        self.typ=umkehrwalze
        self.setting=self.options.get(umkehrwalze,"")
        
class plugboard():
    
    pairs = {}

    def __init__(self,steckerbrett):
        self.pairs=self.setWiring(steckerbrett)
    
    def setWiring(self,steckerbrett):
        pom={}
        for key,value in steckerbrett.items():
            pom[key]=value
            pom[value]=key
        return pom