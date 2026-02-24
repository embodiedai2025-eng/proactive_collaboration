import json

with open('constants.json', 'r') as f:
    constants = json.load(f)
    
ROOMS = constants['ROOMS']
EXPLOREPOINTS = constants['EXPLOREPOINTS'] 
EDGES = constants['EDGES']
RANDOM_OBJECT_LOCTIONS_TRAPPED = constants['RANDOM_OBJECT_LOCTIONS_TRAPPED']
RANDOM_OBJECT_LOCTIONS_MIS = constants['RANDOM_OBJECT_LOCTIONS_MIS']