import os
import math
from collections import Counter
from bitarray import bitarray
import heapq


def lzw_compress(text, max_dict_size):
    code = {(i,): i for i in range(256)}
    last_code = 256

    result = []
    text = [char for char in text]

    left_side = (text[0],)
    for right_side in text[1:]:
        both_sides = (*left_side, right_side)
        if both_sides in code:
            left_side = both_sides
        else:
            if last_code >= max_dict_size:
                result.append(code[left_side])
                left_side = (right_side,)
                continue
            result.append(code[left_side])
            code[both_sides] = last_code
            last_code += 1
            left_side = (right_side,)

    result.append(code[left_side])
    length = math.ceil(math.log2(last_code))
    fixed_length_codebook = {v: f'{v:0{length}b}' for k, v in code.items()}

    encoded_bitstring = ''.join(fixed_length_codebook[char] for char in result)
    encoded_bitstring += '0' * (8 - len(encoded_bitstring) % 8)

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bitstring), 8):
        encoded_bytes.append(int(encoded_bitstring[i:i + 8], 2))

    return bytes(encoded_bytes), length




def lzw_decompress(encoded_bytes, code_length, max_dict_size):
    code = {i: chr(i) for i in range(256)}
    last_code = 256
    decoded_bitstring = ''.join(f'{byte:08b}' for byte in encoded_bytes)

    result = bytearray()
    carry = ''

    char_length = code_length

    chunks = [int(decoded_bitstring[i:i+char_length], 2) for i in range(0, len(decoded_bitstring), char_length)]
    old = chunks.pop(0)
    result.append(ord(code[old]))
    for chunk in chunks:
        if chunk in code:
            word = code[chunk]
        else:
            word = code[old] + carry
        for char in word:
            result.append(ord(char))
        carry = word[0]
        if last_code >= max_dict_size:
            old = chunk
            continue

        code[last_code] = code[old] + carry
        last_code += 1
        old = chunk

    # print(code)

    return result

def write_bits_to_file(file, data):
    with open(f'{file}', 'wb') as f:
        f.write(bytes(data))

def calculate_compression_ratio(original_size, compressed_size):
    return original_size / compressed_size


class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_tree(freq_table):
    heap = [Node(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)

    return heap[0]

def build_codebook(tree):
    codebook = {}
    def traverse(node, code, prefix):
        if node is None:
            return
        if node.char is not None:
            codebook[node.char] = prefix
            return
        traverse(node.left, code, prefix + '0')
        traverse(node.right, code, prefix + '1')

    traverse(tree, codebook, '')
    return codebook

def compress_huffman(data, codebook):
    compressed = bitarray()
    for char in data:
        binary_code = codebook[char]
        compressed.extend([int(b) for b in binary_code])

    # Convert the bitarray to bytes
    compressed_bytes = compressed.tobytes()

    return compressed_bytes


def decompress_huffman(compressed, tree):
    decompressed = bytearray()
    node = tree
    for byte in compressed:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            if bit == 0:
                node = node.left
            else:
                node = node.right
            if node.char is not None:
                decompressed.append(node.char)
                node = tree
    return decompressed

def lzw(file_path, original_data, max_dict_size):
    filename, extension = file_path.split('.')
    # LZW compression without Huffman coding
    compressed_data_lzw, code_length = lzw_compress(original_data, max_dict_size)
    write_bits_to_file(f"output/lzw_{filename}.bin", compressed_data_lzw)

    # LZW decompression
    with open(f'output/lzw_{filename}.bin', 'rb') as file:
        text = file.read()

    decoded_text = lzw_decompress(text, code_length, max_dict_size)
    with open(f'decode/out_lzw_{filename}.{extension}', 'wb') as file:
        file.write(decoded_text)

    # Calculate compression ratio for LZW without Huffman
    compressed_size_lzw = os.path.getsize(f"output/lzw_{filename}.bin")
    compression_ratio_lzw = calculate_compression_ratio(len(original_data) * 8, compressed_size_lzw)

    # Write information to result.txt
    with open(f"result{max_dict_size}.txt", "a") as result_file:
        result_file.write(f'File: {file_path}\n')
        result_file.write(f'max_dict_size: {max_dict_size}\n')
        result_file.write(f'Size before (LZW): {len(original_data) * 8} bits\n')
        result_file.write(f'Size after (LZW): {compressed_size_lzw} bits\n')
        result_file.write(f'Compression Ratio (LZW): {compression_ratio_lzw}\n\n')


def lzw_huffman(file_path, original_data, max_dict_size):
    filename, extension = file_path.split('.')
    # LZW compression
    compressed_data_lzw, code_length = lzw_compress(original_data, max_dict_size)

    # Huffman encoding
    freq_table = Counter(compressed_data_lzw)
    huffman_tree = build_tree(freq_table)
    huffman_codebook = build_codebook(huffman_tree)
    compressed_data_huffman = compress_huffman(compressed_data_lzw, huffman_codebook)

    # Write compressed data to file
    write_bits_to_file(f"output/lzw_huffman_{filename}.bin", compressed_data_huffman)

    # Decode Huffman
    with open(f'output/lzw_huffman_{filename}.bin', 'rb') as file:
        huffman_compressed_data = file.read()

    decoded_lzw_huffman = decompress_huffman(huffman_compressed_data, huffman_tree)
    decoded_lzw = lzw_decompress(decoded_lzw_huffman, code_length, max_dict_size)

    # Write decoded data to file
    with open(f'decode/out_lzw_huffman_{filename}.{extension}', 'wb') as file:
        file.write(decoded_lzw)

    # Calculate compression ratio for LZW + Huffman
    compressed_size_lzw_huffman = os.path.getsize(f"output/lzw_huffman_{filename}.bin")
    compression_ratio_lzw_huffman = calculate_compression_ratio(len(original_data) * 8, compressed_size_lzw_huffman)

    # Write information to result.txt
    with open(f"result{max_dict_size}.txt", "a") as result_file:
        result_file.write(f'File: {file_path}\n')
        result_file.write(f'max_dict_size: {max_dict_size}\n')
        result_file.write(f'Size before (LZW + Huffman): {len(original_data) * 8} bits\n')
        result_file.write(f'Size after (LZW + Huffman): {compressed_size_lzw_huffman} bits\n')
        result_file.write(f'Compression Ratio (LZW + Huffman): {compression_ratio_lzw_huffman}\n\n')


def main():
    files = ['norm_wiki_sample.txt', 'wiki_sample.txt', 'lena.bmp']
    max_dict_size = 2**12
    for file_path in files:
        print(f'Processing {file_path}...')
        original_data = open(f'input/{file_path}', 'rb').read()
        

        lzw(file_path, original_data, max_dict_size)
        lzw_huffman(file_path, original_data, max_dict_size)


if __name__ == "__main__":
    main()
