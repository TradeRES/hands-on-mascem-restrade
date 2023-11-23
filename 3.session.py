# ----------- IMPORTS ----------- #

import os
import sys
import json

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
  # Get execution directory
  session_dirs = config['controller']['temp']['session']['dirs']
  session_exec = config['controller']['temp']['session']['exec']
  exec_dir = session_dirs[session_exec]
  #
  # Check if output directory exists; create it if not
  output_dir = exec_dir.replace(config['persistence']['input_base_dir'], config['persistence']['output_base_dir'])
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  #
  # Get period execution file list and exec position
  period_files = config['controller']['temp']['session']['period']['files']
  period_exec = config['controller']['temp']['session']['period']['exec']
  # DEBUG: print(period_files, period_exec)
  #
  # If period_exec < len(period_files)
  if period_exec < len(period_files):
    #
    # Set symmetrical pool execution file list
    config['controller']['temp']['session']['period']['exec_files'] = [period_files[period_exec]]
    # Set power flow verification data
    config['controller']['temp']['session']['period']['power_flow']['exec_files'] = []
  #
  #
  # rewrite config
  write_json(config, sys.argv[1])