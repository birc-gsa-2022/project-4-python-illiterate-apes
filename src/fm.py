import argparse
import sys
import pickle
from collections import defaultdict

class BWTMatcher:
    def __init__(self, f, rank_table, firstIndexList, alphadic):
        self.rank_table = rank_table
        self.f = f
        self.firstIndexList = firstIndexList
        self.alphadic = alphadic

def main():
    argparser = argparse.ArgumentParser(
        description="FM-index exact pattern matching",
        usage="\n\tfm -p genome\n\tfm genome reads"
    )
    argparser.add_argument(
        "-p", action="store_true",
        help="preprocess the genome."
    )
    argparser.add_argument(
        "genome",
        help="Simple-FASTA file containing the genome.",
        type=argparse.FileType('r')
    )
    argparser.add_argument(
        "reads", nargs="?",
        help="Simple-FASTQ file containing the reads.",
        type=argparse.FileType('r')
    )
    args = argparser.parse_args()

    if args.p:
        print(f"Preprocess {args.genome}")
    else:
        # here we need the optional argument reads
        if args.reads is None:
            argparser.print_help()
            sys.exit(1)
        print(f"Search {args.genome} for {args.reads}")


def lower(a: str, x: str, sa: memoryview, lo: int, hi: int, offset: int) -> int:
    """Finds the lower bound of `a` at `offset` in the block defined by `lo:hi`."""
    while lo < hi:  # Search in sa[lo:hi]
        m = (lo + hi) // 2
        if x[(sa[m] + offset) % len(x)] < a: # compare at column offset in sa
            lo = m + 1
        else:
            hi = m
    return lo

def upper(a: str, x: str, sa: memoryview, lo: int, hi: int, offset: int) -> int:
    """Finds the upper bound of `a` at `offset` in the block defined by `lo:hi`."""
    return lower(chr(ord(a) + 1), x, sa, lo, hi, offset)

def search(sa, pattern, genome):
    lo, hi = 0, len(sa)
    for offset, a in enumerate(pattern):
        lo = lower(a, genome, sa, lo, hi, offset)
        hi = upper(a, genome, sa, lo, hi, offset)
    for sol in sa[lo:hi]:
        yield sol+1

def getSuffixes(x):
    """
    Gets all suffixes from a string
    """
    suffixes = [x[i:] for i in range(0, len(x))] 
    # print("list of unordered suffixes: ",suffixes) 
    return suffixes

def radix_sort(lst: list[memoryview]):
    # print("Radix sort", len(lst))
    maximum = max(lst, key = len)

    for place in range(len(maximum),0, -1):
        lst = counting_sort(lst, place - 1)
    
    lst = [len(maximum) - len(suffix) for suffix in lst]
    return lst
            

def counting_sort(lst: list[memoryview], place):
    maximum = max(lst, key = len)
    
    counts = defaultdict(list)
    for key in ["$",*sorted(maximum)]:
        counts[key] = []

    for string_index in range(len(lst)):
        if place >= len(lst[string_index]):
            counts["$"].append(lst[string_index])
        else:
            counts[lst[string_index][place]].append(lst[string_index])

    ordered = []
    for key in counts:
        ordered += counts[key]
    return ordered

def build_rank_table(x, alphadic, bwt):
    table = [[0 for _ in alphadic] for _ in range(0, len(bwt)+1)]

    for i in range(1, len(bwt)+1):        
        for j in range(0, len(alphadic)):
            table[i][j] = table[i-1][j]
        
        bwtValue = bwt[i-1]
        c = chr(x[bwtValue])

        index = alphadic.get(c)
        table[i][index] += 1

    return table

def getFirstIndexList(x, f, alphadic):
    firstIndexList = {a: -1 for a in alphadic}
    indexesFound = 0

    for i, xIndex in enumerate(f):   
        c = chr(x[xIndex])
        if firstIndexList.get(c) < 0:
            firstIndexList[c] = i
            indexesFound += 1

            if indexesFound >= len(alphadic):
                return firstIndexList
    
    return firstIndexList


def getrank(alphadic, index, c, rank_table):
    return rank_table[index][alphadic.get(c)]

def searchPattern(p, bwtMatcher):
    if p == "":
        return
    
    left, right = 0, len(bwtMatcher.f)
    for a in reversed(p):
        left = bwtMatcher.firstIndexList[a] + bwtMatcher.rank_table[left][bwtMatcher.alphadic.get(a)]
        right = bwtMatcher.firstIndexList[a] + bwtMatcher.rank_table[right][bwtMatcher.alphadic.get(a)]
        if left >= right: return  # no matches

    # Report the matches
    for i in range(left, right):
        yield bwtMatcher.f[i]

    

if __name__ == '__main__':
    alphabet = ["$", "i", "m", "p", "s"]
    alphadic = {a: i for i, a in enumerate(alphabet)}
    x = memoryview("mississippi$".encode())
    suf = getSuffixes(x)

    f = radix_sort(suf)
    bwt = [(i-1)%len(f) for i in f]

    rank_table = build_rank_table(x, alphadic, bwt)

    firstIndexList = getFirstIndexList(x, f, alphadic)

    bwtMatcher = BWTMatcher(f, rank_table, firstIndexList, alphadic)

    file = open("fasta.fa.dat", "wb")    
    pickle.dump([bwtMatcher], file)

    file = open("fasta.fa.dat", "rb")    
    bwtMatcher = pickle.load(file)

    print(bwtMatcher[0])

    matches = list(searchPattern("i", bwtMatcher[0]))
    print("Matches: ")
    for m in matches:
        print(m)

    # print(getrank(alphadic, 3, "a", rank_table))
    

    # main()
