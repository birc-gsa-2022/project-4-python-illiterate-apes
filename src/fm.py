import argparse
import sys


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
        if x[sa[m] + offset % len(x)] < a: # compare at column offset in sa
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
    return

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
    counts = dict.fromkeys(["$",*sorted(maximum)],[])
    for string_index in range(len(lst)):
        if place >= len(lst[string_index]):
            counts["$"] = [*counts["$"], lst[string_index]]
            
        else:
            counts[lst[string_index][place]] = [*counts[lst[string_index][place]], lst[string_index]]

    ordered = []
    for key in counts:
        ordered += counts[key]
    return ordered

def build_rank_table(x, alphadic, bwt):
    counts = {a: 0 for a in alphadic}
    table = [[0 for _ in alphadic] for _ in range(0, len(bwt)+1)]

    for i in range(1, len(bwt)+1):        
        for j in range(0, len(alphadic)):
            table[i][j] = table[i-1][j]
        
        bwtValue = bwt[i-1]
        c = chr(x[bwtValue])

        # Add the count
        counts[c] += 1

        index = alphadic.get(c)
        table[i][index] += 1

    return table, counts

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

def searchPattern(x, p, f, l, rank_table, firstIndexList, countTable, alphadic):
    firstRank = -1
    nRanks = 0

    if p == "":
        return
    
    if len(p) == 1:
        # TODO: Do this
        return

    print(firstIndexList) # {'$': 0, 'a': 1, 'b': 5}
    # First case
    if True:
        c = p[len(p)-1] # b
        upperBound = firstIndexList.get(c)
        lowerBound = upperBound+countTable.get(c)

        for j in range(upperBound, lowerBound):
            print (chr(x[l[j]]), p[len(p)-2], sep=" == ")
            if chr(x[l[j]]) == p[len(p)-2]:
                if firstRank < 0:
                    firstRank = getrank(alphadic, j, p[len(p)-2], rank_table)
                nRanks += 1

    for i in range(len(p)-2, 0, -1):
        if firstRank < 0:
            print("Nothing :(")
            return

        # Look in f
        c = p[i]
        upperBound = firstIndexList.get(c)+firstRank
        lowerBound = upperBound+nRanks
        
        firstRank = -1
        nRanks = 0
        for j in range(upperBound, lowerBound):
            if chr(x[l[j]]) == p[i-1]:
                if firstRank < 0:
                    firstRank = getrank(alphadic, j, p[i-1], rank_table)
                nRanks += 1

    # Handle 0 case: success
    print(firstRank, nRanks)  # 2 2
    firstSolution = firstIndexList.get(p[0])+firstRank
    for i in range(0, nRanks):
        yield f[i+firstSolution]

    

if __name__ == '__main__':
    alphabet = ["$", "a", "b"]
    alphadic = {a: i for i, a in enumerate(alphabet)}
    x = memoryview("abaaba$".encode())
    suf = getSuffixes(x)

    f = radix_sort(suf)
    bwt = [(i-1)%len(f) for i in f]

    rank_table, countTable = build_rank_table(x, alphadic, bwt)

    firstIndexList = getFirstIndexList(x, f, alphadic)
    
    matches = list(searchPattern(x, "ba", f, bwt, rank_table, firstIndexList, countTable, alphadic))
    print("Matches: ")
    for m in matches:
        print(m)

    # print(getrank(alphadic, 3, "a", rank_table))
    

    # main()
