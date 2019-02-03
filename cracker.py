from components import Plugboard, Reflector, Rotor
from crypto import Enigma
from scorers import ngram_score
from datetime import datetime
from string import ascii_uppercase as pomlist
from time import time

class cracker():
    
    def __init__(self,grundStellung,textToCrack,scorer):
        self.grundStellung = grundStellung
        self.ttc = textToCrack
        self.scorer = scorer
        self.rotors = dict()

    def decodeGrundStellung(self):
        #find out the starting grund stellung if we know the other parts
        enigma = Enigma(
            rotors={
                1: Rotor("VIII",19-1,pomlist.index(self.grundStellung[0])),  # slowest, left-most
                2: Rotor("II",7-1,pomlist.index(self.grundStellung[1])),  # middle
                3: Rotor("IV",12-1,pomlist.index(self.grundStellung[2])),  # fastest, right-most
            },
            reflector = Reflector("B"),
            plugboard = Plugboard({"B":"D","C":"O","E":"I","G":"L","J":"S","K":"T","N":"V","P":"M","Q":"R","W":"Z"})
        )  
        text = enigma.EDcrypt(self.grundStellung[3:])

        return text

    def test(self):
        #print (self.grundStellung)
        grunds = self.decodeGrundStellung()

        enigma = Enigma(
            rotors = {
                1: Rotor("VIII", 19-1, pomlist.index(grunds[0])),  #slowest, left-most
                2: Rotor("II", 7-1, pomlist.index(grunds[1])),  #middle
                3: Rotor("IV", 12-1, pomlist.index(grunds[2])),  #fastest, right-most
            },
            reflector = Reflector("B"),
            plugboard = Plugboard({"B":"D","C":"O","E":"I","G":"L","J":"S","K":"T","N":"V","P":"M","Q":"R","W":"Z"})
        )
        text = enigma.EDcrypt(self.ttc)
        print ("DECRYPTED TEXT: "+text)
        print ("STECKERS: {'B':'D','C':'O','E':'I','G':'L','J':'S','K':'T','N':'V','P':'M','Q':'R','W':'Z'}")  

    def testHillClimb(self):
        #print ("testHillClimb")
        bestoftherun = -10000
        bestoftherunIC = -10000
        bestoftherunGRAM = -10000
        myscore = -10000

        steckerscoreIC = -10000
        steckerscoreGRAM = -10000
        steckerscoreAIC = -10000

        steckerinfo = []
        
        plugsIC = 4 # how many plugs we'd like to try to find in 1st run IC
        plugsGRAM = 6 # how many plugs we'd like to try to find in 2nd run trigram
        plugs3 = 0 # how many plugs we'd like to try to find in 3rd run trigram

        f = open("testHillClimb.txt", 'a')
        start = datetime.now()
        f.write("\n\nSTART: "+format(start, '%H:%M:%S')+"\n\n")
        f.flush()

        grunds = self.decodeGrundStellung()
        enigma = Enigma(
            rotors = {
                1: Rotor("VIII", 19-1, pomlist.index(grunds[0])),  # slowest, left-most
                2: Rotor("II", 7-1, pomlist.index(grunds[1])),  # middle
                3: Rotor("IV", 12-1, pomlist.index(grunds[2])),  # fastest, right-most
            },
            reflector = Reflector("B"),
            plugboard = Plugboard({})
        )    
        text = enigma.EDcrypt(self.ttc)

        myic = self.scorer.icscore(text)
        print ("Original IC / plain text (before heuristics): "+str(myic))
        startTime = time()     
        steckerscoreIC,steckerscoreGRAM,steckerscoreAIC,steckerinfo = self.steckerHillClimbTest(enigma, myic,plugsIC,plugsGRAM)
        print ("Execution time is: %.3fs" % (time()-startTime))
        print ("\nScores\n"+"Original IC:"+str(myic)+"\nAfterwards IC:"+str(steckerscoreAIC)+"\nTrigram:"+str(steckerscoreGRAM))
        print ("End of heuristics\n\n")

        print ("Heuristics results:")
        if ((steckerscoreIC > bestoftherunIC and steckerscoreAIC > 0.05) or (steckerscoreGRAM > bestoftherunGRAM and steckerscoreAIC > 0.06)):
                                                #print ("CHECKTHISOUT: " +text+"\n")
            bestoftherunIC = steckerscoreIC
            bestoftherunGRAM = steckerscoreGRAM
            #print ("\nScores\n"+"Original IC:"+str(steckerscoreIC)+"\nAfterwards IC:"+str(steckerscoreAIC)+"\nTrigram:"+str(steckerscoreGRAM))
            #print (str(steckerinfo))
            #print ("TEXT: " +text+"\n")

            if (steckerscoreAIC > 0.065):                                         
                print ("BINGO IC!!! "+str(steckerscoreAIC))
                print ("BEST DESCRYPTED TEXT (IC METHOD): " +text+"\n")    
                print ("STECKERS:"+str(steckerinfo))

            if (steckerscoreGRAM>-1500):
                print ("BINGO GRAM!!! GRAM: "+str(steckerscoreGRAM)) # Trigram score
                print ("BINGO GRAM!!! ORIC: "+str(myic))   # original IC score
                print ("BINGO GRAM!!! BEIC: "+str(steckerscoreIC))   # IC score after first 4 plugs
                print ("BINGO GRAM!!! AFIC: "+str(steckerscoreAIC)+"\n")   # IC sore after Trigrams applied
                print ("BEST DESCRYPTED TEXT (GRAM METHOD): " +text)  
                print ("STECKERS:"+str(steckerinfo))                
             
        #print (text)

    def steckerHillClimbTest(self, enigma, score,plugsIC,plugsGRAM):
        # we'll try to hill-climb just the most used pairs
        mostusedletters = ["E","N","X","R"] # we will use 4 most used letters for the 1st run using IC
        mostusedletters2ndrun = ["S","T","A","H","D","U","L","C","G","M",
                                 "O","B","W","F","K","Z","V","P","J","Y","Q"] #2nd run for trigrams
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        bestpairscoreGRAM = -10000
        topscore = score
        bestpairscoreIC = score

        best = ["",""]
        best[0] = ""
        best[1] = ""

        initial_enigma_setup = enigma

        #print ("Top score: "+str(topscore))
        for i in range(plugsIC):  #find the first best pair out of most used letters
            for firstletter in mostusedletters:
                for secondletter in letters: #check every combination of the most used letters one by one
                    if (secondletter != firstletter):
                        plugboardtestpairs={firstletter:secondletter}
                        plugboardtestdict = dict(plugboardtestpairs, **enigma.plugboard.wiring)
                        enigma.plugboard.setWiring(plugboardtestdict)
                        text = enigma.EDcrypt(self.ttc)
                        myscore = self.scorer.icscore(text)
                        #print (myscore)
                        if (myscore > bestpairscoreIC):
                            bestpairscoreIC = myscore
                            best = [firstletter,secondletter]
                            #print ("Best one: "+str(bestpairscore)+" "+firstletter+secondletter)
            #print ("letas:"+str(letters))
            #print ("most:"+str(mostusedletters))
            #print (best[0])
            #print (best[1])
            if (best[0] in letters):
                letters.remove(best[0])

            if (best[1] in letters):
                letters.remove(best[1])

            if (best[0] in mostusedletters):
                mostusedletters.remove(best[0])
           
            enigma.plugboard.wiring[best[0]]=best[1]
            
            best[0] = ""
            best[1] = ""

        if not enigma.plugboard:
                return bestpairscoreIC, bestpairscoreGRAM, plugboard.wiring

        if (bestpairscoreIC > score):
            # if we found something, we continue to hill-climb

            enigma = initial_enigma_setup  # initial trigram score
            text = enigma.EDcrypt(self.ttc)
            bestpairscoreGRAM = self.scorer.score(text)

            for i in range(plugsGRAM):
                for firstletter in mostusedletters2ndrun:
                    for secondletter in letters: #check every combination of the most used letters one by one
                        if (secondletter != firstletter):
                            plugboardtestpairs={firstletter:secondletter}
                            plugboardtestdict = dict(plugboardtestpairs, **enigma.plugboard.wiring)
                            enigma.plugboard.setWiring(plugboardtestdict)
                            text = enigma.EDcrypt(self.ttc)
                            myscore = self.scorer.score(text)
                            #print (myscore)
                            if (myscore > bestpairscoreGRAM):
                                bestpairscoreGRAM = myscore
                                best = [firstletter,secondletter]

            if (best[0] in letters):
                letters.remove(best[0])

            if (best[1] in letters):
                letters.remove(best[1])

            if (best[0] in mostusedletters2ndrun):
                mostusedletters2ndrun.remove(best[0])
           
            enigma.plugboard.wiring[best[0]] = best[1]
            
            best[0] = ""
            best[1] = ""

        #print ((enigma.plugboard.wiring))

        # IC calculation after the 2nd step of hill climb
        enigma = initial_enigma_setup
        text = enigma.EDcrypt(self.ttc)
        afterwardsIC = self.scorer.icscore(text)

        return bestpairscoreIC, bestpairscoreGRAM, afterwardsIC, enigma.plugboard.wiring

    

    def steckerHillClimbTest2(self, enigma, score, plugs1, plugs2, plugs3):
        # we'll try to hill-climb just the most used pairs
        mostusedletters = ["E","N","X","R"] # we will use 4 most used letters for the 1st run using IC
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        
        topscore = score
        bestpairscore = score

        #print ("Top score: "+str(topscore))
        for i in range(plugs1):  #find the first best pair out of most used letters
            #print (i)
            for firstletter in mostusedletters:
                for secondletter in letters: #check every combination of the most used letters one by one
                    if (secondletter != firstletter):
                        plugboardtestpairs={firstletter:secondletter}
                        plugboardtestdict = dict(plugboardtestpairs, **enigma.plugboard.wiring)
                        enigma.plugboard.setWiring(plugboardtestdict)
                        text = enigma.EDcrypt(self.ttc)
                        myscore = self.scorer.icscore(text)

                        if (myscore > bestpairscore):
                            bestpairscore = myscore
                            best = [firstletter,secondletter]
                            #print ("Best one: "+str(bestpairscore)+" "+firstletter+secondletter)
            #print (best[0])
            #print (best[1])
            letters.remove(best[0])
            letters.remove(best[1])
            mostusedletters.remove(best[0])
            enigma.plugboard.wiring[best[0]] = best[1]
            best[0] = ""
            best[1] = ""

        return bestpairscore, enigma.plugboard
    


