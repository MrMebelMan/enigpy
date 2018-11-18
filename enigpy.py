import collections
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

    def icscorer(self,text):
        icscore=0

        temp=collections.Counter(text)
        
        for key,value in temp.items():
            icscore+=value*(value-1)
  
        icscore=icscore/((len(text))*(len(text)-1))

        return icscore

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
            #print ("\n encrypting "+letter)
            stepagain1=False # 2 notches on VI VII VIII --- moving slowest rotor
            stepagain2=False # 2 notches on VI VII VIII --- moving middle rotor
            
            doublestepagain2=False # magic

            if (self.rotor3.step==13 and r3pos==26): 
                stepagain2=True

            if (self.rotor2.step==13 and r2pos+1==26): 
                stepagain1=True 
            
            if (r3pos==self.rotor3.step or stepagain2==True) or (r2pos+1==self.rotor2.step) or stepagain1==True: # or (double stepping of middle rotor)
                r2pos+=1
                #print ("stepagain1"+str(stepagain1))
                #print ("stepagain2"+str(stepagain2))
                #print ("doublestepagain2"+str(doublestepagain2))
                #print (self.rotor2.step)
                #print("stepping middle")
                #print(r2pos)
                #print(r3pos)

                if (self.rotor2.step==13 and r2pos==26):
                  stepagain1=True

                if (r2pos==self.rotor2.step or stepagain1==True):
                    #print("stepping slow")
                    r1pos+=1
                    stepagain1=False
         
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
            "VI"   : 13, #Z+M 13+26
            "VII"  : 13, #Z+M 13+26
            "VIII" : 13  #Z+M 13+26
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

class cracker():
    
    def __init__(self,textToCrack,scorer):
        self.ttc=textToCrack
        self.scorer=scorer
    
    def fanal(self):
        list={}
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in pomlist:
            list.update({letter:0})
        for letter in self.text:
            list[letter] += 1
            
        return list
        
    def test(self):
        print ("test2")
        plugboardi=plugboard({})
        reflectori=reflector("C")
        rotor1=rotor("I",0,25)  #slowest, left-most
        rotor2=rotor("IV",21,0)  #middle
        rotor3=rotor("VI",15,3)  #fastest, right-most
        enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
        text=enigmai.EDcrypt(self.ttc)
        print (text)

    def steckerHillClimbTest(self,rotor1,rotor2,rotor3,reflectori,score,plugs1,plugs2,plugs3):
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        plugboardi=plugboard({})

        #we'll try to hill-climb just the most used pairs
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        mostusedletters = ["E","N","X","R","S"]

        topscore=score

        #we'll use most used letters for step 1

        for i in mostusedletters:
            
            enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardtest)    
            text=enigmai.EDcrypt(self.ttc)
            myscore=self.scorer.icscorer(text)

            if (myscore>topscore):
                topscore=myscore
                best=[sub[0],sub[1]]
                print ("LTR_IN:"+sub[0]+sub[1])


        return topscore,"aaa"

    '''
    def steckerHillClimbTest(self,rotor1,rotor2,rotor3,reflectori,score,plugs1,plugs2,plugs3):
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        plugboardi=plugboard({})

        '''
        '''
        for subset in itertools.combinations("A","B","C","D","E","F","G","H","I",
        "J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", 2):
        '''
        
        '''letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]'''
        '''
        #we'll try to hill-climb just the most used pairs
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        mostusedletters = ["E","N","X","R","S"]

        #list(itertools.product(mostusedletters, letters))
        #letters.remove("")
        steckerinfo=[]
        lettersToRemove=[]
        topscore=score
        #allcombs = itertools.combinations(letters, 2)
        for i in range(plugs1):
            lettersToRemove[:] = []
            plugboardtestpairs = {}
            #for sub in (itertools.combinations(letters, 2)): #all letters
            print (itertools.product(mostusedletters, letters))
            for sub in (itertools.product(mostusedletters, letters)):
                plugboardtestpairs=dict(plugboardi.pairs)
                print (sub)
                print (plugboardtestpairs)
                plugboardtestpairs[sub[0]]=sub[1]
                plugboardtest=plugboard(plugboardtestpairs)
                enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardtest)    
                text=enigmai.EDcrypt(self.ttc)
                myscore=self.scorer.icscorer(text)
                print (self.scorer.icscorer(text))

                if (myscore>topscore):
                    topscore=myscore
                    lettersToRemove=[sub[0],sub[1]]
                    print ("LTR_IN:"+sub[0]+sub[1])

                input("Press Enter to continue...")

            if (lettersToRemove):
                print ("LTR_OUT"+lettersToRemove[0]+lettersToRemove[1])
                letters.remove(lettersToRemove[0])
                letters.remove(lettersToRemove[1])
                plugboardi.pairs[lettersToRemove[0]]=lettersToRemove[1]

                #2nd run myscore=self.scorer.score(text)
        
        return topscore,dict(plugboardi.pairs)
    '''

    def testHillClimb(self):
        print ("testHillClimb")
        bestoftherun=-10000
        myscore=-10000
        plugboardi=plugboard({})
        plugs1=2 #how many plugs we'd like to try to find in 1st run IC
        plugs2=4 #how many plugs we'd like to try to find in 2nd run trigram
        plugs3=2 #how many plugs we'd like to try to find in 3rd run trigram

        f = open("testHillClimb.txt", 'a')
        start=datetime.now()
        f.write("\n\nSTART: "+format(start, '%H:%M:%S')+"\n\n")
        f.flush()

        reflectori=reflector("C")
        rotor1=rotor("I",0,25)  #slowest, left-most
        rotor2=rotor("IV",21,0)  #middle
        rotor3=rotor("VI",15,3)  #fastest, right-most
        enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
        text=enigmai.EDcrypt(self.ttc)


        myic=self.scorer.icscorer(text)
        steckerscore,steckerinfo=self.steckerHillClimbTest(rotor1,rotor2,rotor3,reflectori,myscore,plugs1,plugs2,plugs3)

        if (steckerscore>-10000):
            bestoftherun=steckerscore
            infostring="Info "\
            +format(datetime.now(), '%H:%M:%S')\
            +"\nORIGINAL Score\n"+str(myic)\
            +"\nSTECKER Score\n"+str(steckerscore)\
            +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number\
            +" Ref:"+str(reflectori.typ)+"\n"\
            +"STECKER: "+str(steckerinfo)+"\n\n"
            f.write(infostring+"\n")
            f.flush()
        #print (text)

