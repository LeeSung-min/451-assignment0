from google import genai
import trafilatura
from bs4 import BeautifulSoup
import requests
import json
import argparse

# url in command line
parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
args = parser.parse_args()

url = args.url

# fetch HTML & get text w Trafilatura
r = requests.get(url)
html = r.text

text = trafilatura.extract(html, url=url)

# beautiful soup fallback if empty
if not text:

    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup (["script","style","noscript","header","footer"]):
        tag.decompose()
    
    text = soup.get_text()

client = genai.Client()





