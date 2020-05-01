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
STATE_CODE="$1"
COUNTY_NAME="$2"
CENSUS_API_KEY=$CENSUS_API_KEY_DEFAULT
NUMBER_OF_WORKERS=$NUMBER_OF_WORKERS_DEFAULT

OUTPUT_DIR=output/
OUTPUT_FILE_BASE_NAME="_$STATE_CODE"_"$COUNTY_NAME"

mkdir -p $OUTPUT_DIR

if test "$#" -ge 4; then
	CENSUS_API_KEY=$4
fi

if test "$#" -ge 3; then
	NUMBER_OF_WORKERS=$3
fi

merge () {
	mv household*.csv $OUTPUT_DIR
	mv people*.csv $OUTPUT_DIR
	python3 demos/merge.py $OUTPUT_DIR "$OUTPUT_FILE_BASE_NAME"
}

LOG_NAME=$OUTPUT_DIR"SynthPop$OUTPUT_FILE_BASE_NAME"_$(date '+%Y%m%d%H%M%S').log

if test "$#" -eq 8; then
	(
	set -x;
	N_WORKERS=$NUMBER_OF_WORKERS CENSUS=$CENSUS_API_KEY python3 demos/synthesize.py $STATE_CODE "$COUNTY_NAME $5 $6 $7 $8" | tee -a "$LOG_NAME"
	merge | tee -a "$LOG_NAME"
	)
elif test "$#" -le 4; then
	(
	set -x;
	N_WORKERS=$NUMBER_OF_WORKERS CENSUS=$CENSUS_API_KEY python3 demos/synthesize.py $STATE_CODE "$COUNTY_NAME" | tee -a "$LOG_NAME"
	merge | tee -a "$LOG_NAME"
	)
else
	printUsageMessage
	exit 2
fi

