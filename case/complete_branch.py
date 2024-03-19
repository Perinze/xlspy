def branch(s, a, b):
    if s == 0:
        return a + b
    elif s == 1:
        return a - b
    else:
        return a * b