# ----------- IMPORTS ----------- #

import os
import sys
import json
import glob
import subprocess
try:
  import shutil
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'shutil'])
  import shutil
try:
  import natsort
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'natsort'])
  import natsort
try:
  import jsonpath_ng
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jsonpath_ng'])
  import jsonpath_ng
from jsonpath_ng.ext import parse

# ----------- CONSTANTS ----------- #

_UNITS_INFO_DIR_ = 'units_info'
_UNITS_INFO_FILE_ = 'Units_Info_2030_MI.json'

# ----------- FUNCTIONS ----------- #

# Read JSON file
def read_json(filepath):
  f = open(filepath, 'r')
  json_content = json.load(f)
  f.close()
  return json_content

# Write JSON file
def write_json(json_content, filepath):
  f = open(filepath, 'w')
  json.dump(json_content, f, indent = 2)
  f.close()

# Get JSON Path data
def get_json_path_data(json_data, json_query):
  # Initialize match list
  match_list = []
  # Set Json Path expression
  jsonpath_expression = parse(json_query)
  # For each jsonpath match
  for match in jsonpath_expression.find(json_data):
    match_list.append(match.value)
  #
  # Return match list
  return match_list

# ----------- MAIN ----------- #

if __name__ == "__main__":
  # 
  # Get configuration
  config = read_json(sys.argv[1])
  #
  # If starting execution
  if config['controller']['starting_exec']:
    #
    # Get configurations
    market_design = config['persistence']['market_designs'][ config['config']['market_design'] ]
    # DEBUG: print(market_design)
    scenario = config['config']['scenarios'][ config['config']['scenario'] ]
    # DEBUG: print(scenario)
    #
    # Create output directories
    output_dir = os.path.join(config['persistence']['output_base_dir'], scenario)
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    #
    # Get input file list
    input_dir = os.path.join(config['persistence']['input_base_dir'], scenario)
    input_file_list = natsort.natsorted(glob.glob(os.path.join(input_dir, '*.json')))
    # DEBUG: print(input_file_list)
    # If len > 0 move files to "session" directories
    if len(input_file_list) > 0:
      # For each input file
      for file in input_file_list:
        # Split file name by '_'
        file_parts = file.split('_')
        # Get session from file name
        if '.' in file_parts[-4]:
          session_in_dir = file_parts[-4].replace('.','_') + '_' + file_parts[-3]
        else:
          session_in_dir = file_parts[-5] + '_' + file_parts[-4] + '_' + file_parts[-3] + '_' + file_parts[-2]
        # DEBUG: print(session)
        # Check if destination directory exists
        destination_directory = os.path.join(input_dir, session_in_dir)
        # DEBUG: print(destination_directory)
        # If not exists
        if not os.path.exists(destination_directory):
          os.mkdir(destination_directory, 0o777)
        #
        # Get file name
        file_name = file.split(os.sep)[-1]
        # DEBUG: print(file_name)
        # Set destination path
        destination_path = os.path.join(destination_directory, file_name)
        # DEBUG: print(destination_path)
        #
        # Copy files from source path to destination path
        shutil.move(file, destination_path)
    #
    # Get simulation sessions (directories) list
    dir_list = natsort.natsorted(os.listdir(input_dir))
    # DEBUG: print(dir_list)
    # Ignore invalid directories
    session_dirs = []
    for dir in dir_list:
      # Check if it is a daily directory
      try:
        i = int(dir)
        session_dirs.append(os.path.join(input_dir, dir))
      except:
        pass
    # DEBUG: print(session_dirs)
    # Add simulation session directories list to controller
    config['controller']['temp'] = {}
    config['controller']['temp']['session'] = {}
    config['controller']['temp']['session']['dirs'] = session_dirs
    # Set next session directory to execute 
    config['controller']['temp']['session']['exec'] = 0
    # Set session period object
    config['controller']['temp']['session']['period'] = {}
    # If config.pfs.run == True
    if config['config']['pfs']['run']:
      #
      # Get units info
      units_info = read_json(os.path.join(config['persistence']['input_base_dir'], scenario, _UNITS_INFO_DIR_, _UNITS_INFO_FILE_))
      # DEBUG: print(units_info)
      #
      # Set PT / ES units list
      config['controller']['temp']['session']['period']['power_flow'] = {}
      config['controller']['temp']['session']['period']['power_flow']['units'] = {}
      config['controller']['temp']['session']['period']['power_flow']['units']['pt'] = get_json_path_data(units_info, '$.unitsInfo[?(@.country=="PT")].unitID')
      config['controller']['temp']['session']['period']['power_flow']['units']['es'] = get_json_path_data(units_info, '$.unitsInfo[?(@.country=="ES")].unitID')
    # 
    # Set start_exec false
    config['controller']['starting_exec'] = False
  #
  #  Set file list to exec
  session_dirs = config['controller']['temp']['session']['dirs']
  session_exec = config['controller']['temp']['session']['exec']
  #
  # If session_exec < len(session_dirs)
  if session_exec < len(session_dirs):
    config['controller']['temp']['session']['period']['files'] = natsort.natsorted(glob.glob(os.path.join(session_dirs[session_exec], '*.json')))
    config['controller']['temp']['session']['period']['exec'] = 0
  #
  #
  # rewrite config
  write_json(config, sys.argv[1])