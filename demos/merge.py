import os
import sys
import pandas as pd
from os import listdir
from os.path import isfile, join

def getFiles(dirPath, startsWith):
    def filterFunc(entry):
        return entry.startswith(startsWith)
    
    onlyFiles = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    selectedFiles_iterator = filter(filterFunc, onlyFiles)
    return sorted(list(selectedFiles_iterator))

def mergeToTable(folderPath, baseName):
    df_list = []
    allParts = getFiles(folderPath, baseName)
    print(allParts)
    for part in allParts:
        df = pd.read_csv(folderPath + part)
        df_list.append(df)
    result_df = pd.concat(df_list, ignore_index=True, sort=True)
    return result_df

def merge(folderPath, baseFileName):
    resultFileName = baseFileName + ".csv"
    table = mergeToTable(folderPath, baseFileName)
    outputFile = open(folderPath + resultFileName, "w+")
    table.to_csv(outputFile)

if __name__ == "__main__":    
    folderPath = sys.argv[1]
    merge(folderPath, "household")
    merge(folderPath, "people")

