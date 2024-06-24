import timeit

def execute_mips_code(a, b, d, e, g, h):
    c = None
    f = None

    if a > b:
        if d > e:
            c = d + e
        else:
            f = g - h
    else:
        f = g + h

    return c, f

def predicate_combining(a, b, d, e, g, h):
    temp_c = d + e
    temp_f1 = g - h
    temp_f2 = g + h
    
    c = None
    f = None
    
    if a > b:
        c = temp_c
    
    if a <= b:
        if d >= e:
            f = temp_f2
        else:
            f = temp_f1
    
    return c, f

def test_performance():
    a, b, d, e, g, h = 10, 5, 8, 4, 6, 7
    
    # Measure execution time for original logic
    original_time = timeit.timeit(lambda: execute_mips_code(a, b, d, e, g, h), number=100000)
    
    # Measure execution time for predicate combining logic
    predicate_time = timeit.timeit(lambda: predicate_combining(a, b, d, e, g, h), number=100000)
    
    print(f"Original Logic Execution Time: {original_time} seconds")
    print(f"Predicate Combining Execution Time: {predicate_time} seconds")

if __name__ == "__main__":
    test_performance()