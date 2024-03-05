from itertools import islice
def main():
    actual_data_path = 'data_actual_words.txt'
    ocr_data_path = 'data_ocr_outputs.txt'
    
    initial_probability_dict, transition_probability_dict, emission_probability_dict =count_letters(actual_data_path,ocr_data_path)
    
    print("INITIAL PROBABILITIES")
    for next_char, probability in initial_probability_dict.items():
        print(f"  {next_char}: {probability}")
    print_nested_dict(transition_probability_dict, "TRANSITION PROBABILITIES")
    print_nested_dict(emission_probability_dict, "EMISSION PROBABILITIES")
    
    changed, changed_word = iterate_over_ocrs(actual_data_path, ocr_data_path, initial_probability_dict, transition_probability_dict, emission_probability_dict)
    print("There is",changed,"corrected letters and", changed_word, "changed words")
    
    
def print_nested_dict(dict, title):
    print(title)
    for char, char_dict in dict.items():
        print(f"{char}:")
        for next_char, probability in char_dict.items():
            print(f"  {next_char}: {probability}")

def iterate_over_ocrs(actual_data_path, ocr_data_path, initial_probability_dict, transition_probability_dict, emission_probability_dict):
    changed = 0
    lines_to_skip = 50000
    changed_word = 0

    with open(actual_data_path, 'r') as file_actual, open(ocr_data_path, 'r') as file_ocr:
        # Iterate over lines in both files, skipping the first 50,000 lines
        for line_number, (line_actual, line_ocr) in enumerate(zip(file_actual, file_ocr), start=1):
            if line_number <= lines_to_skip:
                continue  # Skip lines before the 50,000th line

            stripped_line_ocr = line_ocr.strip()
            stripped_line_actual = line_actual.strip()
            new_line = viterbi(stripped_line_ocr, initial_probability_dict, transition_probability_dict, emission_probability_dict)
            
            i = 0
            for char in new_line[0]:
                if char != stripped_line_ocr[i] and char == stripped_line_actual[i]:
                    
                    changed += 1
                i += 1
            result_string = ''.join(new_line[0])
            
            if stripped_line_ocr != result_string:
                changed_word +=1
                print(stripped_line_ocr, "->", result_string)
            
    return changed, changed_word
    
def viterbi(observed_sequence, initial_prob, transition_prob, emission_prob):
    states = list(transition_prob.keys())
    T = len(observed_sequence)
    
    # Initialize the Viterbi matrix and backpointer matrix
    viterbi_matrix = {state: [0] * T for state in states}
    backpointer_matrix = {state: [""] * T for state in states}
    
    # Initialization step
    for state in states:
        viterbi_matrix[state][0] = initial_prob[state] * emission_prob[state][observed_sequence[0]]
    
    # Recursion step
    for t in range(1, T):
        for state in states:
            max_prob = 0
            max_state = ""
            for prev_state in states:
                prob = viterbi_matrix[prev_state][t-1] * transition_prob[prev_state][state] * emission_prob[state][observed_sequence[t]]
                if prob > max_prob:
                    max_prob = prob
                    max_state = prev_state
            viterbi_matrix[state][t] = max_prob
            backpointer_matrix[state][t] = max_state
    
    # Termination step
    max_last_state = max(states, key=lambda state: viterbi_matrix[state][T-1])
    max_prob = viterbi_matrix[max_last_state][T-1]
    
    # Backtrack to find the best path
    best_path = [max_last_state]
    for t in range(T-1, 0, -1):
        max_last_state = backpointer_matrix[max_last_state][t]
        best_path.insert(0, max_last_state)
    
    return best_path, max_prob

    
def initialize_char_dict():
    # Creates a dictionary of letters  
    return {letter: 0 for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}

def initialize_nested_char_dict():
    # Creates a nested dictionary that contains all letter pairs
    return {char: {letter: 0 for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'} for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}

            
def count_letters(actual_data_path, ocr_data_path):
    initial_probability_dict = initialize_char_dict()
    transition_count_dict = initialize_nested_char_dict()
    emission_count_dict = initialize_nested_char_dict()

    # Open both files in read mode
    with open(actual_data_path, 'r') as file_actual, open(ocr_data_path, 'r') as file_ocr:
        # Iterate over lines in both files simultaneously
        for line_actual, line_ocr in islice(zip(file_actual, file_ocr), 50000):
            # Process lines from both files as needed
            stripped_line_actual = line_actual.strip()
            stripped_line_ocr = line_ocr.strip()
            initial_probability_dict[stripped_line_actual[0]] += 1

            for i in range(len(stripped_line_actual) - 1):
                
                current_char_actual = stripped_line_actual[i]
                next_char_actual = stripped_line_actual[i + 1]
                
                current_char_ocr = stripped_line_ocr[i]
                next_char_ocr = stripped_line_ocr[i + 1]
                
                transition_count_dict[current_char_actual][next_char_actual] += 1
                emission_count_dict[current_char_actual][current_char_ocr] += 1
            emission_count_dict[next_char_actual][next_char_ocr] += 1
            
    return calculate_probabilities(initial_probability_dict), calculate_nested_probabilities(transition_count_dict),calculate_nested_probabilities(emission_count_dict)
    
def calculate_probabilities(count_dict):
    # Calculate probabilities from counts.
    total_count = sum(count_dict.values())
    probabilities_dict = {element: count / total_count for element, count in count_dict.items()}
    return probabilities_dict

def calculate_nested_probabilities(count_dict):
    # Calculate probabilities from counts.
    probabilities_dict = {}
    for char, inner_dict in count_dict.items():
        total_count = sum(inner_dict.values())
        inner_probabilities = {letter: count / total_count for letter, count in inner_dict.items()}
        probabilities_dict[char] = inner_probabilities
    return probabilities_dict

main()