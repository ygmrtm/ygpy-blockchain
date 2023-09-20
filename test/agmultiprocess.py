import time
from multiprocessing import Pool

work = (["W", 5], ["X", 2], ["Y", 4], ["Z", 3])


def worker(work_data):
    print(" Process %s waiting %s seconds" % (work_data[0], work_data[1]))
    time.sleep(int(work_data[1]))
    print(" Process %s Finished." % work_data[0])


def countdown(ind):
    t = time.time()
    size = 10000000
    # print('\n Inicia ind {} at {}'.format(ind, t))
    while size > 0:
        size -= 1
    return '   {}='.format(ind) + str(time.time() - t)


def poolHandler():
    p = Pool(12)
    t = time.time()
    range_ = tuple(range(2))
    ## p.map(worker, work )
    multi = p.map(countdown, range_)
    print("\n\n >>> using pools:" + str(time.time() - t))
    #for x in multi:
    #    print(x)


#if __name__ == '__main__':
#    poolHandler()
