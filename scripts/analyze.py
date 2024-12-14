import os
import sys
import re

def extract_simpl_traces(input_file, output_file):
    # Read the entire content of the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content by double newline characters (i.e., \n\n) to separate different sections
    sections = content.split('\n\n\n\n')

    # List to store all the matching trace sections
    trace_sections = []

    # Regular expression to match the exact 3-line trace structure
    trace_pattern = re.compile(r'^==================== Simpl Trace ====================\n'
                               r'tcww:no\n'
                               r'  bndr: Main.edgeCount\n', re.MULTILINE)

    section_start_line = 0
    for section in sections:
        # Check if the section matches the 3-line trace pattern
        if trace_pattern.match(section):
            section_lines = section.split('\n')
            trace_sections.append(
                (section_start_line + 1, section_start_line + len(section_lines), section))

        section_start_line += len(section.split('\n')) + 3

    # Write the matching trace sections to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, (start_line, end_line, section) in enumerate(trace_sections, 1):
            # Write the index and the line numbers in the original file
            f.write(f"({idx}): {input_file}, {start_line}-{end_line}\n")
            # Write the matched section
            f.write(section)
            f.write('\n\n\n\n')

if __name__ == '__main__':
    # Ensure that the script is called with the correct number of command line arguments
    if len(sys.argv) != 2:
        print("Usage: python analyze.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Generate the output file name by appending .analysis to the original file name
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}.analysis{ext}"

    # Call the function to extract and save the traces
    extract_simpl_traces(input_file, output_file)
    print(f"Analysis output saved to {output_file}")
