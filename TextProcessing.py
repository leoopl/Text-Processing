import json
import re
import string
import nltk
import codecs
nltk.download('stopwords')
from nltk.corpus import stopwords
from emo_unicode import UNICODE_EMO
from emoticons import EMOTICONS

def remove_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_html(text):
    html_pattern = re.compile('<.*?>')
    return html_pattern.sub(r'', text)

def remove_only_mentions(str_input: str) -> str:
        result = re.fullmatch(r"^[\s]*@\b[\S]+\b[\s]*$", str_input)
        return "" if result else str_input

def remove_codeblocks(str_input: str) -> str:
        result = re.sub(r"```[^```]*```", "", str_input)
        return re.sub(r"`[^`]*`", "", str_input)

STOPWORDS = set(stopwords.words('english'))
def remove_stopwords(text):
    """custom function to remove the stopwords"""
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def convert_emojis(text):
    for emot in UNICODE_EMO:
        text = re.sub(r'('+emot+')', "_".join(UNICODE_EMO[emot].replace(",","").replace(":","").split()), text)
    return text

def remove_nonascii_characters(str_input: str) -> str:
        result = codecs.encode(str_input, "utf-8")
        return result.decode("ascii", "ignore")

def convert_emoticons(text):
    for emot in EMOTICONS:
        text = re.sub(u'('+emot+')', "_".join(EMOTICONS[emot].replace(",","").split()), text)
    return text

collections = ['bitcoin-bitcoin.comments']

for collection in collections:
  comments_collection = open(collection + '.json', encoding='utf-8')
  data = json.load(comments_collection)

  txt_file = open(collection + '.txt', 'w', encoding='utf-8')


  for comment in data:
    # Break line removal
    text = ' '.join([line.strip() for line in comment['body'].strip().splitlines() if line.strip()])
    # Lower case
    text = text.lower()
    # URL removal
    text = remove_urls(text)
    # HTML code removal
    text = remove_html(text)
    # Punctuation removal
    text = remove_punctuation(text)
    # Stopwords removal
    text = remove_stopwords(text)
    # Codeblocks removal
    text = remove_codeblocks(text)
    # Mentions removal
    text = remove_only_mentions(text)
    # Convert emojis to text
    text = convert_emojis(text)
    # Nonascii characters removal
    text = remove_nonascii_characters(text)
    # Convert emoticons to text
    text = convert_emoticons(text)

    ## Stemming and Lemmatization ??????
    
    txt_file.write(str(comment["id"]) + '\t' + text + '\n')

  txt_file.close()