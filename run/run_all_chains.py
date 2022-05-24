#!/usr/bin/python3
try:
    import pickle
    import os

    import sys
    import getopt
    import json
    from todoist_api_python.api import TodoistAPI
    from entity.Blockchain import Blockchain
    from jproperties import Properties
except ImportError as exc:
    raise exc


path = "../chains_by_genblock_hash"  # path of the directory


def check_arguments(argv):
    input_action = input_genesis = None
    usage = 'run_all_chains.py -a [new|load] -g hash_code_of_genesis -x [True|False](for Genetic)'
    try:
        opts, args = getopt.getopt(argv, "ha:g:")
        for opt, arg in opts:
            if opt == '-h':
                print(usage)
                sys.exit()
            elif opt in ("-a", "--action"):
                input_action = arg
            elif opt == "-g":
                input_genesis = arg
                input_action = 'load'
    except Exception:
        print(usage)
        sys.exit(2)
    print('Action to perform is: ', input_action, (' this chain hash ' + input_genesis if input_genesis else ''))
    return input_action, input_genesis


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


if __name__ == "__main__":
    limit = 20
    current_version = 3
    action, chain_hash = check_arguments(sys.argv[1:])
    chains = load_chains(action, chain_hash)
    pending_tasks = get_pending_tasks()
    for main_chain in chains:
        filtered = list(filter(lambda x: (x.content == main_chain.chain[0].hash and int(get_property(
            'TODOIST_MINED_LABEL_ID')) not in x.label_ids and int(get_property(
            'TODOIST_READY_TO_MINE_LABEL_ID')) in x.label_ids), pending_tasks))
        if len(filtered) > limit:
            filtered = filtered[0:limit]
        print(f'There are {len(filtered)} pending transactions (for this chain)')
        main_chain.unconfirmed_transactions = []
        main_chain.version = current_version
        #main_chain.current_target = '0x000fffffffffffffffffffffffffffff00000000000000000000000000000000'
        for trx in filtered:
            main_chain.add_new_transaction(trx.description)
        if main_chain.mine(with_ag=False):
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
                continue

        save_chains(main_chain)
            # print(get_chain(main_chain.chain))

