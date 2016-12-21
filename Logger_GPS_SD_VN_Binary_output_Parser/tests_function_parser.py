import parser_logger

# path_to_file = "Example_data/F00368"
path_to_file = "/media/hydroubuntu/78AE-4639/F00377"
path_output = "/home/hydroubuntu/Desktop/Current/TestsParser/tests"

verbose = 0

data_parser = parser_logger.Parser_logger()
data_parser.load_file(path_to_file, verbose=verbose)
data_parser.parse_current_data(path_output, verbose=verbose)
