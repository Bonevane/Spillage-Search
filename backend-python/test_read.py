import csv
import sys
from itertools import islice
import time as t

csv.field_size_limit(10_000_000)


def precompute_offsets(file_name):
    offsets = []
    with open(file_name, mode='r', encoding='utf-8') as file:
        while True:
            offset = file.tell()
            line = file.readline()
            if not line:
                break
            offsets.append(offset)
    return offsets

offsets = precompute_offsets("indices/inverted_index.csv")


def read_300000th_line(file_name, offsets):
    with open(file_name, mode='r', encoding='utf-8') as file:
        file.seek(offsets[299_999])  # 300,000th line index is 299,999
        return file.readline().strip().split(',')

a = t.time()
line = read_300000th_line("indices/inverted_index.csv")
print(t.time() - a)