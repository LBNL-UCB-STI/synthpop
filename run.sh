#!/bin/sh

CENSUS_API_KEY_DEFAULT=38e8cb82455836da423750cb62838c8a753ad31e
NUMBER_OF_WORKERS_DEFAULT=1

printUsageMessage () {
	echo "usage: docker run -it synthpop-image <state code> \"<county name>\" [number of workers] [census api key] [FIPS state code] [FIPS county code] [tract code] [block group]"
	echo "  required arguments:"
	echo "\tstate code \t\t- a two capital letters state code, for example: Texas state code is TX"
	echo "\tcounty name \t\t- usually contain two words, for example: \"Travis County\" or \"Wayne County\""
	echo "  optional arguments:"
	echo "\tnumber of workers \t- number of threads for parallel calculation, by-default is $NUMBER_OF_WORKERS_DEFAULT"
	echo "\tcensus api key \t\t- a key to access to https://api.census.gov, by default is $CENSUS_API_KEY_DEFAULT"
	echo "  optional arguments to run synthpop to generate the data on census tract level:"
	echo "\tFIPS state code"
	echo "\tFIPS county code"
	echo "\ttract code"
	echo "\tblock group"
}

if test "$#" -lt 2; then
	printUsageMessage
	exit 2
fi

CENSUS_API_KEY=$CENSUS_API_KEY_DEFAULT
if test "$#" -ge 4; then
	CENSUS_API_KEY=$4
fi

NUMBER_OF_WORKERS=$NUMBER_OF_WORKERS_DEFAULT
if test "$#" -ge 3; then
	NUMBER_OF_WORKERS=$3
fi

STATE_CODE="$1"
COUNTY_NAME="$2"

OUTPUT_FILE_BASE_NAME="_$STATE_CODE"_"$COUNTY_NAME"

merge () {
	mv household* output/ 
	mv people* output/ 
	python3 demos/merge.py output/ "$OUTPUT_FILE_BASE_NAME"
}

mkdir -p output/

if test "$#" -eq 8; then
	(
	set -x; 
	N_WORKERS=$NUMBER_OF_WORKERS CENSUS=$CENSUS_API_KEY python3 demos/synthesize.py $STATE_CODE "$COUNTY_NAME $5 $6 $7 $8"
	merge
	)
elif test "$#" -le 4; then
	(
	set -x; 
	N_WORKERS=$NUMBER_OF_WORKERS CENSUS=$CENSUS_API_KEY python3 demos/synthesize.py $STATE_CODE "$COUNTY_NAME"
	merge
	)
else
	printUsageMessage
	exit 2
fi

