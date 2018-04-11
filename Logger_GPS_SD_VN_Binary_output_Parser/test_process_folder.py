import parser_logger

path_to_data = "/home/jrlab/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser/Example_data/"
path_to_output = "/home/jrlab/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser/Example_parsed_data/"
verbose = 0

parser = parser_logger.Parser_logger(path=path_to_data, path_output=path_to_output)
parser.process_folder(verbose=verbose)
