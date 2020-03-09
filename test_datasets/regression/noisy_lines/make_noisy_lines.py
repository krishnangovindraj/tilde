from random import randint, normalvariate, shuffle
N_LINES = 4
N_POINTS_PER_LINE_RANGE = (4,7)
X_RANGE=(2,50)
SIGMA = 1


xy = []
for l in range(N_LINES):
	line_x = randint( X_RANGE[0], X_RANGE[1] )
	for _ in range(randint(N_POINTS_PER_LINE_RANGE[0], N_POINTS_PER_LINE_RANGE[1])):
		xy.append((line_x, normalvariate(line_x**2, SIGMA))) # eek, non-gaussian noise

shuffle(xy)

preds = []
kb = []

for i in range(len(xy)):
	id = i+1
	#preds.append("noisy_line(%d, %f)."%(id, xy[i][1]))
	#kb.append("line_x(%d,%d)."%(id, xy[i][0]))
	kb.append("noisy_line(%d, %d, %f)."%(id, xy[i][0], xy[i][1]))

for p in preds:
	print(p)

print()

for k in kb:
	print(k)
