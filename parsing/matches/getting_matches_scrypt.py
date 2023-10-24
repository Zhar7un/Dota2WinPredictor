from get_matches import get_matches
import json


number_of_butches = 5
batch_matches_count = 1000
start_match_id = 7396419423
start_batch_index = 10

for butch_index in range(start_batch_index, start_batch_index + number_of_butches):
    batch = get_matches(batch_matches_count, start_match_id)
    print(f"Getting batch is DONE with batch size {len(batch)}")
    with open(f"matches_butch_{butch_index}.json", "w") as json_file:
        json.dump(batch, json_file)
    print(f"Loading batch is DONE with batch size {len(batch)}")
    start_match_id = batch[-1]["match_id"]
print(f"Last index in scrypt: {start_match_id}")
