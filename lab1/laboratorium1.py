from collections import defaultdict
import math

def calculate_entropy(text):
    char_frequencies = defaultdict(int)
    word_frequencies = defaultdict(int)
    total_chars = len(text)
    total_words = len(text.split())

    # Częstotliwość występowania znaków i słów
    for char in text:
        char_frequencies[char] += 1
    for word in text.split():
        word_frequencies[word] += 1

    # Entropia znaków
    char_entropy = -sum((count / total_chars) * math.log2(count / total_chars) for count in char_frequencies.values())

    # Entropia słów
    word_entropy = -sum((count / total_words) * math.log2(count / total_words) for count in word_frequencies.values())

    return char_entropy, word_entropy

def calculate_conditional_entropy(text, order):
    sequences = defaultdict(lambda: defaultdict(int))
    total_sequences = 0

    # Zlicz wystąpienia sekwencji znaków 
    for i in range(len(text) - order):
        sequence = tuple(text[i:i + order])
        next_element = text[i + order]
        sequences[sequence][next_element] += 1
        total_sequences += 1

    # Entropia warunkowa 
    conditional_entropy = 0
    for sequence, next_elements in sequences.items():
        for next_element, count in next_elements.items():
            probability = count / total_sequences
            conditional_entropy -= probability * math.log2(probability)

    return conditional_entropy

from collections import defaultdict
import math


def analyze_languages_and_files():

    # Entropia warunkowa dla języków
    languages = ['en', 'la', 'eo', 'et', 'so', 'ht', 'nv']
    languages_entropy = {}

    for language in languages:
        with open(f'norm_wiki_{language}.txt', 'r', encoding='utf-8') as file:
            text = file.read()

        language_entropies = []
        for order in range(4):
            conditional_entropy = calculate_conditional_entropy(text, order)
            language_entropies.append(conditional_entropy)

        languages_entropy[language] = language_entropies

    # Entropia warunkowa dla plików
    file_paths = ['sample0.txt', 'sample1.txt', 'sample2.txt', 'sample3.txt', 'sample4.txt', 'sample5.txt']
    files_entropy = {}

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        file_entropies = []
        for order in range(4):
            conditional_entropy = calculate_conditional_entropy(text, order)
            file_entropies.append(conditional_entropy)

        files_entropy[file_path] = file_entropies

    # ZADANIE 1,2 #
    with open('results.txt', 'w', encoding='utf-8') as result_file:
        result_file.write("\tZadanie 1,2:\n")
        result_file.write("Entropia znaków i słów w języku angielskim:\n")
        char_entropy, word_entropy = calculate_entropy(text)
        result_file.write(f"Entropia znaków: {char_entropy}\n")
        result_file.write(f"Entropia słów: {word_entropy}\n")
        print(f"Entropia znaków: {char_entropy}")
        print(f"Entropia słów: {word_entropy}")

    # ZADANIE 3 #
        result_file.write("\tZadanie 3:\n")
        result_file.write("Entropia warunkowa 1 rzędu dla liter w języku angielskim:\n")
        conditional_entropy = calculate_conditional_entropy(text, 1)
        result_file.write(f"Entropia warunkowa 1 rzędu dla znaków: {conditional_entropy}\n")
        print(f"Entropia warunkowa 1 rzędu dla znaków: {conditional_entropy}")

    # ZADANIE 4 #
        result_file.write("\tZadanie 4.1:\n")
        result_file.write("Entropia warunkowa dla różnych rzędów dla znaków i słów:\n")
        for order in range(4):
            char_conditional_entropy = calculate_conditional_entropy(text, order)
            words = text.split()
            word_conditional_entropy = calculate_conditional_entropy(words, order)
            result_file.write(f"Entropia warunkowa {order+1} rzędu dla znaków: {char_conditional_entropy}\n")
            result_file.write(f"Entropia warunkowa {order+1} rzędu dla słów: {word_conditional_entropy}\n")
            print(f"Entropia warunkowa {order+1} rzędu dla znaków: {char_conditional_entropy}")
            print(f"Entropia warunkowa {order+1} rzędu dla słów: {word_conditional_entropy}")

        result_file.write("\tZadanie 4.2:\n")
        result_file.write("Entropia warunkowa dla języków:\n")
        for language, language_entropies in languages_entropy.items():
            result_file.write(f"Entropia warunkowa dla języka {language}: {language_entropies}\n")
            print(f"Entropia warunkowa dla języka {language}: {language_entropies}")

    # ZADANIE 5 #
        result_file.write("\tZadanie 5:\n")
        result_file.write("Entropia warunkowa dla plików:\n")
        for file_path, file_entropies in files_entropy.items():
            result_file.write(f"Entropia warunkowa pliku {file_path}: {file_entropies}\n")
            for language, language_entropies in languages_entropy.items():
                differences = [abs(file_entropy - lang_entropy) for file_entropy, lang_entropy in zip(file_entropies, language_entropies)]
                result_file.write(f"Różnice entropii z językiem {language}: {differences}\n")

        # Porównaj entropię plików z entropią języków
        for file_path, file_entropies in files_entropy.items():
            print(f"\nEntropia warunkowa pliku {file_path}: {file_entropies}")
            for language, language_entropies in languages_entropy.items():
                differences = [abs(file_entropy - lang_entropy) for file_entropy, lang_entropy in zip(file_entropies, language_entropies)]
                print(f"Różnice entropii z językiem {language}: {differences}")
                
                # Sprawdź, czy różnice są mniejsze od pewnego progu (np. 0.1)
                if all(diff < 0.1 for diff in differences):
                    result_file.write(f"Plik {file_path} zawiera język naturalny: {language}\n")
                    print(f"Plik {file_path} zawiera język naturalny: {language}\n")
                    break
            else:
                result_file.write(f"Plik {file_path} nie zawiera języka naturalnego\n")
                print(f"Plik {file_path} nie zawiera języka naturalnego")

analyze_languages_and_files()

