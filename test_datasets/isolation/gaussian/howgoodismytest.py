import random
p = 0.25
x = 7
n = 12

trials = 500
outcomes = [ 1 if sum([1 if random.random() < p else 0 for _i in range(n)]) >= x else 0  for _j in range(trials) ]

# How likely is a success if the isolation forest didn't do anything.
print( float(sum(outcomes))/trials )