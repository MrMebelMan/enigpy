from string import ascii_uppercase

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
        #for letter in pomlist:
        #    self.mapping.update({letter:pomi})
        #    pomi+=1

        mapping=dict((c, ord(c) - 65) for c in ascii_uppercase)
            
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

            stepagain1=False # 2 notches on VI VII VIII --- moving slowest rotor
            stepagain2=False # 2 notches on VI VII VIII --- moving middle rotor
            
            # doublestepagain2=False # magic

            if (self.rotor3.step==13 and r3pos==26): 
                stepagain2=True

            if (self.rotor2.step==13 and r2pos+1==26): 
                stepagain1=True 
            
            if (r3pos==self.rotor3.step or stepagain2==True) or r2pos+1==self.rotor2.step or stepagain1==True: # or (double stepping of middle rotor)
                r2pos+=1
                #print("stepping middle")

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
            scrambled+=onecipher

        return scrambled
