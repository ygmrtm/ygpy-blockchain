from entity.Block import Block
import entity.GeneticAlgorithm




entity.GeneticAlgorithm.main(None)

def proof_of_work_ga(ind):
    value = ind.value
    print(f'> {value}')
    while ind.value >= ind.lower:
        ind.value -= 1
    return True
    # return block, computed_hash



'''
unconfirmed_transactions = ['{{}}', '{{}}']
new_block = Block(index=66, version=55,
                  previous_block='0xf9f287455c92eb330ec2ba3a41131a7ac6a26345f91796ba03fc169b38651422'
                  , merkle_root='', time=time.time()
                  , transactions=unconfirmed_transactions
                  , bits='0x000002952a453d3b8ba000000000000000000000000000000000000000000000'
                  , nonce=0)
pop = Population(population_size=500, target='0x000002952a453d3b8ba000000000000000000000000000000000000000000000'
                 , original_block=new_block, time_target=30, upper_range=100000000)

while not pop.evaluation_score_pebble():
    continue

asd = []
for i in range(0, pop.how_many_workers - 1):
    asd.append(pop.population.pop(0))

asd.sort(key=lambda x: x.value, reverse=False)

prev = 0
for phe in asd:
    phe.lower = prev
    prev = phe.value + 1

print(asd)



with ProcessPool(max_workers=pop.how_many_workers) as pool:
    functions_array = [pool.schedule(proof_of_work_ga, [asd[0]]), pool.schedule(proof_of_work_ga, [asd[1]])]
    try:
        done, not_done = wait(functions_array, timeout=10, return_when=FIRST_COMPLETED)
        for x in done:
            print(dir(x))
            print(x.result())
        for f in not_done:
            f.cancel()
    except TimeoutError:
        print("TimeoutError: aborting remaining computations")

def main():
try:
    #multiprocessing.freeze_support()

except Exception as e:
    print(e)


if __name__ == '__main__':
main()




# results = Parallel(n_jobs=pop.how_many_workers)(delayed(countdown)(ind) for ind in asd)


if __name__ == "__main__":  # I multiprocessed these 2 functions to reduce time.
time.sleep(10)


'''