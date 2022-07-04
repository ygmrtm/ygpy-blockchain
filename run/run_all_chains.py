#!/usr/bin/python3
try:
    import pickle
    import os
    import sys
    import getopt
    import json
    import multiprocessing
    import random
    import time
    import copy
    from todoist_api_python.api import TodoistAPI
    from entity.Blockchain import Blockchain
    from jproperties import Properties
    from concurrent.futures import TimeoutError
    from concurrent.futures import wait, FIRST_COMPLETED, ALL_COMPLETED
    from pebble import ProcessPool
    from entity.GeneticAlgorithm import Population
except ImportError as exc:
    raise exc

path = "../chains_by_genblock_hash"  # path of the directory


def check_arguments(argv):
    input_action = input_genesis = genetic_algorithm = None
    usage = 'run_all_chains.py -a [new|load] -g [hash_code_of_genesis] -x (for Genetic Algorithm)'
    try:
        opts, args = getopt.getopt(argv, "ha:g:x")
        for opt, arg in opts:
            if opt == '-h':
                print(usage)
                sys.exit()
            elif opt in ("-a", "--action"):
                input_action = arg
            elif opt == "-g":
                input_genesis = arg
                input_action = 'load'
            elif opt == "-x":
                genetic_algorithm = True
    except Exception:
        print('wrong param', usage)
        sys.exit(2)

    if input_action not in ('load', 'new') \
            or (input_genesis and len(input_genesis) != 64):
        print('wrong values in params', usage)
        sys.exit()

    print('Action to perform is:', input_action
          , ('this chain hash: ' + input_genesis if input_genesis else '')
          , ('proof of work with Genetic Algorithm' if genetic_algorithm else ''))
    return input_action, input_genesis, genetic_algorithm


def load_properties():
    configs = Properties()
    with open('../blockchain.properties', 'rb') as read_prop:
        configs.load(read_prop)
    return configs


def get_property(key):
    configs = load_properties()
    return configs[key].data


def load_chains(_action, _chain_hash):
    loaded_chains = []
    try:
        if len(os.listdir(path)) == 0 or _action == 'new':
            bc_reconstructed = Blockchain()
            loaded_chains.append(bc_reconstructed)
        elif _chain_hash:
            f = os.path.join(path, _chain_hash + '.pickle')
            if os.path.isfile(f):
                with open(f, "rb") as infile:
                    bc_reconstructed = pickle.load(infile)
                    loaded_chains.append(bc_reconstructed)
            else:
                print("Not a valid HASH to load {}".format(_chain_hash))
        else:
            for filename in os.listdir(path):
                f = os.path.join(path, filename)
                if os.path.isfile(f):
                    print("Loading " + f)
                    with open(f, "rb") as infile:
                        bc_reconstructed = pickle.load(infile)
                        loaded_chains.append(bc_reconstructed)
    except Exception as inst:
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)
    finally:
        return loaded_chains


def upgrade_chain():
    print('Upgrading the chain')
    loaded_chains = load_chains('load', '')
    new_chains = []
    for chain in loaded_chains:
        new_chain = Blockchain()
        new_chain.unconfirmed_transactions = chain.unconfirmed_transactions
        new_chain.chain = chain.chain
        new_chain.current_target = chain.current_target
        new_chain.version = chain.version
        new_chains.append(new_chain)
    for zxc in new_chains:
        print(zxc.new_block())
        save_chains(zxc)
    sys.exit()


def save_chains(_chain):
    print('Saving ' + _chain.chain[0].hash)
    with open('{}/{}.pickle'.format(path, _chain.chain[0].hash), "wb") as outfile:
        pickle.dump(_chain, outfile)


def get_chain(blockchain):
    chain_data = []
    for block in blockchain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


def get_todoist_api():
    return TodoistAPI(get_property('TODOIST_APITOKEN'))


def get_project(project_id):
    project = None
    try:
        api = get_todoist_api()
        project = api.get_project(project_id=project_id)
    except Exception as error:
        print(error)
    return project


def get_tasks(project_id, section_id):
    try:
        api = get_todoist_api()
        tasks = api.get_tasks(project_id=project_id, section_id=section_id)
        return tasks
    except Exception as error:
        print(error)
        raise


def get_pending_tasks():
    _pending_tasks = get_tasks(get_property('TODOIST_PROJECT_ID'), get_property('TODOIST_SECTION_ID'))
    print(f'There are {len(_pending_tasks)} pending transactions (whole universe)')
    _pending_tasks.sort(key=lambda x: x.content and x.priority, reverse=False)
    return _pending_tasks


def add_comment(task_id, content):
    try:
        api = get_todoist_api()
        comment = api.add_comment(
            content=content,
            task_id=task_id
        )
        return comment
    except Exception as error:
        print(error)
        raise


def update_task(task_id, label_ids):
    try:
        api = get_todoist_api()
        label_ids.append(int(get_property('TODOIST_MINED_LABEL_ID')))
        is_success = api.update_task(task_id=task_id, due_string="today", label_ids=label_ids)
        return is_success
    except Exception as error:
        print(error)
        raise


def simple_work():
    return main_chain.mine(expected_time_per_block)


