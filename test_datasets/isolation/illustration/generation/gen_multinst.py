N_REGULAR = 50
N_OUTLIER = 2
N_VARIABLES = 6
FORMULA = [ [2,4,-6] , [3, -5] ]
INVERT = False

N_INST_PER_EXAMPLE = 7

from gen_dnf import DNFGenerator
from dataset_writer import DatasetWriter
from random import sample, shuffle

dgen = DNFGenerator(N_VARIABLES, FORMULA)

goodconj, badconj = dgen.generate_all()

if INVERT:
    regulars = [ sample(goodconj, N_INST_PER_EXAMPLE) for _ in range(N_REGULAR)]
    outliers = [ (sample(goodconj, N_INST_PER_EXAMPLE-1) + sample(badconj, 1)) for _ in range(N_OUTLIER)]
else:
    regulars = [ sample(badconj, N_INST_PER_EXAMPLE) for _ in range(N_REGULAR)]
    outliers = [ (sample(badconj, N_INST_PER_EXAMPLE-1) + sample(goodconj, 1)) for _ in range(N_OUTLIER)]


from math import ceil, log10
padding = ceil(log10(N_REGULAR + N_OUTLIER))
key_str = lambda x: dgen.binary2intstr(x, padding=padding) 

ds_dict = { ('e%s'%str(i).zfill(padding)) : val_list for i,val_list in enumerate(regulars) }
ds_dict.update({('o%s'%str(i).zfill(padding)) : val_list for i,val_list in enumerate(outliers) })

ds_writer = DatasetWriter()

print("%% %d regular and %d outliers ; total = %d"%(len(regulars), len(outliers), len(ds_dict)))

from sys import stdout
ds_writer.write_kb(ds_dict, file=stdout)