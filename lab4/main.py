import os
import math
from bitarray import bitarray


def load_file(file_name):
    file = open(file_name, 'r')
    return file.read()

def analyze_text(text):
    characters_count = {}
    total_characters = 0

    for _, char in enumerate(text):
        count = characters_count.get(char, 0)
        characters_count.update({char: count + 1})
        total_characters += 1

    return characters_count, total_characters

def generate_code(characters_dict):
    codes_dict = {}
    unique_chars = len(characters_dict.keys())
    code_length = math.ceil(math.log(unique_chars + 1, 2))

    for index, char in enumerate(characters_dict.keys()):
        base_code = int_to_bits(code_length, index) # Convert integer value to bit array
        codes_dict.update({char: base_code})

    return codes_dict, code_length

def int_to_bits(length, value):
    bits_array = [1 if digit == '1' else 0 for digit in bin(value)[2:]]
    bits = bitarray(length - len(bits_array))
    bits.setall(0)
    for bit in bits_array:
        bits.append(bit)
    return bits

def encode_text(codes, text):
    encoded_text = bitarray()

    for char in text:
        for bit in codes.get(char):
            encoded_text.append(bit)

    return encoded_text

def decode_text(encoded_bits, codes, length):
    decoded_text = ''
    total_length = len(encoded_bits)

    for index in range(int(total_length / length)):
        code = encoded_bits[index * length: (index + 1) * length].to01()
        decoded_text += codes.get(code, '')

    return decoded_text

def save_encoded_result(codes, encoded_content, directory, bytesize=8):
    if not os.path.exists(directory):
        os.makedirs(directory)

    content = encoded_content.copy()
    for _ in range(len(content) % bytesize):
        content.append(1)
    with open(directory + 'result', 'wb') as content_file:
        content.tofile(content_file)
    with open(directory + 'key', 'w') as key_file:
        for key in codes.keys():
            key_file.write(key)

def load_encoded_result(directory):
    encoded_content = bitarray()
    codes_dict = {}

    with open(directory + 'result', 'rb') as content_file:
        encoded_content.fromfile(content_file)

    with open(directory + 'key', 'r') as key_file:
        content = key_file.read()
        code_length = math.ceil(math.log(len(content) + 1, 2))

        for index, char in enumerate(content):
            base_code = int_to_bits(code_length, index)
            codes_dict.update({base_code.to01(): char})

    return encoded_content, code_length, codes_dict

def calculate_sizes(directory, original_file):
    encoded_size = os.stat(directory + 'result').st_size
    key_size = os.stat(directory + 'key').st_size
    original_size = os.stat(original_file).st_size
    return encoded_size, key_size, original_size

def main():
    encoded_directory = 'encoded/'
    decoded_directory = 'decoded/'
    file_name = 'norm_wiki_sample.txt'

    text_content = load_file(file_name) #read file
    chars_dict, _ = analyze_text(text_content) # Analyze content - calculate probability
    codes_dict, _ = generate_code(chars_dict) #create code 
    encoded_result = encode_text(codes_dict, text_content) #encode text

    save_encoded_result(codes_dict, encoded_result, encoded_directory) # Save the encoded result and codes to files

    loaded_content, loaded_code_length, loaded_codes_dict = load_encoded_result(encoded_directory) # Load the encoded result and codes from files
    decoded_result = decode_text(loaded_content, loaded_codes_dict, loaded_code_length) # Decode the encoded content using the loaded codes

    # Save the decoded result to a file in the 'decoded' folder
    if not os.path.exists(decoded_directory):
        os.makedirs(decoded_directory)

    with open(decoded_directory + 'result', 'w') as decoded_file:
        decoded_file.write(decoded_result)
    
    # Calculate the sizes of the original, encoded, and key files
    encode_size, key_size, file_size = calculate_sizes(encoded_directory, file_name)
    
    # Calculate the total size of the encoded and key files
    sum_size = key_size + encode_size
    print(f'Original file: "{file_name}"')
    print(f'File size: {file_size} [bytes]')

    print(f'Encoded size: {encode_size} [bytes]')
    print(f'Key size: {key_size} [bytes]')
    print(f'All size: {sum_size} [bytes]')

    print('Compare files check')

    # Calculate compression ratio and space saving
    compression_ratio = round(file_size / sum_size, 2)
    space_saving = round(1 - sum_size / file_size, 2)

# Check if the decoded result matches the original content
    if decoded_result == text_content:
        print('Equal == true (✓)')
        print(f'Compression ratio: {compression_ratio}')
        print(f'Space saving: {space_saving}')
    else:
        print('Content != Decoded(Encoded(Content))')

        print(text_content)
        print('\n\n--------\n\n')
        print(decoded_result)

if __name__ == '__main__':
    main()
