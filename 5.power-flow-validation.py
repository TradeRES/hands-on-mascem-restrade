# ----------- IMPORTS ----------- #

import sys
import json
import subprocess
try:
  import jsonpath_ng
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jsonpath_ng'])
  import jsonpath_ng
from datetime import datetime
from jsonpath_ng.ext import parse

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

# Check if there are units from multiple bidding areas
def has_units_from_multiple_bidding_areas(trading_results, pt_units, es_units):
  # Initialize auxiliary variables
  has_units_pt = False
  has_units_es = False
  #
  # For each result
  for result in trading_results:
    if not has_units_pt and result['offerUUID'] in pt_units:
      has_units_pt = True
    if not has_units_es and result['offerUUID'] in es_units:
      has_units_es = True
    if has_units_pt & has_units_es:
      break
  #
  return (has_units_pt & has_units_es)

# Get bidding area traded demand / supply
def get_bid_area_traded_energy(trading_results, bid_area_units, transaction_type = 'buy'):
  # Initialize auxiliary variables
  traded_energy = 0
  # Get tradingResults with transactionType = transaction_type
  filtered_trading_results = get_json_path_data(trading_results, '$[?(@.transactionType=="' + transaction_type + '")]')
  # DEBUG: print(filtered_trading_results)
  #
  # For each result
  for result in filtered_trading_results:
    # If unit in bid_area_units
    if result['offerUUID'] in bid_area_units:
      traded_energy += result['tradedEnergy']
  #
  return traded_energy

# Get year day from date str
def get_year_day(date_str):
  # DEBUG: print(date_str)
  #
  # Return day of year
  return datetime.strptime(date_str, '%Y-%m-%d').timetuple().tm_yday

