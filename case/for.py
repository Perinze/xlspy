def loop(a, b):
    sum = a
    for i in range(8):
        sum = (sum + b) * a
    return sum