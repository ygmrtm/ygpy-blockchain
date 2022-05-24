from GeneticAlgorithm import Population
import time as t

# print('population_size|generation|delta|lower_range|upper_range|min_phe|max_phe|size_already_done|elapsed_time')


def x(a, b, c, x, y, z, gen):
    '''increase pz increase ur'''
    for pz in range(a, b, c):
        for ur in range(x, y, z):
            pop = Population(population_size=pz, upper_range=ur)
            # print('-' * 20)
            while pop.generation < gen:
                # print('Running generation...' + str(pop.generation))
                pop.evaluation_score()
            pop.statistics()
            pop.community.clear()
            pop.already_done.clear()
            del pop
'''
initial = t.time()
x(20, 201, 50, 1000, 100001, 10000, 50)
print(t.time() - initial)
initial = t.time()
x(20, 201, 50, 1000, 100001, 10000, 100)
print(t.time() - initial)
initial = t.time()
x(201, 20, -50, 1000, 100001, 10000, 50)
print(t.time() - initial)
initial = t.time()
x(201, 20, -50, 1000, 100001, 10000, 100)
print(t.time() - initial)
initial = t.time()
x(201, 20, -50, 100001, 1000, -10000, 50)
print(t.time() - initial)
initial = t.time()
x(201, 20, -50, 100001, 1000, -10000, 100)
print(t.time() - initial)
initial = t.time()
x(20, 201, 50, 100001, 1000, -10000, 50)
print(t.time() - initial)
initial = t.time()
x(20, 201, 50, 100001, 1000, -10000, 100)
print(t.time() - initial)
initial = t.time()
'''
pop = Population(population_size=60, lower_range=0, upper_range=500000, time_target=60)
while not pop.evaluation_score():
    continue

for inf in pop.population[0:5]:
    print(inf)
