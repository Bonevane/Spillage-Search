# import requests
# from bs4 import BeautifulSoup
# import csv
# import time as t

# # Function to check if a Medium article is member-only
# def check_medium_article(url):
#     try:
#         # Send a GET request to the URL
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()

#         # Parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Check if the page contains "member-only" indicator
#         member_only = False
#         if soup.find(string="member-only story") or soup.find(class_="meteredContent"):
#             member_only = True

#         # Extract a small description (meta description)
#         description_tag = soup.find('meta', attrs={'name': 'description'})
#         description = description_tag['content'] if description_tag else 'No description available'

#         return member_only, description

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching URL {url}: {e}")
#         return None, None

# # Function to write results to a CSV file
# def write_to_csv(data, filename="scraped.csv"):
#     try:
#         with open(filename, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             # Write the header
#             writer.writerow(["ID", "URL", "Description", "Member Only"])
#             # Write the data
#             writer.writerows(data)
#         print(f"Data successfully written to {filename}")
#     except Exception as e:
#         print(f"Error writing to CSV: {e}")

# # Function to read URLs from a CSV file
# def read_from_csv(input_filename):
#     try:
#         with open(input_filename, mode='r', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             return [row for row in reader]
#     except Exception as e:
#         print(f"Error reading from CSV: {e}")
#         return []

# # Main function
# def main():
#     input_filename = "indexes/processed.csv"  # Input CSV file with header ID, title, url, authors, timestamp, tags
#     output_filename = "scraped.csv"  # Output CSV file

#     # Read data from the input CSV
#     articles = read_from_csv(input_filename)

#     data = []
    
#     for idx, article in enumerate(articles):
#         a = t.time()
#         if idx >= 5:  # Limit to processing 5 URLs
#             print("Reached limit of 5 articles. Stopping.")
#             break

#         article_id = article.get("ID", "Unknown")
#         url = article.get("url", "")

#         if not url:
#             print(f"Skipping article with ID {article_id} due to missing URL")
#             data.append([article_id, "", "Missing URL", "Unknown"])
#             continue

#         print(f"Processing article ID {article_id}: {url}")
#         member_only, description = check_medium_article(url)

#         if member_only is not None:
#             data.append([article_id, url, description, "Yes" if member_only else "No"])
#         else:
#             data.append([article_id, url, "Error fetching data", "Unknown"])
        
#         print(f"Time taken for article {article_id}: {t.time() - a} seconds")

#     # Write the collected data to a CSV file
#     write_to_csv(data, output_filename)

# if __name__ == "__main__":
#     main()


import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
import csv
import os
import time as t

# Asynchronous function to check if a Medium article is member-only
async def check_medium_article(session, article_id, url):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()

            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')

            # Check if the page contains "member-only" indicator
            member_only = False
            if soup.find(string="member-only story") or soup.find(class_="meteredContent"):
                member_only = True

            # Extract a small description (meta description)
            description_tag = soup.find('meta', attrs={'name': 'description'})
            description = description_tag['content'] if description_tag else 'No description available'
            
            # Extract the thumbnail URL
            thumbnail_tag = soup.find('meta', property='og:image')
            url = thumbnail_tag['content'] if thumbnail_tag else 'No thumbnail available'

            return [article_id, url, description, "Yes" if member_only else "No", response.status]
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return [article_id, "Error fetching thumbnail", "Error fetching data", "Unknown", response.status if 'response' in locals() else 'No response']


def scrape_article(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if the page contains "member-only" indicator
        member_only = False
        if soup.find(string="member-only story") or soup.find(class_="meteredContent"):
            member_only = True

        # Extract a small description (meta description)
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag else 'No description available'

        # Extract the thumbnail URL
        thumbnail_tag = soup.find('meta', property='og:image')
        thumbnail_url = thumbnail_tag['content'] if thumbnail_tag else 'No thumbnail available'

        return member_only, description, thumbnail_url, response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None, None, None, response.status_code if 'response' in locals() else None

# Asynchronous function to process multiple URLs
async def process_articles(articles, output_filename, limit=5, start=0):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for idx, article in enumerate(articles[start:limit]):
            article_id = article.get("ID", "Unknown")
            url = article.get("url", "")

            if not url:
                print(f"Skipping article with ID {article_id} due to missing URL")
                tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Dummy task to keep index alignment
                continue

            print(f"Processing article ID {article_id}: {url}")
            tasks.append(check_medium_article(session, article_id, url))

        results = await asyncio.gather(*tasks)
        write_to_csv([result for result in results if result], output_filename)

# Function to write results to a CSV file
def write_to_csv(data, filename="medium_articles.csv"):
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header
            if os.stat(filename).st_size == 0:
                writer.writerow(["ID", "URL", "Description", "Member Only", "Code"])
            # Write the data
            writer.writerows(data)
        print(f"Data successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# Function to read URLs from a CSV file
def read_from_csv(input_filename):
    try:
        with open(input_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except Exception as e:
        print(f"Error reading from CSV: {e}")
        return []

# Function to update an existing CSV file
def update_csv(input_filename, processed_file, output_filename):
    try:
        with open(processed_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            processes_rows = list(reader)
            
        with open(input_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        article_id = 0
        
        updated_rows = []
        for row in rows:
            article_id = row.get("ID", 0)
            url = processes_rows[int(article_id) - 1].get("url", "")
            status = row.get("Member Only", "Unknown")
            code = row.get("Code", "400")

            if code not in ["410", "200", "404"]:
                if code == "429":
                    print("Rate limit exceeded. Skipping remaining articles.")
                    break
                
                print(f"Rescraping article ID {article_id}: {url}")
                member_only, description, thumbnail_url, status_code = scrape_article(url)

                if member_only is not None:
                    updated_rows.append({
                        "ID": article_id,
                        "URL": thumbnail_url,
                        "Description": description,
                        "Member Only": "Yes" if member_only else "No",
                        "Code": status_code
                    })
                else:
                    updated_rows.append({
                        "ID": article_id,
                        "URL": "Error fetching thumbnail",
                        "Description": "Error fetching data",
                        "Member Only": "Unknown",
                        "Code": status_code
                    })
            else:
                updated_rows.append({
                    "ID": row["ID"],
                    "URL": row["URL"],
                    "Description": row["Description"],
                    "Member Only": row["Member Only"],
                    "Code": 200
                })

        # Write the updated rows back to the output file
        with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "URL", "Description", "Member Only", "Code"])
            writer.writeheader()
            writer.writerows(updated_rows)
        print(f"Updated data successfully written to {output_filename}")
        
        return article_id

    except Exception as e:
        print(f"Error updating CSV: {e}")

# Main function
def main():
    input_filename = "indexes/processed.csv"  # Input CSV file with header ID, title, url, authors, timestamp, tags
    output_filename = "scraped.csv"  # Output CSV file

    # Read data from the input CSV
    articles = read_from_csv(input_filename)
        
    latest_article_id = int(update_csv(output_filename, input_filename, output_filename))
    
    for i in range(latest_article_id, len(articles) - 6, 5):
        a = t.time()
        # Process articles asynchronously
        asyncio.run(process_articles(articles[i:i+5], output_filename))
        print(t.time() - a)

if __name__ == "__main__":
    main()