#cracker suitable for parallel computation
class crackerParallel():
    
    def __init__(self,textToCrack,scorer,subset,q):
        self.ttc=textToCrack
        self.subset=subset
        self.q=q
        self.scorer=scorer
    
    def fanal(self):
        list={}
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in pomlist:
            list.update({letter:0})
        for letter in self.text:
            list[letter] += 1         
        return list

#there are two possible methods to do brute force + hill-climbing. Each comprises of several steps

# Method #1:
# 1st step: brute force reflectors (2) + walzen order (60) + positions (26^3) using Index of Coincidence (IC). 
# Combinations: 2 109 120
# 2nd step: brute force fastest (3rd) and middle (2nd) ring settings (26^2) using IC.
# Combinations: 676
# 3rd step: Hill-climb first 4 steckers using IC.
# Combinations: 150 738 274 937 250 [26!/(6!*10!*2^10)] = not feasible to brute force.
# 4th step: Hill-climb steckers using trigrams (possibly bigrams/quadgrams).
# Combinations: 150 738 274 937 250 [26!/(6!*10!*2^10)] = not feasible to brute force.
#
# Steckers (when X steckers are connected):
# Plain = % of Plaintext 
# Mono  = % of Monoalphabetic substition
# Mist  = % of Mist/Garble
#
# X     Plain   Mono    Mist
# 0  :  10.1    18.5    71.4 <--- 71.4% is mist, can't use trigrams. Use IC on Mono part
# 1  :  13.3    22.4    64.3
# 2  :  17.8    25.0    57.2
# 3  :  23.6    26.4    50.0
# 4  :  30.6    26.5    42.9 <--- mist clears up significantly, can now use trigrams
# 5  :  39.0    25.3    35.7
# 6  :  48.6    22.8    28.6
# 7  :  59.6    19.0    21.4
# 8  :  71.7    14.0    14.3
# 9  :  85.2     7.7     7.1
# 10 : 100.0     0.0     0.0
#
#
# Method #2 (much slower due to 1st step):
# 1st step: brute force reflectors (2) + walzen order (60) + positions (26^3) + fastest (3rd) ring (26) using IC.
# Combinations: 54 837 120
# 2nd step: Hill-climb first few (~3-4) steckers using monograms. 
# Combinations: 3 453 450 - 164 038 875
# 3rd step: Hill-climb next few (~3-4) steckers using bigrams. 
# Combinations: 3 453 450 - 164 038 875
# 4th step: Hill-climb last few (~2-3) steckers using trigrams. 
# Combinations: 44 850 -  3 453 450
#
# Method #3 
# 1st step: precompute all possible combinations 27 418 560 (54 837 120 with 2 types of reflector)
# 2nd step: Hill-climb using same technique as in method #1
#
#Index of Coincidence (IC):
#Random text, that is where all letters are present with nearly the same frequency, will have an IC 
#‘score’ of 1/26 or 0.03846. If we measure the IC score of plain Enigma text it can be up to around 
#0.05 to 0.07, depending on the actual frequencies of the letters in the plain message. German IC = 0.0762
#

    def ultimate_MP_method_1(self): 
        #1st step is to find out the plausible walzen and ring settings candidates for next steps using IC
        messagelenght=len(self.ttc)
        ic=0.040 #threshold, everything less than this won't be even evaluated further
        topic=ic

        plugboardi=plugboard({})
        bestoftherun=-10000
        myscore=-10000
        botrstring=""

        #-1725 bi1941 #-2900 tri #-4300 quad
        steckertop=-2900

        for r in range(2):
            if r==0:
                reflectori=reflector("B")
            else:
                reflectori=reflector("C")
            for i in range(26):
                for j in range(26):
                    for k in range(26):
                        rotor1=rotor(self.subset[0],0,i)  #slowest, left-most
                        rotor2=rotor(self.subset[1],0,j)  #middle
                        rotor3=rotor(self.subset[2],0,k)  #fastest, right-most
                        enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
                        text=enigmai.EDcrypt(self.ttc)
                        myic=self.scorer.icscorer(text)
                        #myscore=self.scorer_mono.score(text) #in case we'd need monograms (but we don't at this moment)
                        
                        if (myic>ic):
                            topic=myic
                            '''
                            strtowrite=""+format(datetime.now(), '%H:%M:%S')\
                            +"\n 1st step Score\n"+str(myic)+"\nGuess: "+text\
                            +"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)\
                            +" Ring3: "+str("0")+" Wheels: "\
                            +rotor1.number+":"+rotor2.number+":"+rotor3.number\
                            +" Ref:"+str(reflectori.typ)+"\n"
                            self.q.put(strtowrite)
                            '''
                            
                            #2nd step is to test right-most and middle rotor combinations for the best scored ones
                            for x in range(26):
                                for y in range(26):
                                        #r3shift=0+y
                                        #r2shift=0
                                        #if (rotor2.step>=r3shift):
                                        #    r2shift=1

                                        #rotor1=rotor(self.subset[0],0,i)
                                        #rotor2=rotor(self.subset[1],x,(abs(j-r2shift-x)%26))
                                        #rotor3=rotor(self.subset[2],y,((k+r3shift)%26))
                                        rotor1=rotor(self.subset[0],0,i)
                                        rotor2=rotor(self.subset[1],x,j)
                                        rotor3=rotor(self.subset[2],y,k)
                                        enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)
                                        text=enigmai.EDcrypt(self.ttc)

                                        myic=self.scorer.icscorer(text)

                                        #3rd step is Hill-climbing steckers using trigrams
                                        if (myic>topic and myic>0.042):
                                            topic=myic

                                            strtowrite=""+format(datetime.now(), '%H:%M:%S')\
                                            +"\n2nd step Score\n"+str(myic)+"\nGuess: "+text\
                                            +"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)\
                                            +" Ring2: "+str(x)+ " Ring3: "+str(y)+" Wheels: "\
                                            +rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                            +" Ref:"+str(reflectori.typ)+"\n"
                                            self.q.put(strtowrite)

                                            #bestoftherun=topscore #nope
                                            #stecker
                                           
                                            '''strtowrite=""+format(datetime.now(), '%H:%M:%S')
                                            +"\nORIGINAL Score\n"+str(myscore)+"\nGuess: "
                                            +text+"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)
                                            +" Grunds new: "+str(i)+":"
                                            +str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)
                                            +" Ring3: "+str(o)
                                            +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                            +" Ref:"+str(reflectori.typ)+"\n"
                                            #self.q.put(strtowrite)
                                            '''
                                            myscore=self.scorer.score(text)
                                            steckerscore,steckerinfo=self.steckerHillClimb(rotor1,
                                                                                           rotor2,
                                                                                           rotor3,
                                                                                           reflectori,
                                                                                           myscore)

                                            

                                            if (steckerscore>bestoftherun):
                                                bestoftherun=steckerscore
                                                botrstring="BOTR info "\
                                                +format(datetime.now(), '%H:%M:%S')\
                                                +"\nORIGINAL Score\n"+str(myic)\
                                                +"\nSTECKER Score\n"+str(steckerscore)\
                                                +"\nGuess: "+text+"\nGrunds original: "\
                                                +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "\
                                                #+str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)\
                                                +" Ring3: "+str(x)\
                                                +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                                +" Ref:"+str(reflectori.typ)+"\n"\
                                                +"STECKER: "+str(steckerinfo)+"\n\n"

                                            #stecker
                                            
                                            if (steckerscore>-2850 or steckerscore>steckertop):
                                                strtowrite="!!! info"\
                                                +format(datetime.now(), '%H:%M:%S')\
                                                +"\nORIGINAL Score\n"+str(myic)\
                                                +"\nSTECKER Score\n"+str(steckerscore)\
                                                +"\nGuess: "+text+"\nGrunds original: "\
                                                +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "\
                                                #+str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)\
                                                +"Ring2: "+str(x)+" Ring3: "+str(y)\
                                                +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                                +" Ref:"+str(reflectori.typ)+"\n"\
                                                +"STECKER: "+str(steckerinfo)+"\n\n"

                                                self.q.put(strtowrite)
        if (bestoftherun > -10000):
            strtowrite="BOTR: "+str(bestoftherun)+"\n"+str(botrstring)
        strtowrite=""
        self.q.put(strtowrite)                          

    def ultimate_MP_method2(self):
        #1st step is to find out the plausible walzen and ring settings candidates for next steps using monograms
        #plugboardi=plugboard({"A":"B","C":"D","E":"F","G":"H","I":"J","K":"L","M":"N","O":"P","Q":"R","S":"T"})
        messagelenght=len(self.scrambled)
        plugboardi=plugboard({})
        bestoftherun=-10000
        botrstring=""
        topscore=-10000
        for r in range(2):
            if r==0:
                reflectori=reflector("B")
            else:
                reflectori=reflector("C")
            for i in range(26):
                for j in range(26):
                    for k in range(26):
                        for x in range(1):
                            #print(subset)
                            rotor1=rotor(self.subset[0],0,i) #slowest, left-most
                            rotor2=rotor(self.subset[1],0,j) #middle
                            rotor3=rotor(self.subset[2],x,k) #fastest, right-most
                            enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
                            text=enigmai.EDcrypt(self.ttc)
                            myscore=self.scorer.score(text)
                                    
                            if (myscore>topscore) or (myscore>-1900):
                                #-1950 bi1941 #4400 quad
                                topscore=myscore
                                strtowrite="a "+format(datetime.now(), '%H:%M:%S')\
                                +"\nORIGINAL Score\n"+str(myscore)+"\nGuess: "+text\
                                +"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)\
                                +" Ring3: "+str("0")+" Wheels: "\
                                +rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                +" Ref:"+str(reflectori.typ)+"\n"
                                self.q.put(strtowrite)                                                                                                             

                                '''
                                if (myscore>-900): #4350 quad
                                    
                                    strtowrite="\n???\n"+format(datetime.now(), '%H:%M:%S')
                                    +"\nORIGINAL Score\n"+str(myscore)+"\nGuess: "
                                    +text+"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)+" Ring3: "+str("0")
                                    +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                    +" Ref:"+str(reflectori.typ)+"\n"
                                    self.q.put(strtowrite)
                                '''
                                
                                for p in range(26):
                                    for o in range(26):
                                            r3shift=0+o
                                            r2shift=0
                                            if (rotor2.step>=r3shift):
                                                r2shift=1

                                            rotor1=rotor(self.subset[0],l,i)
                                            rotor2=rotor(self.subset[1],m,(abs(j-r2shift-p)%26))
                                            rotor3=rotor(self.subset[2],o,((k+r3shift)%26))
                                            enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)
                                            text=enigmai.EDcrypt(self.ttc)
                                            myscore=self.scorer.score(text)
                                                
                                            if (myscore>topscore):
                                                topscore=myscore
                                                bestoftherun=topscore
                                                #stecker
                                                
                                                '''strtowrite=""+format(datetime.now(), '%H:%M:%S')
                                                +"\nORIGINAL Score\n"+str(myscore)+"\nGuess: "
                                                +text+"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)
                                                +" Grunds new: "+str(i)+":"
                                                +str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)
                                                +" Ring3: "+str(o)
                                                +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                                +" Ref:"+str(reflectori.typ)+"\n"
                                                #self.q.put(strtowrite)
                                                '''

                                                steckerscore,steckerinfo=self.steckerHillClimb(rotor1,
                                                                                               rotor2,
                                                                                               rotor3,
                                                                                               reflectori,
                                                                                               myscore)
                                                
                                                '''
                                                #strtowrite="STECKER info"+format(datetime.now(), '%H:%M:%S')
                                                +"\nORIGINAL Score\n"+str(myscore)+"\nSTECKER Score\n"+str(steckerscore)
                                                +"\nGuess: "+text
                                                +"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)
                                                +" Grunds new: "+str(i)+":"
                                                +str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)
                                                +" Ring3: "+str(o)
                                                +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                                +" Ref:"+str(reflectori.typ)+"\n"
                                                +"STECKER: "+str(steckerinfo)+"\n\n"
                                                #self.q.put(strtowrite)
                                                '''
                                                
                                                if (steckerscore>bestoftherun):
                                                    bestoftherun=steckerscore
                                                    botrstring="BOTR info "\
                                                    +format(datetime.now(), '%H:%M:%S')\
                                                    +"\nORIGINAL Score\n"+str(myscore)\
                                                    +"\nSTECKER Score\n"+str(steckerscore)\
                                                    +"\nGuess: "+text+"\nGrunds original: "\
                                                    +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "\
                                                    +str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)\
                                                    +" Ring3: "+str(o)+" Wheels: "\
                                                    +rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                                    +" Ref:"+str(reflectori.typ)+"\n"\
                                                    +"STECKER: "+str(steckerinfo)+"\n\n"

                                                #stecker
                                                
                                                if (steckerscore>-2800):
                                                    #1725 bi1941 #4300 quad
                                                    strtowrite="!!! info"\
                                                    +format(datetime.now(), '%H:%M:%S')\
                                                    +"\nORIGINAL Score\n"+str(myscore)\
                                                    +"\nSTECKER Score\n"+str(steckerscore)\
                                                    +"\nGuess: "+text+"\nGrunds original: "\
                                                    +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "\
                                                    +str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)\
                                                    +" Ring3: "+str(o)\
                                                    +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                                    +" Ref:"+str(reflectori.typ)+"\n"\
                                                    +"STECKER: "+str(steckerinfo)+"\n\n"

                                                    self.q.put(strtowrite)
        strtowrite="BOTR: "+str(bestoftherun)+"\n"+str(botrstring)
        self.q.put(strtowrite)                                                               
                                                        
    def steckerHillClimb(self,rotor1,rotor2,rotor3,reflectori,score):
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        plugboardi=plugboard({})

        '''
        for subset in itertools.combinations("A","B","C","D","E","F","G","H","I",
        "J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", 2):
        '''
        
        '''letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]'''

        #we'll try to hill-climb just the most used pairs
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        mostusedletters = ["E","N","X","R","S"]

        #list(itertools.product(mostusedletters, letters))
        #letters.remove("")
        steckerinfo=[]
        lettersToRemove=[]
        topscore=score
        #allcombs = itertools.combinations(letters, 2)
        for i in range(10):
            lettersToRemove[:] = []
            plugboardtestpairs = {}
            #for sub in (itertools.combinations(letters, 2)): #all letters
            for sub in (itertools.product(mostusedletters, letters)):
                plugboardtestpairs=dict(plugboardi.pairs)
                plugboardtestpairs[sub[0]]=sub[1]
                plugboardtest=plugboard(plugboardtestpairs)
                enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardtest)    
                text=enigmai.EDcrypt(self.ttc)
                myscore=self.scorer.score(text)
                print (self.scorer.icscorer(text))
                
                if (myscore>topscore):
                    topscore=myscore
                    lettersToRemove=[sub[0],sub[1]]
            if (lettersToRemove):
                letters.remove(lettersToRemove[0])
                letters.remove(lettersToRemove[1])
                plugboardi.pairs[lettersToRemove[0]]=lettersToRemove[1]

        return topscore,dict(plugboardi.pairs)
                            
    def finalRing(self):
        #ring cracker is good for cracking ciphers with some values known
            #plugboardi=plugboard({"A":"B","C":"D","E":"F","G":"H","I":"J","K":"L","M":"N","O":"P","Q":"R","S":"T"})
            plugboardi=plugboard({"":"","":"","":"","":"","":"",
                                  "":"","":"","":"","":"","":""})
            #reflectori=reflector("B")
            #B grunds20:8:14 wheelsII:V:IV
            #p.2 reflector: B grunds: 11:12:13 wheels: II:V:IV
            topscore=-10000
            reflectori=reflector("B")
            for j in range(26):
                for k in range(26):
                    rotor1=rotor("IV",self.subset,3)
                    rotor2=rotor("III",j,8)
                    rotor3=rotor("I",k,3)                                                                    
                    enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
                    text=enigmai.EDcrypt(self.ttc)
                    myscore=self.scorer.score(text)
                                        
                    if (myscore>topscore) and (myscore>-4400):
                        topscore=myscore
                        strtowrite="Score"+str(topscore)+" Guess: "+text
                        +" Rings:" +str(self.subset)+":"+str(j)+":"+str(k)
                        +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                        +" Ref:"+str(reflectori.typ)+"\n"
                        self.q.put(strtowrite)
