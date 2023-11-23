# ----------- IMPORTS ----------- #

import os
import sys
import glob
import json
import subprocess
try:
  import natsort
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'natsort'])
  import natsort
try:
  import shutil
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'shutil'])
  import shutil
from datetime import datetime

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

# ----------- MAIN ----------- #

if __name__ == "__main__":
  # 
  # Get configuration
  config = read_json(sys.argv[1])
  # DEBUG: print(config)
  #
  # Get configurations
  market_design = config['persistence']['market_designs'][ config['config']['market_design'] ]
  # DEBUG: print(market_design)
  scenario = config['config']['scenarios'][ config['config']['scenario'] ]
  # DEBUG: print(scenario)
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
  # For each dir
  for dir in session_dirs:
    # Delete input files _PT & _ES
    _DEL_ = natsort.natsorted(glob.glob(os.path.join(dir, '*_PT.json')))
    _DEL_.extend(natsort.natsorted(glob.glob(os.path.join(dir, '*_ES.json'))))
    for file in _DEL_:
      os.remove(file)
  #
  # If starting execution
  if not config['controller']['starting_exec']:
    #
    # Drop temp property
    del config['controller']['temp']
    # 
    # Set start_exec true
    config['controller']['starting_exec'] = True
    #
    # rewrite config
    write_json(config, sys.argv[1])
    #
    # Delete out folder
    out_dir = input_dir.replace(config['persistence']['input_base_dir'], config['persistence']['output_base_dir'])
    if os.path.exists(out_dir):
      shutil.rmtree(out_dir)
    #
    # DEBUG:
    print('Configuration reset!')
  else:
    # DEBUG:
    print('Configuration ready!')
  #
  #
  # DEBUG: 
  print('STARTING @', datetime.now())