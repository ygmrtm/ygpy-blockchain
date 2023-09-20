try:
    from run.run_all_chains import load_chains
    from run.run_all_chains import get_chain
    import json
    import datetime
    import sys
except ImportError as exc:
    raise exc


def search(search_token):
    blockchains = load_chains("load", None)
    transactions_found = []
    for blockchain in blockchains:
        cadena = f'Searching for {search_token} ' + '=' * 80
        data_chain = get_chain(blockchain.chain)
        if data_chain.find(search_token) > 0:
            data_json = json.loads(data_chain)
            cadena += f'\nfound in {blockchain.chain[0].hash} w/({data_json["length"]}) blocks'
            for block in data_json['chain'][1:]:
                for transaction in block['transactions']:
                    try:
                        transaction_json = json.loads(transaction)
                        found = search_token == transaction_json['meta']['GDrive_id'] \
                                or search_token == transaction_json['meta']['DropBox_id'] \
                                or search_token == transaction_json['meta']['originalFilename']
                    except Exception as error:
                        continue
                    finally:
                        if found:
                            transactions_found.append(json.dumps({"block": block['index'],
                                                                  "version": block['version'],
                                                                  "difficulty": block['difficulty'],
                                                                  "mined": str(
                                                                      datetime.datetime.fromtimestamp(block['time'])),
                                                                  "mimetype": transaction_json['meta']['mimeType'],
                                                                  "md5Checksum": transaction_json['meta'][
                                                                      'md5Checksum'],
                                                                  "originalFilename": transaction_json['meta'][
                                                                      'originalFilename'],
                                                                  "created": transaction_json['meta']['creationDate'],
                                                                  "modified": transaction_json['meta'][
                                                                      'modificationDate'],
                                                                  "summary": transaction_json['generals'][
                                                                                 'what'] + ' because ' +
                                                                             transaction_json['generals'][
                                                                                 'why'] + ' by ' +
                                                                             transaction_json['generals'][
                                                                                 'who'] + ' last ' +
                                                                             transaction_json['generals'][
                                                                                 'when'] + ' in ' +
                                                                             transaction_json['generals']['where']
                                                                  }))
                            found = False
        else:
            cadena += f'\nNot found in {blockchain.chain[0].hash}'
        print(cadena)
    for tr in transactions_found:
        print(tr)


def display(bc_hash):
    blockchains = load_chains("load", bc_hash)
    transactions = []
    for blockchain in blockchains:
        for block in blockchain.chain[1:]:
            print(block)
            for transaction in block.transactions:
                '''this is for money transactions'''
                try:
                    transaction_json = json.loads(transaction.replace('\n"from"', '\n,"from"'))
                    transactions.append({"who": f'{transaction_json["generals"]["who"]}'
                                            , "when": f'{transaction_json["generals"]["when"]}'
                                            , "concept": f'{transaction_json["generals"]["concept"]}'
                                            , "amount": f'{transaction_json["generals"]["amount"]}'
                                            , "block": f'{block.index}'
                                            , "version": f'{block.version}'
                                            , "difficulty": f'{block.difficulty}'
                                            , "mined": f'{str(datetime.datetime.fromtimestamp(block.time))}'
                                         })
                except Exception as error:
                    '''this is for files transactions'''
                    try:
                        transaction_json = json.loads(transaction.replace('\n"from"', '\n,"from"'))
                        transactions.append({"who": f'{transaction_json["generals"]["who"]}-{transaction_json["generals"]["where"]}'
                                                , "when": f'{transaction_json["generals"]["when"]}'
                                                , "GDrive_id": f'{transaction_json["meta"]["GDrive_id"]}'
                                                , "DropBox_id": f'{transaction_json["meta"]["DropBox_id"]}'
                                                , "originalFilename": f'{transaction_json["meta"]["originalFilename"]}'
                                                , "block": f'{block.index}'
                                                , "version": f'{block.version}'
                                                , "difficulty": f'{block.difficulty}'
                                                , "mined": f'{str(datetime.datetime.fromtimestamp(block.time))}'
                                             })
                    except Exception as error:
                        print(error)
    transactions.sort(key=lambda x: (x["who"], x["when"]), reverse=False)
    with open("display_or_search.txt", "w") as outfile:
        outfile.write("\n".join(str(item) for item in transactions))


if __name__ == "__main__":
    print("jeloworl")
    # search('1tNIR8vPJi-MqCkB8FAiXA_e3LVzKq68f')
    display('c00e75b41f5ecaf3f9290312be3457b7d538450668ae26608efe81c836dec0e4') ## transacciones monetarias
    # display('25ff42edc4b2123b6e31a1219451ece27417a201876cc31bbd0abbcbfbb08216') ## transacciones de creaciones
    # display('02b204464a54c252b56b72ee7555e915841bb8aa8524fb5968673ba1a3040240') ## transacciones de archivos
