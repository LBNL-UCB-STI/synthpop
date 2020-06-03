import sys
import pandas as pd
from os import listdir
from os.path import isfile, join


def get_files(dir_path, starts_with):
    def filter_func(entry):
        return entry.startswith(starts_with)

    only_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    selected_files_iterator = filter(filter_func, only_files)
    return sorted(list(selected_files_iterator))


def merge_to_table(folder_path, base_file_name):
    df_list = []
    all_parts = get_files(folder_path, base_file_name)
    print("parts to merge:", all_parts)
    for part in all_parts:
        df = pd.read_csv(folder_path + part)
        df_list.append(df)
    result_df = pd.concat(df_list, ignore_index=True, sort=True)
    return result_df


def merge(folder_path, base_file_name):
    table = merge_to_table(folder_path, base_file_name)
    result_file_name = base_file_name + ".csv"
    output_file = open(folder_path + result_file_name, "w+")
    table.to_csv(output_file)
    print(result_file_name, "created")


if __name__ == "__main__":
    folder_path = sys.argv[1]
    base_file_name = sys.argv[2]
    merge(folder_path, "household" + base_file_name)
    merge(folder_path, "people" + base_file_name)