from bs4 import BeautifulSoup
import requests

url = "https://medium.com/age-of-awareness/how-the-pandemic-affects-our-brain-and-mental-health-ae2ec0a9fc1d"
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        members_only = soup.find('p', string='Member-only story').get_text()
        print(members_only)
    except:
        members_only = "N/A"
    
    if "Member-only story" in members_only:
        print("'Member-only story' found on the page!")
        
        new_url = "https://freedium.cfd/" + url
        response = requests.get(new_url)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            title = soup.find('title').text
            print("Page Title:", title)
            articles = soup.find_all('p', class_='leading-8')
            for article in articles:
                print(article.text)
        else:
            print(f"Failed to retrieve the freedium page: {response.status_code}")
    else:
        articles = soup.find_all('p', class_='pw-post-body-paragraph')
        for article in articles:
            print(article.text)
else:
    print(f"Failed to retrieve the page: {response.status_code}")
    