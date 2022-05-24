import copy
import os
import random
import time
import sys
from concurrent.futures import TimeoutError
from concurrent.futures import wait, FIRST_COMPLETED, ALL_COMPLETED
import multiprocessing

from joblib import Parallel, delayed
from pebble import ProcessPool


class Phenotype:
    def __init__(self, value, score=0):
        self.value = value
        self.score = score
        self.how_many_kids = 0
        self.how_many_gens = 1
        self.how_many_muts = 0

    def __str__(self):
        return "value:{} score:{} active_gens:{} kids:{} mutations:{}".format(self.value,
                                                                              self.score,
                                                                              self.how_many_gens,
                                                                              self.how_many_kids,
                                                                              self.how_many_muts)

    def value_to_binary(self):
        return bin(self.value)


class Population:

    def __init__(self, population_size=10, lower_range=0, upper_range=50000, population=None,
                 target="0x00000000ffff0000000000000000000000000000000000000000000000000000", original_block=None,
                 generation_target=None, time_target=None):
        if population is None:
            population = []
        self.init_time = time.time()
        self.original_block = original_block
        self.random_threshold = 0.2
        self.population_size = population_size
        self.generation = 0
        self.target = target
        self.lower_range = lower_range
        self.upper_range = upper_range
        self.population = population
        self.generation_target = generation_target
        self.time_target = time_target
        self.how_many_workers = int(os.cpu_count())
        if "sched_getaffinity" in dir(os):
            self.how_many_workers = len(os.sched_getaffinity(0))
        random.seed(self.init_time)
        if population_size > 0 and len(population) == 0:
            self.initial_population()

    def initial_population(self):
        random_list = random.sample(range(self.lower_range, self.upper_range), self.population_size)
        self.generation = 1
        for number in random_list:
            self.population.append(Phenotype(number))

    def statistics(self):
        self.population.sort(key=lambda x: x.value, reverse=True)
        max_value = self.population[0].value
        self.upper_range = max_value if max_value >= self.upper_range else self.upper_range
        print('gen:{}|range[{}-{}]|elapsed:{}secs'.format(self.generation, self.lower_range, self.upper_range
                                                          , str(time.time() - self.init_time)))

    def evaluation_score(self):
        new_generation = []

        evaluated_gen = Parallel(n_jobs=self.how_many_workers)(delayed(self.evaluation)(ind) for ind in self.population)
        evaluated_gen.sort(key=lambda x: x.score, reverse=False)
        last_best_phe = int(len(evaluated_gen) / 2)
        moms_and_dads = evaluated_gen[0:last_best_phe]
        golden_phe = evaluated_gen[0]

        while len(moms_and_dads):
            mom = moms_and_dads.pop(0)
            dad = moms_and_dads.pop() if len(moms_and_dads) else golden_phe
            sis, bro = self.crossover(mom, dad)
            new_generation.append(mom)
            new_generation.append(sis)
            new_generation.append(dad)
            new_generation.append(bro)
        new_generation = new_generation[0:self.population_size]

        results = Parallel(n_jobs=self.how_many_workers)(delayed(self.mutation)(ind) for ind in new_generation)
        results = Parallel(n_jobs=self.how_many_workers)(delayed(self.spartan_rule)(ind) for ind in results)
        '''Increasing the Generation'''
        self.generation += 1
        self.population = Parallel(n_jobs=self.how_many_workers)(delayed(self.increase_gen)(ind) for ind in results)
        return self.stop()

    def evaluation_score_pebble(self):
        new_generation = []
        with ProcessPool(max_workers=self.how_many_workers) as pool:
            f1 = pool.schedule(self.evaluation, [self.population[0]])
            f2 = pool.schedule(self.evaluation, [self.population[1]])
            farray = [pool.schedule(self.evaluation, [self.population[0]]), pool.schedule(self.evaluation, [self.population[1]])]
            try:
                done, not_done = wait(farray, timeout=10, return_when=ALL_COMPLETED)
                for x in done:
                    print(x.result())
                for f in not_done:
                    print("canceling")
                    f.cancel()
            except TimeoutError:
                print("TimeoutError: aborting remaining computations")
        return self.stop()

    def evaluation(self, ind):
        if self.original_block:
            tmp_block = copy.deepcopy(self.original_block)
            tmp_block.nonce = ind.value
            ind.score = int(self.target, 16) - int('0x' + tmp_block.compute_hash(), 16)
        else:
            ind.score = random.random() * 100
        return ind

    @staticmethod
    def crossover(mom, dad):
        mom_str = mom.value_to_binary()
        dad_str = dad.value_to_binary()
        if len(mom_str) > len(dad_str):
            longest_string = len(mom_str) - 2
            dad_str = dad_str[:2] + dad_str[3:].zfill(longest_string)
        else:
            longest_string = len(dad_str) - 2
            mom_str = mom_str[:2] + mom_str[3:].zfill(longest_string)

        bit_to_cross = random.sample(range(2, len(mom_str)), 1)[0]
        sis_str = mom_str[:bit_to_cross] + dad_str[bit_to_cross:]
        bro_str = dad_str[:bit_to_cross] + mom_str[bit_to_cross:]
        sis = Phenotype(int(sis_str, 2))
        bro = Phenotype(int(bro_str, 2))
        mom.how_many_kids += 1
        dad.how_many_kids += 1
        return sis, bro

    def mutation(self, ind):
        if random.random() < self.random_threshold:
            if random.random() < self.random_threshold:
                ind.value <<= 1
                # print('mutation {} to {} '.format(ind.value >> 1, ind.value))
            else:
                binary_str = ind.value_to_binary()
                bit_to_mutate = random.sample(range(2, len(binary_str)), 1)[0]
                binary_new = binary_str[:bit_to_mutate] + ('0' if binary_str[bit_to_mutate] == '1' else '1') \
                             + binary_str[bit_to_mutate + 1:]
                ind.value = int(binary_new, 2)
                # print('mutation{} to{} bit_mutated {}'.format(int(binary_str, 2), int(binary_new, 2), bit_to_mutate))
            ind.how_many_muts += 1
            ind.how_many_gens = 1
        return ind

    def spartan_rule(self, ind):
        return ind if ind.value > 0 else Phenotype(int(random.random() * self.upper_range))

    @staticmethod
    def increase_gen(ind):
        ind.how_many_gens += 1
        return ind

    def stop(self):
        stop = False
        if 0 > self.population[0].score >= -10000000:
            stop = True
        elif self.generation_target:
            stop = self.generation >= self.generation_target
        elif self.time_target:
            stop = (time.time() - self.init_time) >= self.time_target
        if stop:
            self.statistics()
            self.population.sort(key=lambda x: x.how_many_kids + x.how_many_gens, reverse=True)

        return stop
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking


def main(new_node, time_deadline):
    multiprocessing.freeze_support()
    pop = Population(population_size=500, target=new_node.bits
                 , original_block=new_node, time_target=time_deadline, upper_range=100000000)

    while not pop.evaluation_score_pebble():
        continue



if __name__ == '__main__':
    multiprocessing.freeze_support()
    main(sys.argv[1:])
