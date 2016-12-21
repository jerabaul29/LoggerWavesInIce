import parser_logger

path_to_data = "/media/hydroubuntu/29AE-4639/"
path_to_output = "/home/hydroubuntu/Desktop/Current/TestsParser/"
verbose = 0

parser = parser_logger.Parser_logger(path=path_to_data, path_output=path_to_output)
parser.process_folder(verbose=verbose)
