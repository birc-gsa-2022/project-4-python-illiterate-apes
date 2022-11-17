import random

MISSISSIPPI = True

def generate_random_sequence(chainLength, alphabet):
    """
    Returns a string of length='chainLength' made up from random characters from 'alpabet'
    Arguments:
    chainLength: Expects an integer > 0 to determine the length of the string output
    alphabet: A Python list containing all valid characters
    """
    # If you try to join a non empty string with this it explodes
    output = "".join(random.choice(alphabet) for _ in range(chainLength))
    return output

def generate_same_before(chainLength, alphabet):
    """
    Returns a string of length='chainLength' made up from random characters from 'alphabet'
    For every character a random float between 0 and 1 is chosen: if it's lower than prob
    the character used for generating the previous character is used
    chainLength: Expects an integer > 0 to determine the length of the string output
    alphabet: A Python list containing all valid characters
    prob: 0.3
    """
    prob = 0.3
    output = ""
    selectedChar = random.choice(alphabet)
    for i in range(chainLength):
        if random.random()>=prob:
            selectedChar = random.choice(alphabet)
        output += selectedChar
    return output

def generate_multiple(chainLength, alphabet):
    """
    Returns a string of length='chainLength' made up from random characters from 'alphabet'
    For every character a random float between 0 and 1 is chosen: if it's lower than prob
    the character is printed n times, where n is a random value between 'minstreak' and 'maxstreak'
    (included)
    chainLength: Expects an integer > 0 to determine the length of the string output
    alphabet: A Python list containing all valid characters
    prob: A probability between 0 and 1 (0.2)
    minstreak: The minimum amount of characters that will appear in a streak (3)
    maxstreak: The maximum amount of characters that will appear in a streak (100)
    """
    prob = 0.2
    minstreak = 3
    maxstreak = 100
    output = ""
    i= 0
    while i<chainLength:
        selectedChar = random.choice(alphabet)
        if random.random()>=prob:
            output += selectedChar
            i += 1
        else:
            streakLength = random.choice(range(minstreak, maxstreak+1))
            if streakLength > chainLength-i:
                streakLength = chainLength-i
            output += "".join(selectedChar for _ in range(streakLength))
            i += streakLength
    return output

def generate_different(chainLength, alphabet):
    """
    Returns a string of length='chainLength' made up from random characters from 'alphabet'.
    It's ensured that the same character cannot appear two times in a row
    chainLength: Expects an integer > 0 to determine the length of the string output
    alphabet: A Python list containing all valid characters
    """
    output = ""
    prevChar = ""
    for _ in range(chainLength):
        selectedChar = random.choice(alphabet)
        while selectedChar==prevChar:
            selectedChar = random.choice(alphabet)
        output += selectedChar
        prevChar = selectedChar
    return output

def generate_fibonacci(chainLength, alphabet):
    match chainLength:
        case 0:
            return ""
        case 1:
            return random.choice(alphabet)

    a = random.choice(alphabet)
    b = random.choice(alphabet)
    while a==b:
        b = random.choice(alphabet)

    while len(b)<chainLength:
        a, b = b, a + b
    return b[:chainLength]

def randomRange(min, max):
    if min >= max:
        return min
    else:
        return random.choice(range(min,max))

def generate_chains(nChains, alphabet, method, minLength, maxLength):
    chains = []
    
    for i in range(nChains):
        length = randomRange(minLength, maxLength)
        chains.append(method(length, alphabet))
    
    return chains

