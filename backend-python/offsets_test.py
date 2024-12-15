import struct
import time as t

def save_offsets_to_binary(file_name, offset_file_name):
    offsets = []
    with open(file_name, mode='r', encoding='utf-8') as file:
        while True:
            offset = file.tell()
            line = file.readline()
            if not line:
                break
            offsets.append(offset)

    # Save offsets to a binary file
    with open(offset_file_name, mode='wb') as offset_file:
        for offset in offsets:
            offset_file.write(struct.pack('Q', offset))  # 'Q' is for unsigned long long (8 bytes)


def load_offsets_from_binary(offset_file_name):
    offsets = []
    with open(offset_file_name, mode='rb') as offset_file:
        while True:
            bytes_read = offset_file.read(8)  # Read 8 bytes (size of 'Q')
            if not bytes_read:
                break
            offsets.append(struct.unpack('Q', bytes_read)[0])
    return offsets


def read_line_using_offset(file_name, offsets, line_number):
    with open(file_name, mode='r', encoding='utf-8') as file:
        file.seek(offsets[line_number - 1])  # Convert 1-based to 0-based index
        return file.readline().strip().split(',')  # Split into columns


csv_file = "indices/inverted_index.csv"
offset_file = "indices/offsets.bin"

a = t.time()
# Precompute and save offsets
save_offsets_to_binary(csv_file, offset_file)
print(t.time() - a)

# Load offsets from binary file
offsets = load_offsets_from_binary(offset_file)

# Access the 300,000th line
line_number = 300000
line = read_line_using_offset(csv_file, offsets, line_number)
# print(line)
