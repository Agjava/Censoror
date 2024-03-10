import argparse
import spacy.cli
import spacy
import os
import glob
from google.cloud import language_v1
import re

# Download the spaCy large English model
spacy.cli.download("en_core_web_lg")


# Function to filter out 4-digit numbers from the list
def filter_out_4_digit_numbers(strings):
    return [s for s in strings if not re.match(r'^\d{4}$', s)]

def replace_with_blocks(text, entities):
    ent = filter_out_4_digit_numbers(entities)
    for replace_str in ent:
        full_block = "\u2588" * len(replace_str)  # Unicode full block character
        text = text.replace(replace_str, full_block)

    return text

def analyze_entities(text_content):
    
    count = [] # count variable for stats [name, address, phone no., date]

    # Load the English NER model from spacy
    nlp = spacy.load("en_core_web_lg")
    
    # Process the text with the spaCy NLP pipeline
    doc = nlp(text_content)

    # Extract named entities (addresses, dates, and phone numbers) using google natural language api
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    client = language_v1.LanguageServiceClient.from_service_account_json('key.json')

    document = language_v1.Document(content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entities(document=document, encoding_type=language_v1.EncodingType.UTF8)

    entities = response.entities

    entity_texts = [entity.name for entity in entities if language_v1.Entity.Type(entity.type_).name in ['DATE', 'ADDRESS', 'PHONE_NUMBER']]
    
    # Count occurence of each entity
    date = address = phone = 0
    for entity in entities:
        if language_v1.Entity.Type(entity.type_).name == 'DATE' :
            date += 1
        elif language_v1.Entity.Type(entity.type_).name == "ADDRESS" :
            address += 1
        elif language_v1.Entity.Type(entity.type_).name == "PHONE_NUMBER" :
            phone += 1
       
    count = [len(names), address, date, phone]     
    # entity_texts += stanza_name
    entity_texts += names

    return entity_texts, count

def print_stats(count) :
    
    print ("Number of name censored - ", count[0])
    print ("Number of address censored - ", count[1])
    print ("Number of date censored - ", count[2])
    print ("Number of phone no. censored - ", count[3])

def detect_information(text):
    # Extract entities using Google Cloud Natural Language API
    entities, count = analyze_entities(text)

    # Replace entities with Unicode full block characters
    text = replace_with_blocks(text, entities)
    
    # Print stats
    print_stats(count)

    return text

def process_files(file_paths, output_dir):
    
    # Load the English model
    # stanza_nlp = stanza.Pipeline('en', processors='tokenize,ner')

    for file_path in file_paths:
        print(f"\nProcessing file: {file_path}")
        try:
            # Read the text file
            with open(file_path, 'r') as file:
                text_content = file.read()

            # Detect information from the text and replace with full block characters
            modified_text = detect_information(text_content)

            # Generate the output file path with the .censored suffix
            output_file_name = os.path.basename(file_path) + ".censored"
            output_file_path = os.path.join(output_dir, output_file_name)
            
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Write the modified text to the output file
            with open(output_file_path, 'w') as output_file:
                output_file.write(modified_text)

            print(f"Output file saved to: {output_file_path}")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Censor files based on specified entity types.")
    parser.add_argument("--input", nargs="+", help="Glob patterns representing input files.")
    parser.add_argument("--output", required=True, help="Directory to store censored files.")
    parser.add_argument("--names", action="store_true", help="Censor names.")
    parser.add_argument("--dates", action="store_true", help="Censor dates.")
    parser.add_argument("--phones", action="store_true", help="Censor phone numbers.")
    parser.add_argument("--address", action="store_true", help="Censor addresses.")
    parser.add_argument("--stats", choices=["stdout", "stderr"], default="stderr", help="Output statistics to stdout or stderr.")
    
    args = parser.parse_args()

    if not args.input:
        print("Please provide input files using --input flag.")
    else:
        # Use the glob pattern to get a list of text files
        file_paths = []
        for file_glob in args.input:
            file_paths.extend(glob.glob(os.path.join('./', file_glob)))

        if not file_paths:
            print("No matching files found with the specified patterns.")
        else:
            # Create the output directory if it doesn't exist
            os.makedirs(args.output, exist_ok=True)

            # Process the files based on the specified censor flags
            censor_flags = {"names": args.names, "dates": args.dates, "phones": args.phones, "address": args.address}
            selected_flags = [flag for flag, value in censor_flags.items() if value]

            if selected_flags:
                process_files(file_paths, args.output)
            else:
                print("Please specify at least one censor flag (--names, --dates, --phones, --address).")
