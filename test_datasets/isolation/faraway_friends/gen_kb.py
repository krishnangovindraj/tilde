import random

N_PEOPLE = 40
E_LINKS_PER_PERSON = 5
P_OUTLIER = 0.015

geography = {'asia':  ['india', 'china', 'japan', 'iran', 'kazakhstan'],
'europe': ['belgium', 'france', 'netherlands', 'italy', 'spain', 'germany']}
geo_keys = list(geography.keys())


def gen_person(i):
    continent = geo_keys[int( random.random() * len(geography) )]
    country = random.choice(geography[continent])
    name = 'p_%s_%s'%(i, country)
    
    return (name, country, continent)


people = [gen_person(i) for i in range(N_PEOPLE)]
p_by_group = {k: [] for k in geography}
for p in people:
    p_by_group[p[2]].append(p)

links = set()
n_links = N_PEOPLE * E_LINKS_PER_PERSON
outlier_count = 0
outlier_links = set()
while len(links) < n_links:
    g0 = random.choice(geo_keys)
    g1 = g0
    if random.random() < P_OUTLIER:
        while g1 == g0:
            g1 = random.choice(geo_keys)
        
    
    p0, p1 = random.choice(p_by_group[g0]), random.choice(p_by_group[g1])
    while p0[1] == p1[1]:
        p0, p1 = random.choice(p_by_group[g0]), random.choice(p_by_group[g1])  
    # Fun side-effect: Without this check, we end up generating a lot of people who are outliers because ...
    #   they're friends with someone in their own country. What weirdos \(-_-)/
    # A better way to fix this would be to increase the number of countries per continent
    links.add( (p0[0], p1[0]) )

    if g1 != g0:
        outlier_links.add((p0[0], p1[0]))  
        outlier_count +=1

from sys import stderr as sys_stderr
print("%% Generated %d links with %d anomalies"%(len(links), outlier_count))

print("% People:") # Why do i not have to escape these? Why is python weird?
for p in people:
    print("person(%s, dummyclass)."%(p[0]))

print("\n\n% Nationality:")
for p in people:
    print("nationality(%s, %s)."%(p[0], p[1]))

print("\n\n% Friends:")
for l in links:
    comment = 'outlier' if l in outlier_links else ''
    print("friends(%s,%s). %% %s"%(l[0], l[1], comment))

# print("\n\n% Geography background:")
# for continent in geography:
# 	for country in geography[continent]:
# 		print("continent(%s,%s)."%(country, continent))


print("\n\n% end")
