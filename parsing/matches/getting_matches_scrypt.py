from get_matches import get_matches, get_parsed_matches_ids
import json


number_of_butches = 3
batch_matches_count = 1000
start_match_id = 7399623463
start_batch_index = 2

for butch_index in range(start_batch_index, start_batch_index + number_of_butches):
    batch, start_match_id = get_matches(batch_matches_count, start_match_id)
    print(f"Getting batch is DONE with batch size {len(batch)}")
    with open(f"matches_butch_{butch_index}.json", "w") as json_file:
        json.dump(batch, json_file)
    print(f"Loading batch is DONE with batch size {len(batch)}")
print(f"Last index in scrypt: {start_match_id}")