def hard_work():
    _computed_hash = ''
    new_block = main_chain.new_block()
    pop = Population(population_size=500, target=new_block.bits
                     , original_block=new_block, time_target=expected_time_per_block / 10, upper_range=100000000)
    how_many = pop.how_many_workers
    print(f'Genetic Algorithm Running, waiting for {pop.time_target} secs')
    while not pop.evaluation_score():
        continue
    asd = []
    for i in range(0, how_many):
        asd.append(pop.population.pop(0))

    asd.sort(key=lambda x: x.value, reverse=False)

    with ProcessPool(max_workers=how_many) as pool:
        prev = 0
        ind = 1
        functions_array = []
        for phe in asd:
            phe.lower = prev
            phe.up_down = 'down' if ind != how_many else 'up'
            prev = phe.value + 1
            phe.value = phe.value if ind != how_many else phe.lower
            ind += 1
            functions_array.append(pool.schedule(parallel_work, [copy.deepcopy(new_block), phe, main_chain, random.random() * 100]))
        try:
            done, not_done = wait(functions_array, timeout=expected_time_per_block * 1.5, return_when=FIRST_COMPLETED)
            for f in done:
                new_block = f.result()[0]
                _computed_hash = f.result()[1]
            for f in not_done:
                print("canceling")
                f.cancel()
        except TimeoutError:
            print("TimeoutError: aborting remaining computations")
    return new_block, _computed_hash


def parallel_work(block, phenotype, _main_chain, time_to_sleep):
    cadena = f'{phenotype.up_down.upper()} ' \
             f'range[{phenotype.lower if phenotype.up_down == "down" else phenotype.value} to '\
             f'{phenotype.value if phenotype.up_down == "down" else "INFINITE"}]'
    _block_proof, _computed_hash = Blockchain.proof_of_work_alternate(block, phenotype)
    valid = _main_chain.is_valid_proof(_block_proof, _computed_hash)
    if not valid:
        print('x: waiting to die ', cadena)
        while True:  # waiting for time out
            continue
    print('<: done ', cadena)
    return _block_proof, _computed_hash


if __name__ == "__main__":
    # upgrade_chain()
    multiprocessing.freeze_support()
    limit_process_tasks = random.sample(range(10, 30), 1)[0]
    current_version = 4
    expected_time_per_block = 1 * 10 * 60  # (number of seconds expected between 2016 blocks) One Block
    min_transactions_to_mine = 3

    action, chain_hash, enable_ga = check_arguments(sys.argv[1:])
    chains = load_chains(action, chain_hash)
    pending_tasks = get_pending_tasks()
    for main_chain in chains:
        filtered = list(filter(lambda x: (x.content == main_chain.chain[0].hash
                                          and int(get_property('TODOIST_MINED_LABEL_ID')) not in x.label_ids
                                          and int(get_property('TODOIST_READY_TO_MINE_LABEL_ID')) in x.label_ids)
                               , pending_tasks))
        if len(filtered) > limit_process_tasks:
            filtered = filtered[0:limit_process_tasks]
        main_chain.unconfirmed_transactions = []
        main_chain.version = current_version
        # main_chain.current_target = '0x00000fffffffffffffffffffffffffffff000000000000000000000000000000'
        for trx in filtered:
            main_chain.add_new_transaction(trx.description)
        if len(main_chain.unconfirmed_transactions) < min_transactions_to_mine:
            print(f'- No enough transactions to be mined {main_chain.chain[0].hash}')
        else:
            try_to_mine_again = True
            while try_to_mine_again:
                print("-" * 150)
                print(f'- There are {len(filtered)} pending transactions (for this chain:{main_chain.chain[0].hash})')
                print(f'- Mining for the following {expected_time_per_block} seconds')
                start_mine = time.time()
                if not enable_ga:
                    block_proof, computed_hash = simple_work()
                else:
                    block_proof, computed_hash = hard_work()
                end_mine = time.time()

                if main_chain.add_block(block_proof, computed_hash):
                    #  main_chain.consensus()
                    #  main_chain.announce_new_block(blockchain.last_block)
                    print(f"Block #{main_chain.last_block.index} was mined "
                          f"with {len(main_chain.last_block.transactions)} transactions "
                          f"with nonce={main_chain.last_block.nonce}")
                    try:
                        for trx in filtered:
                            add_comment(trx.id, 'Mined in block {} with nonce={}'.format(main_chain.last_block.index
                                                                                         , main_chain.last_block.nonce))
                            update_task(trx.id, trx.label_ids)
                        print('This is a valid({}) chain with {} blocks'.format(main_chain.check_chain_validity(),
                                                                                len(main_chain.chain)))
                    except Exception as error:
                        print(f"Error in {main_chain.chain[0].hash}")
                    try_to_mine_again = False
                main_chain.current_target = main_chain.adjust_target(first=start_mine, last=end_mine
                                                         , expected_time_per_block=expected_time_per_block)
        save_chains(main_chain)
        # print(get_chain(main_chain.chain))

# export PYTHONPATH="${PYTHONPATH}:/Users/yg/Dropbox/Mac/Documents/GitHub/ygpy-blockchain/"