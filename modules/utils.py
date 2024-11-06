import csv
import random
import time
from datetime import datetime

from tqdm import tqdm


def random_sleep(from_sleep, to_sleep):
    time.sleep(random.randint(from_sleep, to_sleep))


def sleep(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    desc = datetime.now().strftime("%H:%M:%S")

    for _ in tqdm(
        range(x), desc=desc, bar_format="{desc} | Sleeping {n_fmt}/{total_fmt}"
    ):
        time.sleep(1)
    print()


def write_to_csv(path, headers, data):
    with open(path, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(headers)

        writer.writerow(data)
