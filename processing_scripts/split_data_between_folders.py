from __future__ import print_function
import os
import math
import shutil

# The code for looking at the data is not too much optimized and will load everything in RAM.
# To avoid RAM exhaustion, should avoid to load too much data at once.
# For this, split the data in a number of partial data folders.
# TODO: can be improved in several ways; in particular, should decide how to put data depending on timestamps
# should go first once through all files, find timestamps range, and use this to split

NUMBER_FILES_PER_LOG = 11

path_to_data_to_split = "/home/jrlab/Desktop/Data/DataSvalbard2019/Parsed" + "/"
path_to_data_splitted = "/home/jrlab/Desktop/Data/DataSvalbard2019/all_segments/Segment"

number_of_splitted_folders = 10

for crrt_dir in os.listdir(path_to_data_to_split):
    print("--------------- spltting {} ---------------".format(crrt_dir))

    list_files = os.listdir(path_to_data_to_split + crrt_dir + "/")
    list_files.sort()

    number_of_files = len(list_files)
    number_of_filenumbers = number_of_files / NUMBER_FILES_PER_LOG

    print("number of files: {}".format(number_of_files))
    print("corresponding to a number of logs: {}".format(number_of_filenumbers))

    print("first sorted file: {}".format(list_files[0]))
    print("last  sorted file: {}".format(list_files[-1]))

    # note: the last segment may contain more files than the others
    number_of_files_per_segment = math.floor(number_of_filenumbers / number_of_splitted_folders) * NUMBER_FILES_PER_LOG

    for current_segment in range(number_of_splitted_folders):

        crrt_dir_out = path_to_data_splitted + "_" + str(current_segment) + "/"
        if not os.path.isdir(crrt_dir_out):
            os.mkdir(crrt_dir_out)

        start_file = current_segment * number_of_files_per_segment

        if current_segment == number_of_splitted_folders - 1:
            end_file = number_of_files - 1
        else:
            end_file = (current_segment + 1) * number_of_files_per_segment - 1

        print("current segment is files {} (included) to {} (included)".format(start_file, end_file))

        crrt_dir_out = path_to_data_splitted + "_" + str(current_segment) + "/" + crrt_dir + "/"
        print("copy to {}".format(crrt_dir_out))

        if not os.path.isdir(crrt_dir_out):
            os.mkdir(crrt_dir_out)

        assert(float(start_file).is_integer())
        assert(float(end_file).is_integer())

        start_file = int(start_file)
        end_file = int(end_file)

        assert(list_files[start_file][-1] == 'B')
        assert(list_files[end_file][-1] == 'S')

        for crrt_file_number in range(start_file, end_file + 1):

            path_in = path_to_data_to_split + crrt_dir + "/" + list_files[crrt_file_number]
            path_out = crrt_dir_out + list_files[crrt_file_number]

            print("    copy file {} to {}".format(path_in, path_out))

            shutil.copy(path_in, path_out)


"""
just to not be annoyed of the static analyser tool popping up









"""
