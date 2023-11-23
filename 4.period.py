# ----------- IMPORTS ----------- #

import os
import sys
import json
import subprocess
try:
  import requests
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
  import requests
try:
  import jsonschema
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jsonschema'])
  import jsonschema
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

# Get EMS request JSON schema
def get_json_schema(url, request_headers):
  response = requests.get(url, headers = request_headers)
  if response.status_code != 200:
    print('Failed to obtain JSON schema:', response)
    exit(0)
  return json.loads(response.text)

# VALIDATE INPUT AGAINST SCHEMAS
def validate(json_input, base_url, request_headers):
  try:
    # Get EMS input schema
    ems_request_schema = get_json_schema(base_url + "schema", request_headers)
    #
    # Validate JSON against schema
    jsonschema.validate(instance = json_input, schema = ems_request_schema)
    #
    # Return input in case no exception is thrown
    return json_input
  except Exception as err:
    print(err)
    exit(0)

# RUN EMS
def run_ems(json_input, base_url, request_headers):
  response = requests.post(base_url, json = json_input, headers = request_headers)
  #
  # Validate response status code
  if response.status_code != 200:
    print(response.text)
    exit(0)
  #
  # convert to JSON
  json_output = json.loads(response.text)
  #
  # Return JSON output
  return json_output

# ----------- MAIN ----------- #

if __name__ == "__main__":
  # 
  # Get configuration
  config = read_json(sys.argv[1])
  # DEBUG: print(config)
  #
  # Get execution file list
  exec_files = config['controller']['temp']['session']['period']['exec_files']
  # DEBUG: print(exec_files)
  #
  # For each file
  for exec_file in exec_files:
    #
    # Check if output file already exists
    out_file_name = exec_file.replace(config['persistence']['input_base_dir'], config['persistence']['output_base_dir'])
    # DEBUG: print(out_file_name)
    #
    # If output file not exists, run EMS
    if config['config']['ems']['force_exec'] == True or not os.path.exists(out_file_name):
      # DEBUG:
      print('PROCESSING FILE', exec_file, '@', datetime.now())
      #
      # Read JSON input file
      data = read_json(exec_file)
      # Validate against schema
      input = validate(data, config['config']['ems']['base_url'], config['config']['ems']['request_headers'])
      # Run EMS
      output = run_ems(input, config['config']['ems']['base_url'], config['config']['ems']['request_headers'])
      # Save output to JSON file
      write_json(output, out_file_name)
      #
      # If config.pfs.run == True
      if config['config']['pfs']['run']:
        # Set power flow exec files
        config['controller']['temp']['session']['period']['power_flow']['exec_files'].append(out_file_name)
    else:
      # DEBUG:
      print('SKIPPING FILE', exec_file, '@', datetime.now())
  # Clear controller.temp.session.period.exec_files list
  config['controller']['temp']['session']['period']['exec_files'].clear()
  #
  #
  # rewrite config
  write_json(config, sys.argv[1])