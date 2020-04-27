# raise NotImplementedError("Neither of these work great")

from random import gauss
U_X, SIG_X = 0.0, 20.0
U_Y, SIG_Y = 0.0, 10.0

def gen_point(u_x, sig_x, u_y, sig_y):
    return ( gauss(u_x, sig_x), gauss(u_y, sig_y) )

points = []
classes = {}


# N_POINTS = 20
# points = [gen_point(U_X, SIG_X, U_Y, SIG_Y) for _ in range(N_POINTS)]
# classes = {}
# x_sorted = sorted(points)
# classes[x_sorted[0]] = 'pos'
# classes[x_sorted[-1]]= 'pos'
# y_sorted = sorted(points, key=lambda x: x[1])
# classes[y_sorted[0]] = 'pos'
# classes[y_sorted[-1]] = 'pos'

# # Manhattan would be cheating
# euclid_sorted = sorted(points, key=lambda x: ((x[0]-U_X)/SIG_X) ** 2 + ((x[1]-U_Y)/SIG_Y)**2 )
# classes[euclid_sorted[-1]] = 'pos'
# classes[euclid_sorted[-2]] = 'pos'
# classes[euclid_sorted[-3]] = 'pos'
# classes[euclid_sorted[-4]] = 'pos'


N_OUTLIERS, N_TOTAL = 10, 40
N_REGULARS = N_TOTAL-N_OUTLIERS
INLIER_SIGMA_FACTOR, OUTLIER_SIGMA_FACTOR = 1.0, 2.0

def is_outlier(p):
    return abs(p[0]-U_X)/SIG_X > OUTLIER_SIGMA_FACTOR or abs(p[1]-U_Y)/SIG_Y > OUTLIER_SIGMA_FACTOR

def is_inlier(p):
    return abs(p[0]-U_X)/SIG_X < INLIER_SIGMA_FACTOR and abs(p[1]-U_Y)/SIG_Y < INLIER_SIGMA_FACTOR


def gen_point(u_x, sig_x, u_y, sig_y):
    return ( gauss(u_x, sig_x), gauss(u_y, sig_y) )

outliers, regulars =  [], []
while len(outliers) < N_OUTLIERS or len(regulars) < N_REGULARS:
    p = gen_point(U_X, SIG_X, U_Y, SIG_Y)
    if is_outlier(p):
        if len(outliers) < N_OUTLIERS:
            outliers.append(p)
            classes[p] = 'pos'
    elif is_inlier(p):
        if len(regulars) < N_REGULARS:
            regulars.append(p)
            classes[p] = 'neg'

points = outliers + regulars

pos_examples = [e for e in points if classes.get(e,None)=='pos']
neg_examples = [e for e in points if classes.get(e,None)!='pos']
import matplotlib.pyplot as plt
import sys
plt.scatter(list(map(lambda x:x[0], pos_examples)), list(map(lambda x:x[1],pos_examples) ), color = 'red' )
plt.scatter(list(map(lambda x:x[0], neg_examples)), list(map(lambda x:x[1],neg_examples) ), color = 'blue' )
plt.show()


for p in points:
    print("gaussian(%.1f,%.1f, %s)."%(p[0],p[1], classes.get(p, 'neg')))
