import timeit

def predicated_execution(a, b, d, e, g, h):
    temp_c = d + e
    temp_f = g + h
    
    if a > b:
        c = temp_c
        f = None
    else:
        c = None
        f = temp_f
    
    return c, f

def original_mips_code(a, b, d, e, g, h):
    c = None
    f = None

    if a > b:
        c = d + e
    else:
        f = g + h

    return c, f

def test_performance():
    a, b, d, e, g, h = 10, 5, 3, 4, 6, 7
    
    # Measure execution time for predicated execution logic
    predicated_time = timeit.timeit(lambda: predicated_execution(a, b, d, e, g, h), number=100000)
    
    # Measure execution time for original MIPS code logic
    original_time = timeit.timeit(lambda: original_mips_code(a, b, d, e, g, h), number=100000)
    
    print(f"Predicated Execution Time: {predicated_time} seconds")
    print(f"Original MIPS Code Execution Time: {original_time} seconds")

if __name__ == "__main__":
    test_performance()