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


if __name__ == '__main__':
    x = memoryview("abaaba$".encode())
    suf = getSuffixes(x)

    f = radix_sort(suf)
    bwt = [(i-1)%len(f) for i in f]

    print(f, bwt)

    # main()
