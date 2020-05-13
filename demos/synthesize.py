# coding: utf-8
from synthpop.recipes.starter2 import Starter
from synthpop.synthesizer import synthesize_all, enable_logging
import pandas as pd
import os
import sys
from multiprocessing import Pool
from datetime import datetime


def run_all(index_to_process, county_name, state_abbr, worker_number, starter):
    worker_name = "[{}] task {}".format(str(os.getpid()), str(worker_number))
    try:
        print_progress("{} started with {} indexes.".format(worker_name, str(len(index_to_process))))

        indexes = []
        for item in index_to_process:
            indexes.append(pd.Series(item, index=["state", "county", "tract", "block group"]))

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
    except:
        print("{} unexpected error:".format(worker_name), sys.exc_info()[0])


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

    pool = Pool(workers)

    jobs_per_process = indexes  # np.array_split(indexes, len(indexes))

    number_of_jobs = len(jobs_per_process)

    jobs_per_process_with_index = zip(jobs_per_process, range(number_of_jobs))

    # processes do not share memory, so all variables just copy,
    # and it should be safe to pass a starter object inside function
    async_results = [pool.apply_async(func=run_all,
                                      args=([index], county_name, state_abbr, worker_idx, starter))
                     for (index, worker_idx) in jobs_per_process_with_index]

    print("Created %d async function runs" % (len(async_results)))

    pool.close()
    pool.join()

    for result in async_results:
        if not result.successful():
            print("ERROR. One of the workers exited unexpectedly, the results are not correct or not full!")
            sys.exit()

    print_progress("all workers have completed tasks as expected.")

    # mgr = Manager()
    # ns = mgr.Namespace()
    # ns.jobs_per_process = jobs_per_process
    # ns.state_abbr = state_abbr
    # ns.county_name = county_name

    # processes = []
    # for i in range(0, len(jobs_per_process)):
    #     p = Process(target=run_all, args=(jobs_per_process[i], county_name, state_abbr, i,))
    #     p.start()
    #     processes.append(p)
    # for p in processes:
    #     p.join()
    #     print("Process %d exit code is: %d" % (p.pid, p.exitcode))
    #     if p.exitcode != 0:
    #         print("Process %d has exited unexpectedly, the results are not correct or full!" % (p.pid))


if __name__ == "__main__":
    state_abbr = sys.argv[1]
    county_name = sys.argv[2]
    start_workers(state_abbr, county_name)
