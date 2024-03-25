def branch(s, a, b):
    r = 0
    if s == 0:
        r = a + b
    elif s == 1:
        r = a - b
    else:
        r = a * b
    return r