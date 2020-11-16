# Еще одна имплементация цепей Маркова от 2020.09.24
import re, sys, json, getopt, random

wordslist = []
chain = []
lastel = None # pointer to last element in chain

def split_str(s):
    s = s.lower()
    s = re.sub('[,.;]+', ' dot ', s)
    s = re.sub('[^а-яёa-z]+', ' ', s)
    return tuple(filter(None, s.split(' ')))

def markov(inpu, lnum=0, wnum=0):
    global wordslist, chain, lastel
    with open(inpu, 'r', encoding='utf8') as f:
        wi = 0
        for line in f:
            if len(line) <= 1: continue
            words = split_str(line)
            for w in words:
                wi += 1
                if lnum > 0 and wi % lnum == 0:
                    print(f'{wi} words read from file.')
                if wnum > 0 and wi > wnum:
                    print('Max words num reached.')
                    return
                if w in wordslist:
                    ci = wordslist.index(w) # find word index
                    lastel.append(ci)       # append index in chain
                    lastel = chain[ci]      # set as last element
                else:
                    ci = len(wordslist)          # create index
                    wordslist.append(w)          # create word
                    lastel and lastel.append(ci) # append index in chain
                    lastel = []                  # create chain element
                    chain.append(lastel)         # append element in chain

def gen(coun=64):
    s = ''
    i = random.randint(1, len(chain)) - 1
    for _ in range(coun):
        s += wordslist[i] + ' '
        try:
            i = random.choice(chain[i])
        except:
            i = random.randint(1, len(chain)) - 1
    return s[:-1]

def load_data(geni):
    global wordslist, chain
    with open(geni, 'r') as f:
        d = json.load(f)
        wordslist = d['wordslist']
        chain = d['chain']

def save_data(outp):
    with open(outp, 'w') as f:
        json.dump({ 'wordslist':wordslist, 'chain':chain }, f)

def main(argv):
    inpu = None # (in) dataset path
    outp = None # (out) data path
    lnum = 1000 # words num after wich status will be printed
    wnum = 0    # words num after wich data generation will be terminated
    geni = None # (in) data path
    coun = 64   # words num wich will be generated
    try:
        opts, args = getopt.getopt(argv, 'i:o:l:w:g:c:')
        for opt, arg in opts:
            if   opt in ('-i'): inpu = str(arg)
            elif opt in ('-o'): outp = str(arg)
            elif opt in ('-l'): lnum = int(arg)
            elif opt in ('-w'): wnum = int(arg)
            elif opt in ('-g'): geni = str(arg)
            elif opt in ('-c'): coun = int(arg)
        if not (inpu and outp or geni): raise Exception()
    except:
        print('Usage: markov.py -i <inputfile> -o <outputfile> [-w <wordsnum> -l <lognum>]')
        print('              OR -g <datafile> [-c <wordscount>]')
        exit(2)
    if geni:
        load_data(geni)
        print(gen(coun))
    else:
        markov(inpu, lnum, wnum)
        save_data(outp)

if '__main__' == __name__:
   main(sys.argv[1:])
