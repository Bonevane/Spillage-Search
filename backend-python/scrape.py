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

from nltk.stem import WordNetLemmatizer
import os
import csv

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

stemmer = PorterStemmer()

def preprocess_word(word):
    """
    Preprocess a word by lemmatizing and then stemming.
    This ensures the word is reduced to its root form.
    """
    # Lemmatize the word (context-aware)
    lemmatized_word = lemmatizer.lemmatize(word.lower())

    # Stem the word (handle suffix removal)
    stemmed_word = stemmer.stem(lemmatized_word)
    return stemmed_word
    return lemmatized_word

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

    # Preprocess and deduplicate words
    unique_words = set(preprocess_word(w) for w in filtered_words)

    # Add new words to the lexicon
    new_entries = []
    for word in unique_words:
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
    # for range_key, count in range_counts.items():
    #     print(f"Words starting with {range_key}: {count}")


def extract_filtered_words_from_url(url):
    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z ]+'  # Regex to clean non-alphabet characters

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        filtered_words = []

        # Process the title
        title = soup.find('title').text
        title_clean = re.sub(pattern, ' ', title)
        title_token = word_tokenize(title_clean)
        filtered_words.extend(
            preprocess_word(w) for w in title_token if w.lower() not in stop_words
        )

        # Process body content
        articles = soup.find_all('p')
        for article in articles:
            text = re.sub(pattern, ' ', article.text)
            word_tokens = word_tokenize(text)
            filtered_words.extend(
                preprocess_word(w) for w in word_tokens if w.lower() not in stop_words
            )

        # Deduplicate and save words
        filtered_words = list(set(filtered_words))  # Remove duplicates
        save_words_to_lexicon(filtered_words)
    else:
        print(f"Failed to retrieve the page: {response.status_code}")



csv_file = "D:\\SEECS\\3rd Semester\\DSA\\Sem\\small dataset\\csv_small_dataset.csv"  # Path to your CSV file


column_name = 'url'  # Name of the column you want to extract

column_data = read_column_from_csv(csv_file, column_name)

# for url in column_data:
#     extract_filtered_words(url)
for url in column_data:
# url = 'https://medium.com/invisible-illness/mental-note-vol-24-969b6a42443f'
    print(url)
    extract_filtered_words_from_url(url)

# response = requests.get(url)
# stop_words = set(stopwords.words('english'))
# pattern = r"[,.!?'\-\-\—\"()“”’;:\[\]\d]"
# lemmatizer = WordNetLemmatizer()

# if response.status_code == 200:
#     html_content = response.text
#     soup = BeautifulSoup(html_content, 'html.parser')
#     filtered_words = []

#     try:
#         members_only = soup.find('p', string='Member-only story').get_text()
#         print(members_only)
#     except:
#         members_only = "N/A"
    
#     if "Member-only story" in members_only:
#         print("'Member-only story' found on the page!")
        
#         new_url = "https://freedium.cfd/" + url
#         response = requests.get(new_url)
        
#         if response.status_code == 200:
#             html_content = response.text
#             soup = BeautifulSoup(html_content, 'html.parser')

#             title = soup.find('title').text
#             print("Page Title:", title)
#             articles = soup.find_all('p', class_='leading-8')
#             for article in articles:
#                 text = re.sub(pattern, '', article.text)
#                 word_tokens = word_tokenize(text)
#                 filtered_words.extend(lemmatizer.lemmatize(w.lower()) for w in word_tokens if w.lower() not in stop_words)
#             print(filtered_words)
#         else:
#             print(f"Failed to retrieve the freedium page: {response.status_code}")
#     else:
#         articles = soup.find_all('p', class_='pw-post-body-paragraph')
#         for article in articles:
#             text = re.sub(pattern, '', article.text)
#             word_tokens = word_tokenize(text)
#             filtered_words.extend(lemmatizer.lemmatize(w.lower()) for w in word_tokens if w.lower() not in stop_words)
#         print(filtered_words)
# else:
#     print(f"Failed to retrieve the page: {response.status_code}")
    
    
# print("Complete!")