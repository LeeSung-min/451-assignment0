from google import genai
import trafilatura
from bs4 import BeautifulSoup
import requests
import json
import argparse
from google.genai import types

# url in command line
parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
args = parser.parse_args()

url = args.url

#fix for article blocks

headers = {
    "User-Agent" : "Mozilla/5.0",
    "Referer": "https://www.google.com"
}

# fetch HTML & get text w Trafilatura
r = requests.get(url, headers=headers, timeout= 20)
r.raise_for_status()
html = r.text

text = trafilatura.extract(html, url=url)

# beautiful soup fallback if empty
if not text:

    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup (["script","style","noscript","header","footer"]):
        tag.decompose()
    
    text = soup.get_text()

# use gemini for summarization
client = genai.Client()

prompt = f"""

Source Text to summarize: {text}

You are to take a provided piece of text and summarize its contents.
Your job is to have the most accurate, factual, and eloquent summary produced, 
and you are to output only in the format of JSON with no extra content.
You may not invent or include facts that are not provided by the source text.

Your task is to:
summarize the given text into three sentences,
extract at least 5 key words or phrases that is relevant to the text or are important concepts in the text and make sure that there are no duplicate words in the 5 key terms,
and lastly provide the source URL.

The output JSON should be in this format:
{{
    "From URL": "{url}",
    "Summary": "Only one paragraph summary that is exactly 3 sentences.",
    "Keywords": ["At least 5 Keyword or phrases that represent core concepts of the text"],
    "References": "{url}": 

}}
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature = 0.2,
        top_p = 0.9,
        top_k = 40,
        max_output_tokens = 2048
    )
)

try:
    data = json.loads(response.text)
    output = {
        "From URL": url,
        "Summary": data["summary"],
        "Keywords": data["keywords"],
        "References": url
    }

    print(json.dumps(output))

except Exception:
    print(json.dummps({
        "From URL" : url,
        "Error" : "Error in summarizing text, could not return JSON."
    }))



