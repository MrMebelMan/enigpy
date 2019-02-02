#local
import cracker

#global
import itertools
import multiprocessing
from datetime import datetime

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
    noteating=1
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
            job = pool.apply_async(cracker.final, (subset,q))
             #p=multiprocessing.Process(target=multi7, args=(subset,))
                #jobs.append(p)
                #p.start()
            jobs.append(job)
    else:
        for subset in range(26):
            job = pool.apply_async(cracker.finalRing, (subset,q))
            jobs.append(job)
            
    for job in jobs: 
        job.get()
    
    q.put('kill')
    pool.close()
    pool.join()