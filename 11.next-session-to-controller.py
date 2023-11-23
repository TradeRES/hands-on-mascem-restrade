# ----------- IMPORTS ----------- #

import os
import json

# ----------- FUNCTIONS ----------- #

# Read JSON file
def read_json(filepath):
  f = open(filepath, 'r')
  json_content = json.load(f)
  f.close()
  return json_content

# ----------- MAIN ----------- #

if __name__ == "__main__":
  #
  # Get execution control file path
  _EXEC_CONTROL_ = os.path.join(os.getcwd(), 'res', 'exec-config.json')
  # 
  # Default value to loop (error)
  error = 1
  # 
  # If file exists
  if os.path.exists(_EXEC_CONTROL_):
    # 
    # Get configuration
    config = read_json(_EXEC_CONTROL_)
    #
    # Get control data
    session_dirs = config['controller']['temp']['session']['dirs']
    session_exec = config['controller']['temp']['session']['exec']
    #
    # If current excution session < len(session_dirs)
    if session_exec < len(session_dirs):
      #
      # Value to ignore loop (no error)
      error = 0
  #
  # "return error value"
  exit(error)