# Get season
def get_season(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    # DEBUG: print(date)
    month = date.month * 100
    # DEBUG: print(month)
    day = date.day
    # DEBUG: print(day)
    month_day = month + day  #combining month and day
    # DEBUG: print(month_day)
    #
    if ((month_day >= 301) and (month_day <= 531)):
        season = "spring"
    elif ((month_day > 531) and (month_day < 901)):
        season = "summer"
    elif ((month_day >= 901) and (month_day <= 1130)):
        season = "autumn"
    elif ((((month_day > 1130) and (month_day <= 1231))) or ((month_day > 100) and (month_day <= 229))):
        season = "winter"
    else:
        raise IndexError("Invalid Input")
    #
    return season

# Get bidding area bids
def get_biding_area_bids(in_json, bid_area_units):
  # Initialize variable
  bids = { 'demandBids': [], 'supplyBids': [] }
  #
  # For each demand bid
  for bid in in_json['demandBids']:
    if bid['offerUUID'] in bid_area_units:
      bids['demandBids'].append(bid)
  #
  # For each supply bid
  for bid in in_json['supplyBids']:
    if bid['offerUUID'] in bid_area_units:
      bids['supplyBids'].append(bid)
  #
  return bids

# ----------- MAIN ----------- #

if __name__ == "__main__":
  # 
  # Get configuration
  config = read_json(sys.argv[1])
  # DEBUG: print(config)
  #
  # If config.pfs.run == True
  if config['config']['pfs']['run']:
    #
    # Get pt / es units
    pt_units = config['controller']['temp']['session']['period']['power_flow']['units']['pt']
    es_units = config['controller']['temp']['session']['period']['power_flow']['units']['es']
    #
    # Get execution file list
    exec_files = config['controller']['temp']['session']['period']['power_flow']['exec_files']
    # DEBUG: print(exec_files)
    #
    # For each file
    for exec_file in exec_files:
      # Get exec_file JSON content
      pool_result = read_json(exec_file)
      # DEBUG: print(pool_result)
      #
      # Check if there are players from both trading areas
      if has_units_from_multiple_bidding_areas(pool_result['tradingResults'], pt_units, es_units):
        # Get pt / es traded energy
        pt_traded_demand = get_bid_area_traded_energy(pool_result['tradingResults'], pt_units)
        # DEBUG: print('pt_traded_demand:', pt_traded_demand)
        pt_traded_supply = get_bid_area_traded_energy(pool_result['tradingResults'], pt_units, 'sell')
        # DEBUG: print('pt_traded_supply:', pt_traded_supply)
        es_traded_demand = get_bid_area_traded_energy(pool_result['tradingResults'], es_units)
        # DEBUG: print('es_traded_demand:', es_traded_demand)
        es_traded_supply = get_bid_area_traded_energy(pool_result['tradingResults'], es_units, 'sell')
        # DEBUG: print('es_traded_supply:', es_traded_supply)
        # DEBUG: print("Validity check ::", pt_traded_demand + es_traded_demand, '==', pt_traded_supply + es_traded_supply)
        # 
        # Compute cross boarder energy flow
        cross_boarder_flow = round(pt_traded_demand - pt_traded_supply, 0)
        if cross_boarder_flow > 0:
          # PT imports energy from ES: ES->PT
          direction = 'ES->PT'
          # DEBUG: print('PT imports', cross_boarder_flow, 'from ES')
        else:
          # ES imports energy from PT: PT->ES
          direction = 'PT->ES'
          # DEBUG: print('ES imports', cross_boarder_flow, 'from PT')
        # 
        # Compute season
        # Split file name by '_'
        file_parts = exec_file.split('_')
        # DEBUG: print(file_parts)
        # Get date_str from file name
        if '.' in file_parts[-4]:
          date_str = file_parts[-3].replace('.','-')
        else:
          date_str = file_parts[-5] + '-' + file_parts[-4] + '-' + file_parts[-3]
        # DEBUG: print(date_str)
        season = get_season(date_str)
        # DEBUG: print(season)
        #
        # Get cross boarder capacity by season
        cross_boarder_capacity = config['config']['pfs']['dlr'][direction][season]
        # DEBUG: print(cross_boarder_capacity)
        #
        # If cross_boarder_flow > cross_boarder_capacity
        if cross_boarder_flow > cross_boarder_capacity:
          # Get input bids
          in_file = exec_file.replace(config['persistence']['output_base_dir'], config['persistence']['input_base_dir'])
          # DEBUG: print(in_file)
          #
          # Get JSON data
          in_json = read_json(in_file)
          # DEBUG: print(in_json)
          # Split bids to rerun period
          pt_bids = get_biding_area_bids(in_json, pt_units)
          # DEBUG: print(len(pt_bids))
          es_bids = get_biding_area_bids(in_json, es_units)
          # DEBUG: print(len(es_bids))
          # 
          # Save area bids as input files
          in_file_pt = in_file.replace('.json', '_PT.json')
          in_file_es = in_file.replace('.json', '_ES.json')
          write_json(pt_bids, in_file_pt)
          write_json(es_bids, in_file_es)
          #
          # Add paths to controller.temp.session.period.exec_files list
          config['controller']['temp']['session']['period']['exec_files'] = [in_file_pt, in_file_es]
          # Clear controller.temp.session.period.power_flow.exec_files list 
          config['controller']['temp']['session']['period']['power_flow']['exec_files'].clear()
          # 
          # Invalid power flow
          config['controller']['temp']['session']['period']['power_flow']['is_valid'] = False
        else:
          # Valid power flow
          config['controller']['temp']['session']['period']['power_flow']['is_valid'] = True
      else:
        # Ignores the power flow validation, 
        # assuming each bidding area transmission grid supports all transactions
        config['controller']['temp']['session']['period']['power_flow']['is_valid'] = True
    # Clear controller.temp.session.period.power_flow.exec_files list
    config['controller']['temp']['session']['period']['power_flow']['exec_files'].clear()
  else:
    # Ignores the power flow validation, assuming it is valid
    config['controller']['temp']['session']['period']['power_flow']['is_valid'] = True
  #
  #
  # rewrite config
  write_json(config, sys.argv[1]) 