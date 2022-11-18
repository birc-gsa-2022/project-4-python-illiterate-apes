import matplotlib.pyplot as plt
import numpy as np
import fm
import timeit



 


def main():
    
    
    #Preprocessing

    
    string = "msipiiiippi"*10
    runtimes = runtimeConstruction(string)
    x = np.array([i[0] for i in runtimes])
    y = np.array([i[1] for i in runtimes])
    plt.title("rank_table, firstIndexList and BWT construction")
    plt.xlabel("string length")
    plt.ylabel("Runtime")
    plt.plot(x,y)
    plt.show()

    #Search
    
    
    string = "msipiiiippi"*10
    runtimes = runtimeSearch(string, "msipiiiippi")
    x = np.array([i[0] for i in runtimes])
    y = np.array([i[1] for i in runtimes])
    plt.title("fm_index search algorithm")
    plt.xlabel("pattern length")
    plt.ylabel("Runtime")
    plt.plot(x,y)
    plt.show()



def runtimeConstruction(string: str):
    """
    measures runtimes for rank_table and firstIndexList construction 
    """
    runtimes = []
    

    for i in range(1,5):
        string = (string*i)+"$"
        alphadic = {a: l for l, a in enumerate(set(string))}

        x = memoryview(string.encode())
        suf = fm.getSuffixes(x)
        f = fm.radix_sort(suf)
        start = timeit.default_timer()
        bwt = [(l-1)%len(f) for l in f]
        rank_table = fm.build_rank_table(x, alphadic, bwt)
        firstIndexList = fm.getFirstIndexList(x, f, alphadic)

        stop = timeit.default_timer()
        runtimes.append([len(string*i), stop - start])

    
    return runtimes

def search(p, firstIndexList, rank_table, alphadic, f):
    if p == "":
        return
    
    left, right = 0, len(f)
    for a in reversed(p):
        if a not in alphadic:
            return
        left = firstIndexList[a] + rank_table[left][alphadic.get(a)]
        right = firstIndexList[a] + rank_table[right][alphadic.get(a)]
        if left >= right: return  # no matches

    # Report the matches
    for i in range(left, right):
        yield f[i]    

def runtimeSearch(string: str, pattern: str):
    """
    measures runtimes for fm-index search
    """
    runtimes = []
    
    string = (string*25)+"$"
    alphadic = {a: l for l, a in enumerate(set(string))}

    x = memoryview(string.encode())
    suf = fm.getSuffixes(x)
    f = fm.radix_sort(suf)
    start = timeit.default_timer()
    bwt = [(l-1)%len(f) for l in f]
    rank_table = fm.build_rank_table(x, alphadic, bwt)
    firstIndexList = fm.getFirstIndexList(x, f, alphadic)


    for i in range(0,20):
        start = timeit.default_timer()
        for match in search(pattern * i, firstIndexList, rank_table,alphadic,f):
                pass
        stop = timeit.default_timer()
        runtimes.append([len(pattern*i), stop - start])

    
    return runtimes




if __name__ == "__main__":
    main()