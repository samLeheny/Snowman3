import os
import json
POSITIONS_FILEPATH = '{}/data/biped_positions.json'.format(os.path.dirname(__file__).replace('\\', '/'))

with open(POSITIONS_FILEPATH, mode='r') as f:
    BIPED_POSITIONS = json.loads(f.read())