#cracker suitable for parallel computation
class crackerParallel():
    
    def __init__(self,textToCrack,scorer,subset,q):
        self.ttc = textToCrack
        self.subset = subset
        self.q = q
        self.scorer = scorer

    def steckerHillClimbTest(self, rotors: dict, reflector, score, plugsIC, plugsGRAM):
        # we'll try to hill-climb just the most used pairs
        mostusedletters = ["E","N","X","R"] # we will use 4 most used letters for the 1st run using IC
        mostusedletters2ndrun = ["S","T","A","H","D","U","L","C","G","M",
                                 "O","B","W","F","K","Z","V","P","J","Y","Q"] #2nd run for trigrams
        letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        bestpairscoreGRAM = -10000
        topscore = score
        bestpairscoreIC = score

        best = ["",""]
        best[0]=""
        best[1]=""
        enigma = Enigma(
            rotors = rotors,
            reflector = reflector,
            plugboard = Plugboard({})
        )

        #print ("Top score: "+str(topscore))
        for i in range(plugsIC):  #find the first best pair out of most used letters
            #print (i)
            for firstletter in mostusedletters:
                for secondletter in letters: #check every combination of the most used letters one by one
                    if (secondletter != firstletter):
                        plugboardtestpairs = {firstletter:secondletter}
                        plugboardtestdict = dict(plugboardtestpairs, **enigma.plugboard.wiring)
                        enigma.plugboard.setWiring(plugboardtestdict)
                        text = enigma.EDcrypt(self.ttc)
                        myscore = self.scorer.icscore(text)
                        #print (myscore)
                        if (myscore > bestpairscoreIC):
                            bestpairscoreIC = myscore
                            best = [firstletter,secondletter]
                            #print ("Best one: "+str(bestpairscore)+" "+firstletter+secondletter)
            #print ("letas:"+str(letters))
            #print ("most:"+str(mostusedletters))
            #print (best[0])
            #print (best[1])
            if (best[0] in letters):
                letters.remove(best[0])

            if (best[1] in letters):
                letters.remove(best[1])

            if (best[0] in mostusedletters):
                mostusedletters.remove(best[0])
           
            enigma.plugboard.wiring[best[0]] = best[1]
            
            best[0]=""
            best[1]=""
            
            #print ((enigma.plugboard.wiring))

        if not enigma.plugboard:  # FIXME
                return bestpairscoreIC, bestpairscoreGRAM, enigma.plugboard.wiring

        if (plugsGRAM > 0):
            # if we found something, we continue to hill-climb

            enigma = Enigma(rotors, reflector, enigma.plugboard)  # initial trigram score
            text = enigma.EDcrypt(self.ttc)
            bestpairscoreGRAM = self.scorer.score(text)
            #print (bestpairscoreGRAM)

            for i in range(plugsGRAM):
                for firstletter in mostusedletters2ndrun:
                    for secondletter in letters: #check every combination of the most used letters one by one
                        if (secondletter != firstletter):
                            plugboardtestpairs={firstletter:secondletter}
                            plugboardtestdict = dict(plugboardtestpairs, **enigma.plugboard.wiring)
                            enigma.plugboard.setWiring(plugboardtestdict)
                            text = enigma.EDcrypt(self.ttc)
                            myscore = self.scorer.score(text)
                            #print (myscore)
                            if (myscore > bestpairscoreGRAM):
                                bestpairscoreGRAM = myscore
                                best = [firstletter,secondletter]

            if (best[0] in letters):
                letters.remove(best[0])

            if (best[1] in letters):
                letters.remove(best[1])

            if (best[0] in mostusedletters2ndrun):
                mostusedletters2ndrun.remove(best[0])
           
            enigma.plugboard.wiring[best[0]] = best[1]
            
            best[0] = ""
            best[1] = ""

        #print ((enigma.plugboard.wiring))

        # IC calculation after the 2nd step of hill climb
        enigma = Enigma(rotors, reflector, enigma.plugboard)
        text = enigma.EDcrypt(self.ttc)
        afterwardsIC = self.scorer.icscore(text)

        return bestpairscoreIC, bestpairscoreGRAM, afterwardsIC, enigma.plugboard.wiring


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
        strtowrite = "!!! Starting at " +format(datetime.now(), '%H:%M:%S')+ " with: "+ self.subset[0]+"-"+self.subset[1]+"-"+ self.subset[2]     
        self.q.put(strtowrite)
        messagelenght = len(self.ttc)
        ic = 0.04 #threshold, everything less than this won't be even evaluated further
        topic = ic

        plugs1run = 4               #number of plugs to be indentified by IC
        plugs2run = 10 - plugs1run    #rest of the plugs, identified by trigram score

        bestoftherunIC = -10000
        bestoftherunGRAM = -10000
        myscore = -10000
        botrstring = ""

        #-1725 bi1941 #-2900 tri #-4300 quad
        steckertop = -2900

        enigma = Enigma(rotors=None, reflector=None, plugboard=Plugboard({}))    

        for r in range(2):
            for i in range(26):
                for j in range(26):
                    for k in range(26):
                        enigma.rotors = {
                            1: Rotor(self.subset[0],0,i),  # slowest, left-most
                            2: Rotor(self.subset[1],0,j),  # middle
                            3: Rotor(self.subset[2],0,k),  # fastest, right-most
                        }
                        enigma.reflector = Reflector("B" if r == 0 else "C")
                        text = enigma.EDcrypt(self.ttc)
                        myic = self.scorer.icscore(text)
                        #myscore = self.scorer_mono.score(text) #in case we'd need monograms (but we don't at this moment)
                        
                        if (myic > ic):
                            topic = myic
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
                                        #r3shift = 0+y
                                        #r2shift = 0
                                        #if (rotor2.step>=r3shift):
                                        #    r2shift = 1

                                        enigma.rotors = {
                                            1: Rotor(self.subset[0],0,i),  # slowest, left-most
                                            2: Rotor(self.subset[1],x,j),  # middle
                                            3: Rotor(self.subset[2],y,k),  # fastest, right-most
                                        }
                                        text = enigma.EDcrypt(self.ttc)

                                        myic = self.scorer.icscore(text)

                                        #3rd step is Hill-climbing steckers using trigrams
                                        if (myic > topic and myic > 0.040):
                                            topic = myic

                                            '''
                                            strtowrite=""+format(datetime.now(), '%H:%M:%S')\
                                            +"\n2nd step Score\n"+str(myic)+"\nGuess: "+text\
                                            +"\nGrunds original: "+str(i)+":"+str(j)+":"+str(k)\
                                            +" Ring2: "+str(x)+ " Ring3: "+str(y)+" Wheels: "\
                                            +rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                            +" Ref:"+str(reflectori.typ)+"\n"
                                            self.q.put(strtowrite)
                                            '''
                                            #bestoftherunIC = topscore #nope
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
                                            #myscore = self.scorer.score(text)
                                            steckerscoreIC,steckerscoreGRAM,steckerscoreAIC,steckerinfo = self.steckerHillClimbTest(rotors, reflectori, myic,plugs1run,plugs2run)

                                            #strtowrite="STECKER: "+str(steckerinfo)+"\n\n"
                                            #self.q.put(strtowrite)
                                            if ((steckerscoreIC > bestoftherunIC and steckerscoreAIC > 0.06) or (steckerscoreGRAM > bestoftherunGRAM and steckerscoreAIC > 0.06)):
                                                #print ("CHECKTHISOUT: " +text+"\n")
                                                bestoftherunIC = steckerscoreIC
                                                bestoftherunGRAM = steckerscoreGRAM
                                                strtowrite="Time "\
                                                +format(datetime.now(), '%H:%M:%S')\
                                                +"\nORIGINAL Score\n"+str(myic)\
                                                +"\nScores\n"+"Original IC:"+str(steckerscoreIC)+"\nAfterwards IC:"+str(steckerscoreAIC)+"\nTrigram:"+str(steckerscoreGRAM)\
                                                +"\nGuess: "+text+"\nGrunds original: "\
                                                +str(i)+":"+str(j)+":"+str(k)+" Grunds new: "\
                                                +"Ring2: "+str(x)+" Ring3: "+str(y)\
                                                +" Wheels: "+rotor1.number+":"+rotor2.number+":"+rotor3.number\
                                                +" Ref:"+str(reflectori.typ)+"\n"\
                                                +"STECKER: "+str(steckerinfo)+"\n\n"
                                                self.q.put(strtowrite)

                                            if (steckerscoreAIC > 0.065):                                         
                                                print ("BINGO IC!!! "+str(steckerscoreAIC))
                                                print ("CHECKTHISOUT: " +text+"\n")

                                            if (steckerscoreGRAM>-2900):
                                                print ("CHECKTHISOUT: " +text+"\n")
                                                print ("BINGO GRAM!!! GRAM:"+str(steckerscoreGRAM)) # Trigram score
                                                print ("BINGO GRAM!!! ORIC:"+str(myic))   # original IC score
                                                print ("BINGO GRAM!!! BEIC:"+str(steckerscoreIC))   # IC score after first 4 plugs

                                                print ("BINGO GRAM!!! AFIC:"+str(steckerscoreAIC)+"\n\n")   # IC sore after Trigrams applied
                                            #stecker

                                                
        if (bestoftherunIC > -10000):
            strtowrite="BOTR: "+str(bestoftherunIC)+"\n"+str(botrstring)
        strtowrite=""
        self.q.put(strtowrite)                                                            
                                                        
    def steckerHillClimb(self, rotors, reflector, score):
        
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
        steckerinfo = []
        lettersToRemove = []
        topscore = score
        #allcombs = itertools.combinations(letters, 2)

        enigma = Enigma(rotors=rotors, reflector=reflector, plugboard=Plugboard({}))

        for i in range(10):
            lettersToRemove[:] = []
            plugboardtestpairs = {}
            #for sub in (itertools.combinations(letters, 2)): #all letters
            for sub in (itertools.product(mostusedletters, letters)):
                plugboardtestpairs = enigma.plugboard.wiring
                plugboardtestpairs[sub[0]] = sub[1]
                enigma.plugboard.setWiring(plugboardtestpairs)
                text = enigma.EDcrypt(self.ttc)
                myscore = self.scorer.score(text)
                print(self.scorer.icscore(text))
                
                if (myscore > topscore):
                    topscore = myscore
                    lettersToRemove = [sub[0], sub[1]]
            if (lettersToRemove):
                letters.remove(lettersToRemove[0])
                letters.remove(lettersToRemove[1])
                enigma.plugboard.wiring[lettersToRemove[0]] = lettersToRemove[1]

        return topscore, enigma.plugboard.wiring

