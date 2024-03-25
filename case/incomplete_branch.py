def branch(s, a, b):
    t1 = 1
    if s == 0:
        t1 = a + b
    t3 = t1 * b
    return t3

# 2   t1.1 = literal(1)
# 
# 3   t2.2 = literal(UNDEFINED)
# 4   t1.3 = add(a, b)
# 5   t2.4 = literal(5)
# 
# 3   literal.5 = literal(0)
#     if.6 = eq(s, literal.5)
#     t1.7 = sel(if.6, [t1.1, t1.3])
#     t2.8 = sel(if.6, [t2.2, t2.4])
# 
# 6   t3.9 = mul(t1.7, b)
# 7   ret t3.10 = identity(t3.9)