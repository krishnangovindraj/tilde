import random

N_PEOPLE = 30
E_LINKS_PER_PERSON = 3

GROUPS_MUSIGMA = [(500,50), (2000,200)]
P_OUTLIER = 0.03

def gen_person(i):
    group = int( random.random() * len(GROUPS_MUSIGMA) )
    name = 'p_%d_%d'%(i, group)
    wealth = int(random.gauss(GROUPS_MUSIGMA[group][0], GROUPS_MUSIGMA[group][1]))
    
    return (name, wealth, group)


people = [gen_person(i) for i in range(N_PEOPLE)]
p_by_group = {i: [] for i in range(len(GROUPS_MUSIGMA))}
for p in people:
    p_by_group[p[2]].append(p)

links = set()
last_group_index = len(GROUPS_MUSIGMA)-1
n_links = N_PEOPLE * E_LINKS_PER_PERSON
outlier_count = 0
outliers = set()
while len(links) < n_links:
    g0 = random.randint(0, last_group_index)
    g1 = random.randint(0, last_group_index) if random.random() < P_OUTLIER else g0
    link = (random.choice(p_by_group[g0])[0], random.choice(p_by_group[g1])[0])
    links.add( link )
    if g1 != g0:
        outliers.add(link)
    outlier_count += 0 if g1==g0 else 1
    

from sys import stderr as sys_stderr
print("%% Generated %d links with %d anomalies"%(len(links), outlier_count))

print("% People:") # Why do i not have to escape these? Why is python weird?
for p in people:
    print("person(%s, dummyclass)."%(p[0]))

print("\n\n% Wealth:")
for p in people:
    print("wealth(%s, %d)."%(p[0], p[1]))

print("\n\n% Links:")
for l in links:
    comment = 'outlier' if l in outliers else ''
    print("friends(%s,%s)."%(l[0], l[1]))

print("\n\n% end")
