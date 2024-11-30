from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import re
import csv
import os
import nltk
nltk.download('punkt')  # For word tokenization
nltk.download('stopwords')  # If using stop words
nltk.download('wordnet')  
nltk.download('punkt_tab')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_word(word):
    return lemmatizer.lemmatize(word.lower())

def save_words_to_lexicon(filtered_words):
    lexicon_file = 'lexicon.csv'
    id_file = 'latest_id.txt'
    lexicon_dict = {}

    # Read the latest ID from the file
    if os.path.exists(id_file):
        with open(id_file, 'r') as file:
            latest_id = int(file.read().strip())
    else:
        latest_id = 0

    # Load existing lexicon
    if os.path.exists(lexicon_file):
        with open(lexicon_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                lexicon_dict[row[1]] = int(row[0])

    # Add new words to the lexicon
    new_entries = []
    for word in filtered_words:
        if word not in lexicon_dict:
            latest_id += 1
            lexicon_dict[word] = latest_id
            new_entries.append([latest_id, word])

    # Append new entries to the CSV
    with open(lexicon_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(lexicon_file).st_size == 0:
            writer.writerow(['ID', 'Word'])
        writer.writerows(new_entries)

    # Save the latest ID
    with open(id_file, 'w') as file:
        file.write(str(latest_id))

    print("Words have been saved to the lexicon.")



def read_column_from_csv(csv_file, column_name):
    
    column_data = []
    
    print(os.getcwd())
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            column_data.append(row[column_name])  # Add the value of the specific column
            
    return column_data


def extract_filtered_words_from_csv(csv_filename):
    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z ]+' 
    chunk_size = 1000
    filtered_words = []
    
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            row_count = 0
            
            for row in reader:
                # Combine "title", "text", and "tags" columns
                combined_text = f"{row['title']} {row['text']} {row['tags']}"
                # Clean and tokenize text
                clean_text = re.sub(pattern, ' ', combined_text)
                tokens = word_tokenize(clean_text)
                # Filter out stop words, short words, and preprocess
                filtered_words.extend(
                    preprocess_word(w) for w in tokens 
                    if w.lower() not in stop_words and len(w) > 2
                )
                
                row_count += 1
                
                # Save and clear the list every chunk_size rows
                if row_count % chunk_size == 0:
                    filtered_words = list(dict.fromkeys(filtered_words))  # Deduplicate
                    save_words_to_lexicon(filtered_words)
                    filtered_words.clear()  # Clear the list to free memory
            
            # Process remaining rows (if total rows are not a multiple of chunk_size)
            if filtered_words:
                filtered_words = list(dict.fromkeys(filtered_words))  # Deduplicate
                save_words_to_lexicon(filtered_words)

    except FileNotFoundError:
        print(f"File not found: {csv_filename}")
    except KeyError as e:
        print(f"Missing column in CSV: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


csv_file = "test.csv"  # Path to your CSV file
extract_filtered_words_from_csv(csv_file)





#
#   Leftover code from earlier attempts at making barrels for the lexicon (realized we did not need this.)
#   Also scraping code that could be useful later (realized we did not [currently] need this.)
#

def count_word_ranges(filtered_words):
    # Initialize a dictionary to store counts for each range
    range_counts = defaultdict(int)

    # Define the letter ranges
    letter_ranges = [
        ('aa', 'am'), ('an', 'az'), ('ba', 'bm'), ('bn', 'bz'), ('ca', 'cm'), ('cn', 'cz'),
        ('da', 'dm'), ('dn', 'dz'), ('ea', 'em'), ('en', 'ez'), ('fa', 'fm'), ('fn', 'fz'),
        ('ga', 'gm'), ('gn', 'gz'), ('ha', 'hm'), ('hn', 'hz'), ('ia', 'im'), ('in', 'iz'),
        ('ja', 'jm'), ('jn', 'jz'), ('ka', 'km'), ('kn', 'kz'), ('la', 'lm'), ('ln', 'lz'),
        ('ma', 'mm'), ('mn', 'mz'), ('na', 'nm'), ('nn', 'nz'), ('oa', 'om'), ('on', 'oz'),
        ('pa', 'pm'), ('pn', 'pz'), ('qa', 'qm'), ('qn', 'qz'), ('ra', 'rm'), ('rn', 'rz'),
        ('sa', 'sm'), ('sn', 'sz'), ('ta', 'tm'), ('tn', 'tz'), ('ua', 'um'), ('un', 'uz'),
        ('va', 'vm'), ('vn', 'vz'), ('wa', 'wm'), ('wn', 'wz'), ('xa', 'xm'), ('xn', 'xz'),
        ('ya', 'ym'), ('yn', 'yz'), ('za', 'zm'), ('zn', 'zz')
    ]
    
    # Loop over the ranges and count words that start with letters within each range
    for start, end in letter_ranges:
        for word in filtered_words:
            if start <= word[:2] <= end:
                range_counts[start + '-' + end] += 1
    
    # Print the results
    for range_key, count in range_counts.items():
        print(f"Words starting with {range_key}: {count}")



# Old stuff, may reuse later for scraping thumbnails and other data
def extract_filtered_words_from_url(url):
    # Initialize stop words, regex pattern, and lemmatizer
    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z ]+'  #r"[,.!?'\-\-\—\"()“”…‘’;:\[\]|\\/\d]"
    lemmatizer = WordNetLemmatizer()

    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        filtered_words = []
        
        # Doing the cleanup, tokenization, lemmetization on the title
        title = soup.find('title').text
        title_clean = re.sub(pattern, '', title)
        title_token = word_tokenize(title_clean)
        filtered_words.extend(lemmatizer.lemmatize(w.lower()) for w in title_token if w.lower() not in stop_words and len(w) > 2)

        # Check if the page is a 'Member-only story'
        try:
            members_only = soup.find('p', string='Member-only story').get_text()
            print(members_only)
        except:
            members_only = "N/A"
        
        if "Member-only story" in members_only:
            print("'Member-only story' found on the page!")
            # Redirect to a new URL if it's a member-only story
            new_url = "https://freedium.cfd/" + url
            response = requests.get(new_url)
            
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                articles = soup.find_all('p', class_='leading-8')
                
                for article in articles:
                    text = re.sub(pattern, '', article.text)
                    word_tokens = word_tokenize(text)
                    filtered_words.extend(lemmatizer.lemmatize(w.lower()) for w in word_tokens if w.lower() not in stop_words and len(w) > 2)
                # print(filtered_words)
                save_words_to_lexicon(filtered_words)
            else:
                print(f"Failed to retrieve the freedium page: {response.status_code}")
        else:
            # Process the non-member-only content
            articles = soup.find_all('p', class_='pw-post-body-paragraph')
            for article in articles:
                text = re.sub(pattern, '', article.text)
                word_tokens = word_tokenize(text)
                filtered_words.extend(lemmatizer.lemmatize(w.lower()) for w in word_tokens if w.lower() not in stop_words)
            # print(filtered_words)
            save_words_to_lexicon(filtered_words)
            #count_word_ranges(filtered_words)
            #print(filtered_words.__len__())
    else:
        print(f"Failed to retrieve the page: {response.status_code}")