def final(subset,q):
    #insert the scrambled text 547 char long
    scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    #scorer_mono=ngram_score('grams/german_monograms.txt')
    #scorer_bi=ngram_score('grams/german_bigrams.txt')
    scorer_tri=ngram_score('grams/german_trigrams1941.txt')
    #scorer_quad=ngram_score('grams/german_quadgrams.txt')
    scorer=scorer_tri

    crackerF=crackerParallel(scrambled,scorer,subset,q)
    crackerF.ultimate_MP_method_1()

def finalRing(subset,q):
    #insert the scrambled text 547 char long
    scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    scorer=ngram_score('grams/german_quadgrams.txt')
    crackerF=crackerParallel(scrambled,scorer,subset,q)
    crackerF.finalRing()

def listener(q):
    '''listens for messages on the q, writes to file. '''

    f = open("attempt.txt", 'a')
    start=datetime.now()
    f.write("\n\nSTART: "+format(start, '%H:%M:%S')+"\n\n")
    f.flush()
    while 1:
        m = q.get()
        if m == 'kill':
            f.write("STOP: "+format(datetime.now(), '%H:%M:%S')+"\nRUN TIME: "+str(datetime.now()-start)+"\nEND\n\n\n")
            print ("STOP: "+format(datetime.now(), '%H:%M:%S')+"\nRUN TIME: "+str(datetime.now()-start))
            f.flush()
            break
        f.write(str(m) + '\n')
        f.flush()
    f.close()