def border_array(x: str) -> list[int]:
    """
    Construct the border array for x.

    >>> border_array("aaba")
    [0, 1, 0, 1]
    >>> border_array("ississippi")
    [0, 0, 0, 1, 2, 3, 4, 0, 0, 1]
    >>> border_array("")
    []
    >>> strict_border_array("abaabaa")
    [0, 0, 1, 1, 2, 3, 4]
    >>> border_array("abcabdabcabc")
    [0, 0, 0, 1, 2, 0, 1, 2, 3, 4, 5, 3]
    """
    if x=="":
        return []
    ba = [0] * len(x)
    for j in range(1, len(x)):
        b = ba[j - 1]
        while b > 0 and x[j] != x[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if x[j] == x[b] else 0
    return ba

# Returns the border length of the last border in the given string
def lastBorder(x):
    border = border_array(x)
    index = len(border)-1
    if index<0:
        return 0
    else:
        return border[index]

def findPattern(chain, pattern):
    patternIndexes = []
    start = 0
    while True:
        start = chain.find(pattern, start) + 1
        if start > 0:
            patternIndexes.append(start)
        else:
            return patternIndexes

def embedString(base, insertion, index):
    newChain = base[:index] + insertion + base[index+len(insertion):]
    return newChain

def adapt_chain(chain, pattern, min_matches, max_matches):
    if chain == "" or pattern == "":
        return chain

    if len(pattern)*max_matches > len(chain):
        max_matches = len(chain)//len(pattern)

    n_matches = randomRange(min_matches, max_matches)

    currentMatches = len(findPattern(pattern, chain))

    if currentMatches < n_matches:
        # Random probabilities of a match at the beginning and at the end (20% each)
        beginMatch = random.random() > 0.8
        if beginMatch:
            chain = embedString(chain, pattern, 0)
            currentMatches = len(findPattern(pattern, chain))

        if currentMatches >= n_matches: return chain

        endMatch = random.random() > 0.8
        if endMatch:
            chain = embedString(chain, pattern, len(chain)-len(pattern))
            currentMatches = len(findPattern(pattern, chain))
        
        if currentMatches >= n_matches: return chain

        # Force having two patterns in the chain with overlapping solutions if possible.
        # If not, simply put them one after the other.
        # Chance of this happening on purpose: 20%
        overlappingMatches = random.random() > 0.8
        if currentMatches>0 and overlappingMatches:
            selectedMatch = random.choice(range(currentMatches))
            borderPos = lastBorder(pattern)
            indexSelectedMatch = findPattern(chain, pattern)[selectedMatch]
            # Special case when selecting the last match (we put the pattern before the string instead of after)
            if selectedMatch == currentMatches-1:
                # Overlap before the final string
                positionModification = indexSelectedMatch-len(pattern)*2+borderPos
                chain = embedString(chain, pattern, positionModification)
            else:
                # Overlap after the string
                positionModification = indexSelectedMatch+len(pattern)+borderPos
                chain = embedString(chain, pattern, positionModification)

        currentMatches = len(findPattern(chain, pattern))
        # Chain modification loop
        rangeIndexes = range(0, 1)
        if len(chain)-len(pattern) > 0:
            rangeIndexes = range(len(chain)-len(pattern))
        while currentMatches < n_matches:
            randomIndex = random.choice(rangeIndexes)
            chain = embedString(chain, pattern, randomIndex)
            currentMatches = len(findPattern(chain, pattern))
    
    return chain


def adapt_chains(chains, patterns, min_matches, max_matches):
    if isinstance(chains, list):
        for i, chain, pattern in enumerate(chains, patterns):
            chains[i] = adapt_chain(chain, pattern, min_matches, max_matches)
    else:
        chains = adapt_chain(chains, patterns, min_matches, max_matches)
    
    return chains


def output_chains(name, startIndex, file, chains):
    if isinstance(chains, list):
        chainNames = [name+str(i+1+startIndex) for i in range(len(chains))]
        for i, chain in enumerate(chains):
            file.write(chainNames[i]+'\n')
            file.write(chain+'\n')
        return chainNames
    else:
        chainName = name+str(1+startIndex)
        file.write(chainName+'\n')
        file.write(chains+'\n')
        return [chainName]


def generate_sam(file, fasta, fastaNames, fastq, fastqNames):
    """
    Finds patterns in chromosome using a ground-truth algorithm (Python function)

    Args:
        file (fileIO): The file to append the results to in simple-sam format
        fasta (list[str]): Chromosomes to be searched
        fastaName (list[str]): Names of Chromosome
        fastq (list[str]): Patterns to look for in Chromosome
        fastqNames (list[str]): Names of patterns
    """
    if fasta == "":
        return
    out = []

    for i, pattern in enumerate(fastq):
        if pattern == "":
            continue
        for j, chain in enumerate(fasta):
            if chain == "":
                continue
            
            matches = findPattern(chain, pattern)
            for match in matches:
                out.append(f'{fastqNames[i].strip()}\t{fastaNames[j].strip()}\t{int(match)}\t{len(pattern)}M\t{pattern.strip()}')
    
    if out:
        file.write('\n'.join(out)+'\n')


def generate_test():
    ALPHABET = ['m', 'i', 's', 'p']
    GENERATION_METHODS = [generate_random_sequence, generate_same_before, generate_multiple, generate_different, generate_fibonacci]
    CHAINS_PER_TYPE = 5

    # Set seed
    random.seed(0)

    fastqNames = None
    fastqChains = []
    if MISSISSIPPI:
        fastqChains = ['iss']
    
    if True:
        NAME_FASTQ = "@read"

        MIN_FASTQ_LENGTH = 3
        MAX_FASTQ_LENGTH = 200

        for i in range(10):
            fastqChains.extend(generate_chains(1, ALPHABET, generate_random_sequence, i, i))

        # Generate fastq patterns
        for gen in GENERATION_METHODS:
            fastqChains.extend(generate_chains(CHAINS_PER_TYPE, ALPHABET, gen, MIN_FASTQ_LENGTH, MAX_FASTQ_LENGTH))

        fastq_file = open('fastq.fq', 'w')
        fastqNames = output_chains(NAME_FASTQ, 0, fastq_file, fastqChains)
        fastq_file.close()

    NAME_FASTA = "> chr"

    MIN_FASTA_LENGTH = 50
    MAX_FASTA_LENGTH = 1500

    MIN_MATCHES = 0
    MAX_MATCHES = 10

    fasta_file = open('fasta.fa', 'w')

    fasta_index = 0
    fastas = []
    nameFastas = []
    if MISSISSIPPI:
        chain = 'mississippi'
        fastas.append(chain)
        nameFastas.append(output_chains(NAME_FASTA, 0, fasta_file, chain)[0])
        fasta_index = 1

    for i in range(10):
        fastaChain = generate_chains(1, ALPHABET, generate_random_sequence, i, i)[0]
        fastaChain = adapt_chains(fastaChain, fastqChains[fasta_index], MIN_MATCHES, MAX_MATCHES)
        fastas.append(fastaChain)
        nameFastas.append(output_chains(NAME_FASTA, fasta_index, fasta_file, fastaChain)[0])
        fasta_index += 1

    # Random chains
    for gen in GENERATION_METHODS:
        fastaChains = generate_chains(CHAINS_PER_TYPE, ALPHABET, gen, MIN_FASTA_LENGTH, MAX_FASTA_LENGTH)
        for fastaChain in fastaChains:
            fastaChain = adapt_chains(fastaChain, fastqChains[fasta_index], MIN_MATCHES, MAX_MATCHES)
            fastas.append(fastaChain)
            nameFastas.append(output_chains(NAME_FASTA, fasta_index, fasta_file, fastaChain)[0])
            fasta_index += 1
    
    fasta_file.close()
    sam_file = open('sam.sam', 'w')
    fastqNames = [item.replace("@", "") for item in fastqNames]
    nameFastas = [item.replace("> ", "") for item in nameFastas]
    generate_sam(sam_file, fastas, nameFastas, fastqChains, fastqNames)
    sam_file.close()

def main():
    generate_test()

if __name__=='__main__':
    main()