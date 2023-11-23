# ----------- IMPORTS ----------- #

import sys
import json
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
  # Drop temp property
  del config['controller']['temp']
  # Set start_exec true
  config['controller']['starting_exec'] = True
  #
  #
  # rewrite config
  write_json(config, sys.argv[1])
  #
  # DEBUG: 
  print('THE END @', datetime.now())