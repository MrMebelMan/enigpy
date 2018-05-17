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
    
class cracker():
    
    def __init__(self,textToCrack):
        self.ttc=textToCrack
    
    def fanal(self):
        list={}
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in pomlist:
            list.update({letter:0})
        for letter in self.text:
            list[letter] += 1
            
        return list    


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
                            
    def finalMP(self):
        #plugboardi=plugboard({"A":"B","C":"D","E":"F","G":"H","I":"J",
                            #"K":"L","M":"N","O":"P","Q":"R","S":"T"})
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
                        for l in range(1):
                            for m in range(1):
                                for n in range(1):
                            #print(subset)
                                    rotor1=rotor(self.subset[0],l,i)
                                    rotor2=rotor(self.subset[1],m,j)
                                    rotor3=rotor(self.subset[2],n,k)
                                    enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
                                    text=enigmai.EDcrypt(self.ttc)
                                    myscore=self.scorer.score(text)
                                    
                                    if (myscore>topscore) or (myscore>-1900):
                                        #-1950 bi1941 #4400 quad
                                        topscore=myscore
                                        strtowrite=""+format(datetime.now(), '%H:%M:%S')
                                        +"\nORIGINAL Score\n"+str(myscore)+"\nGuess: "
                                        +text+"\nGrunds original: "
                                        +str(i)+":"+str(j)+":"+str(k)+" Ring3: "+str("0")
                                        +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
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
                                                        
                                                        steckerscore,steckerinfo=self.steckerConfig(rotor1,
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
                                                            botrstring="BOTR info "
                                                            +format(datetime.now(), '%H:%M:%S')
                                                            +"\nORIGINAL Score\n"+str(myscore)
                                                            +"\nSTECKER Score\n"+str(steckerscore)
                                                            +"\nGuess: "+text+"\nGrunds original: "
                                                            +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "
                                                            +str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)
                                                            +" Ring3: "+str(o)+" Wheels: "
                                                            +rotor1.number+":"+rotor2.number+":"+rotor3.number
                                                            +" Ref:"+str(reflectori.typ)+"\n"
                                                            +"STECKER: "+str(steckerinfo)+"\n\n"

                                                        #stecker
                                                        
                                                        if (myscore>-1725 or steckerscore>-1725):
                                                            #1725 bi1941 #4300 quad
                                                            strtowrite="!!! info"
                                                            +format(datetime.now(), '%H:%M:%S')
                                                            +"\nORIGINAL Score\n"+str(myscore)
                                                            +"\nSTECKER Score\n"+str(steckerscore)
                                                            +"\nGuess: "+text+"\nGrunds original: "
                                                            +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "
                                                            +str(i)+":"+str(abs(j-r2shift)%26)+":"+str((k+r3shift)%26)
                                                            +" Ring3: "+str(o)
                                                            +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                                            +" Ref:"+str(reflectori.typ)+"\n"
                                                            +"STECKER: "+str(steckerinfo)+"\n\n"
                                                            self.q.put(strtowrite)
        strtowrite="BOTR: "+str(bestoftherun)+"\n"+str(botrstring)
        self.q.put(strtowrite)                                                    
                                                        
    def steckerConfig(self,rotor1,rotor2,rotor3,reflectori,score):
        pomlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        plugboardi=plugboard({})
        
        '''
        for subset in itertools.combinations("A","B","C","D","E","F","G","H","I",
        "J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", 2):
        '''
        
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        #letters.remove("")
        steckerinfo=[]
        lettersToRemove=[]
        topscore=score
        #allcombs = itertools.combinations(letters, 2)
        for i in range(10):
            lettersToRemove[:] = []
            plugboardtestpairs = {}
            for sub in (itertools.combinations(letters, 2)):
                plugboardtestpairs=dict(plugboardi.pairs)
                plugboardtestpairs[sub[0]]=sub[1]
                plugboardtest=plugboard(plugboardtestpairs)
                enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardtest)    
                text=enigmai.EDcrypt(self.ttc)
                myscore=self.scorer.score(text)
                
                if (myscore>topscore):
                    topscore=myscore
                    lettersToRemove=[sub[0],sub[1]]
            if (lettersToRemove):
                letters.remove(lettersToRemove[0])
                letters.remove(lettersToRemove[1])
                plugboardi.pairs[lettersToRemove[0]]=lettersToRemove[1]

        return topscore,dict(plugboardi.pairs)
                            
    def finalRing(self):
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


    def finalSimple(self):
        #plugboardi=plugboard({"A":"B","C":"D","E":"F","G":"H","I":"J","K":"L","M":"N","O":"P","Q":"R","S":"T"})
        #plugboardi=plugboard({"":"","":"","":"","":"","":"","":"","":"","":"","":"","":""})
        plugboardi=plugboard({"":""})
        #reflectori=reflector("B")
        #B grunds20:8:14 wheelsII:V:IV
        #p.2 reflector: B grunds: 11:12:13 wheels: II:V:IV
        topscore=-10000
        
        for r in range(2):
            if r==0:
                reflectori=reflector("B")
            else:
                reflectori=reflector("C")
            for i in range(26):
                for j in range(26):
                    for k in range(26):
                        for l in range(1):
                            for m in range(1):
                                for n in range(1):
                            #print(subset)
                                    rotor1=rotor(self.subset[0],l,i)
                                    rotor2=rotor(self.subset[1],m,j)
                                    rotor3=rotor(self.subset[2],n,k)
                                    enigmai = enigma (rotor1, rotor2, rotor3, reflectori, plugboardi)    
                                    text=enigmai.EDcrypt(self.ttc)
                                    myscore=self.scorer.score(text)
                                    
                                    if (myscore>topscore) and (myscore>-320):
                                        topscore=myscore
                                        strtowrite="Score"+str(topscore)
                                        +" Guess: "+text
                                        +" Grunds: "+str(i)+":"+str(j)+":"+str(k)+" Ring2: "+str(o)+" Ring3: "+str(n)
                                        +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number
                                        +" Ref:"+str(reflectori.typ)+"\n"
                                        self.q.put(strtowrite)                                        
    
def final(subset,q):
    #insert the scrambled text
    scrambled="""KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSA
    ZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSK
    EUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZ
    UNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZD
    PNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRM
    KNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHM
    IOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHA
    RLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS"""
    scorer=ngram_score('enigma\\grams\\german_bigrams1941.txt')
    crackerF=crackerParallel(scrambled,scorer,subset,q)
    crackerF.finalMP()
    #q.put(cracker7mp.seventhMP())
    
def finalRing(subset,q):
    #insert the scrambled text
    scrambled="""KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSA
    ZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSK
    EUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZ
    UNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZD
    PNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRM
    KNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHM
    IOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHA
    RLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS"""
    scorer=ngram_score('enigma\\grams\\german_quadgrams.txt')
    crackerF=crackerParallel(scrambled,scorer,subset,q)
    crackerF.finalRing()
    
def listener(q):
    '''listens for messages on the q, writes to file. '''

    f = open("enigma\attempt.txt", 'a')
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

    print("Entering the castle of Aaaaaaaaaaaaaaaaaargh")
    walzennumbers = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]  
    #jobs = []
    print ("Logical cores available %d" % multiprocessing.cpu_count())
    noteating=2
    print ("Cores NOT being eaten omnomnom %d" % noteating)
    
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(multiprocessing.cpu_count()-noteating) #use logical cores 1-12
    
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