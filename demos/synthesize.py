# coding: utf-8
from synthpop.recipes.starter import Starter
from synthpop.synthesizer import synthesize_all, enable_logging
import pandas as pd
import os
import sys
from multiprocessing import Process, Lock, Queue
from datetime import datetime


def synthesize_runner(indexes_queue, county_name, state_abbr, lock, starter):
    worker_name = "[{}] runner".format(str(os.getpid()))
    print("{} started.".format(worker_name))

    try:
        while True:
            index = -1
            worker_number = -1

            lock.acquire()
            queue_is_empty = indexes_queue.empty()
            if not queue_is_empty:
                (index, worker_number) = indexes_queue.get()
            lock.release()

            if queue_is_empty:
                break

            synthesize_one_index(index, county_name, state_abbr, worker_number, starter)

        print("{} finished.".format(worker_name))

    except Exception as e:
        print("{} finished by unexpected error:".format(worker_name), e)
        raise e


def synthesize_one_index(index_to_process, county_name, state_abbr, worker_number, starter):
    worker_name = "[{}] task {}".format(str(os.getpid()), str(worker_number))
    print_progress("{} started with index {}".format(worker_name, str(index_to_process)))

    indexes = [pd.Series(index_to_process, index=["state", "county", "tract", "block group"])]

    households, people, fit_quality = synthesize_all(starter, indexes=indexes)

    hh_file_name = "household_{}_{}__part_number_{}.csv".format(state_abbr, county_name, worker_number)
    people_file_name = "people_{}_{}__part_number_{}.csv".format(state_abbr, county_name, worker_number)

    households.to_csv(hh_file_name, index=None, header=True)
    people.to_csv(people_file_name, index=None, header=True)

    for geo, qual in fit_quality.items():
        print('Geography: {} {} {} {}'.format(geo.state, geo.county, geo.tract, geo.block_group))
        # print '    household chisq: {}'.format(qual.household_chisq)
        # print '    household p:     {}'.format(qual.household_p)
        print('    people chisq:    {}'.format(qual.people_chisq))
        print('    people p:        {}'.format(qual.people_p))

    print_progress("{} has completed calculations.".format(worker_name))


def print_progress(text):
    current_time = datetime.now().strftime("%H:%M:%S")
    print("{} progress report: {}".format(current_time, text))


def start_workers(state_abbr, county_name):
    workers = int(os.cpu_count() / 2)
    if 'sched_getaffinity' in dir(os):
        workers = int(len(os.sched_getaffinity(0)) / 2)
    if os.environ.get("N_WORKERS") is not None:
        workers = int(os.environ["N_WORKERS"])
    if len(sys.argv) > 3:
        state, county, tract, block_group = sys.argv[3:]
        indexes = [pd.Series(
            [state, county, tract, block_group],
            index=["state", "county", "tract", "block group"])]
    else:
        indexes = None

    starter = Starter(os.environ["CENSUS"], state_abbr, county_name)
    enable_logging()

    if indexes is None:
        indexes = list(starter.get_available_geography_ids())
    if len(indexes) < workers:
        workers = len(indexes)

    print("Workers: %d" % (workers))
    print("Indexes: %d" % (len(indexes)))

    lock = Lock()
    indexes_queue = Queue()
    for (idx, number) in zip(indexes, range(len(indexes))):
        indexes_queue.put((idx, number))

    processes = []
    for i in range(0, workers):
        p = Process(target=synthesize_runner, args=(indexes_queue, county_name, state_abbr, lock, starter))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
        print("Process %d exit code is: %d" % (p.pid, p.exitcode))
        if p.exitcode != 0:
            print("Process %d has exited unexpectedly, the results are not correct or not full!" % (p.pid))
            sys.exit()

    print_progress("all workers have completed tasks as expected.")


if __name__ == "__main__":
    state_abbr = sys.argv[1]
    county_name = sys.argv[2]
    start_workers(state_abbr, county_name)