if __name__ == "__main__":

    '''
    print ("test")
    scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    #scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTL" 
    scorer_tri=ngram_score('grams/german_trigrams1941.txt')
    crackerTest=cracker(scrambled)
    crackerTest.test()
    '''
    print ("test")
    scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    scorer_tri=ngram_score('grams/german_trigrams1941.txt')
    crackerTest=cracker(scrambled,scorer_tri)
    crackerTest.testHillClimb()
    '''

    print("Entering the castle of Aaaaaaaaaaaaaaaaaargh")
    walzennumbers = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]  
    #jobs = []
    print ("Logical cores available %d" % multiprocessing.cpu_count())
    noteating=2
    print ("Cores NOT being eaten omnomnom %d" % noteating)
    
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(multiprocessing.cpu_count()-noteating) #use logical cores
    
    watcher = pool.apply_async(listener, (q,))

    jobs = []
    
    #if we want to chceck walzen subsets or just speed computation across cores without walzens
    walzen=True

    if (walzen):
        for subset in itertools.permutations(walzennumbers, 3):
            job = pool.apply_async(final, (subset,q))
             #p=multiprocessing.Process(target=multi7, args=(subset,))
                #jobs.append(p)
                #p.start()
            jobs.append(job)
    else:
        for subset in range(26):
            job = pool.apply_async(finalRing, (subset,q))
            jobs.append(job)
            
    for job in jobs: 
        job.get()
    
    q.put('kill')
    pool.close()
    pool.join()
    '''
    