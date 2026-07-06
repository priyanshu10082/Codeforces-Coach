# test_db.py
from db import create_checkpoints_table, save_checkpoint, get_last_two_checkpoints

create_checkpoints_table()
print("Table created successfully.")

save_checkpoint(
    "tourist",
    3800,
    3200,
    [{"tag": "dp", "success_rate": 0.3}],
    [{"tag": "greedy", "success_rate": 0.9}],
)
print("Checkpoint saved.")

result = get_last_two_checkpoints("tourist")
print(result)