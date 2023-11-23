# ----------- IMPORTS ----------- #

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
  # Increment period
  config['controller']['temp']['session']['period']['exec'] += 1
  # Clear controller.temp.session.period.exec_files list
  config['controller']['temp']['session']['period']['exec_files'].clear()
  # Clear controller.temp.session.period.power_flow.exec_files list 
  config['controller']['temp']['session']['period']['power_flow']['exec_files'].clear()
  #
  #
  # rewrite config
  write_json(config, sys.argv[1])