def final(subset,q):
    #insert the scrambled text 547 char long
    scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    #scorer_mono = ngram_score('grams/german_monograms.txt')
    #scorer_bi = ngram_score('grams/german_bigrams.txt')
    scorer_tri = ngram_score('grams/german_trigrams1941.txt')
    #scorer_quad = ngram_score('grams/german_quadgrams.txt')
    scorer = scorer_tri

    crackerF = crackerParallel(scrambled,scorer,subset,q)
    crackerF.ultimate_MP_method_1()

def simpleTest(grundstellung,scrambledtext):
   
    print ("---------- simple test - Right decryption: ----------------")
    scorer_tri = ngram_score('grams/german_trigrams1941.txt')
    scorer = scorer_tri
    crackerTest = cracker(grundstellung,scrambledtext,scorer)
    crackerTest.test()
    print ("-----------------------------------------------------------")
    print ("")

def hillTest(grundstellung,scrambledtext):
    print ("-------- hill test - work in progress heuristics: ---------")
    #scrambled="KYYUGIWKSEYPQDFYPIJNTGNDIAHNBROXDIKEKPTMOUHBEJRRJPVBAOCUZRDFSAZDCNUNNMRPCCMCHJBWSTIKZIREBBVJQAXZARIYVANIJVOLDNBUMXXFNZVRQEGOYXEVVNMPWEBSKEUTJJOKPBKLHIYWGNFFPXKIEWSNTLMDKYIDMOFPTDFJAZOHVVQETNIPVZGTUMYJCMSEAKTYELPZUNHEYFCLAADYPEEXMHQMVAVZZDOIMGLERBBLATHQJIYCBSUPVVTRADCRDDSTYIXYFEAFZYLNZZDPNNXXZJNRCWEXMTYRJOIAOEKNRXGXPNMTDGKFZDSYHMUJAPOBGANCRCZTMEPXESDZTTJZGNGQRMKNCZNAFMDAXXTJSRTAZTZKRTOXHAHTNPEVNAAVUZMHLPXLMSTWELSOBCTMBKGCJKMDPDQQGCZHMIOCGRPDJEZTYVDQGNPUKCGKFFWMNKWPSCLENWHUEYCLYVHZNKNVSCZXUXDPZBDPSYODLQRLCGHARLFMMTPOCUMOQLGJJAVXHZZVBFLXHNNEJXS" 
    scorer_tri = ngram_score('grams/german_trigrams1941.txt')
    scorer = scorer_tri
    crackerTest = cracker(grundstellung,scrambledtext,scorer)
    crackerTest.testHillClimb()
    print ("-----------------------------------------------------------")

