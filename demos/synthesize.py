
# coding: utf-8

from synthpop.recipes.starter2 import Starter
from synthpop.synthesizer import synthesize_all, enable_logging
import pandas as pd
import os
import sys

state_abbr = sys.argv[1]
county_name = sys.argv[2]

starter = Starter(os.environ["CENSUS"], state_abbr, county_name)
enable_logging()

if len(sys.argv) > 3:
    state, county, tract, block_group = sys.argv[3:]

    indexes = [pd.Series(
        [state, county, tract, block_group],
        index=["state", "county", "tract", "block group"])]
else:
    indexes = None

households, people, fit_quality = synthesize_all(starter, indexes=indexes)

hh_file_name = "household_{}_{}.csv".format(state_abbr, county_name)
people_file_name = "people_{}_{}.csv".format(state_abbr, county_name)

households.to_csv(hh_file_name, index=None, header=True)
people.to_csv(people_file_name, index=None, header=True)

for geo, qual in fit_quality.items():
    print ('Geography: {} {} {} {}'.format(
        geo.state, geo.county, geo.tract, geo.block_group))
    # print '    household chisq: {}'.format(qual.household_chisq)
    # print '    household p:     {}'.format(qual.household_p)
    print ('    people chisq:    {}'.format(qual.people_chisq))
    print ('    people p:        {}'.format(qual.people_p))
