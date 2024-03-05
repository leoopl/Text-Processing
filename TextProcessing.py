import json
import re
import string
import nltk
import codecs
import contractions
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from emo_unicode import UNICODE_EMO
from emoticons import EMOTICONS
from chat_abbreviations import chat_words_str

# n_rare_words = 10
# RAREWORDS = set([w for (w, wc) in cnt.most_common()[:-n_rare_words-1:-1]])
# def remove_rarewords(text):
#     """custom function to remove the rare words"""
#     return " ".join([word for word in str(text).split() if word not in RAREWORDS])


def remove_emoji(string):
    """
    Function to removes all the emojis in a text.
    """
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def remove_emoticons(text):
    """
    Function to removes all the emoticons in a text.
    """
    emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in EMOTICONS) + u')')
    return emoticon_pattern.sub(r'', text)

def remove_urls(text):
    """
    Function to removes all the URL in a text.
    """
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_html(text):
    """
    Function to removes all the HTML Tags in a text.
    """
    html_pattern = re.compile('<.*?>')
    return html_pattern.sub(r'', text)

def remove_only_mentions(str_input: str) -> str:
    """
    Function to removes all the mentions/users tags in a text.
    """
    result = re.fullmatch(r"^[\s]*@\b[\S]+\b[\s]*$", str_input)
    return "" if result else str_input

def remove_codeblocks(str_input: str) -> str:
    """
    Function that removes all code blocks that have triple backticks ``` before and after the code.
    """
    result = re.sub(r"```[^```]*```", "", str_input)
    return re.sub(r"`[^`]*`", "", str_input)

STOPWORDS = set(stopwords.words('english'))
def remove_stopwords(text):
    """
    Function to removes stopwords in a text.
    """
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])

def remove_punctuation(text):
    """
    Function that removes all punctuation from a text.
    """
    return text.translate(str.maketrans('', '', string.punctuation))

def convert_emojis(text):
    """
    Function that convert emojis to text.
    """
    for emot in UNICODE_EMO:
        text = re.sub(r'('+emot+')', "_".join(UNICODE_EMO[emot].replace(",","").replace(":","").split()), text)
    return text

def remove_nonascii_characters(str_input: str) -> str:
    """
    Function that removes non ASCII characters in a text.
    """
    result = codecs.encode(str_input, "utf-8")
    return result.decode("ascii", "ignore")

def convert_emoticons(text):
    """
    Function that convert emoticons to text.
    """
    for emot in EMOTICONS:
        text = re.sub(u'('+emot+')', "_".join(EMOTICONS[emot].replace(",","").split()), text)
    return text

stemmer = PorterStemmer()
def stem_words(text):
    """
    Function to stem words in a text.
    """
    return " ".join([stemmer.stem(word) for word in text.split()])

lemmatizer = WordNetLemmatizer()
wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV}
def lemmatize_words(text):
    """
    Function to lemmatize words in a text.
    """
    pos_tagged_text = nltk.pos_tag(text.split())
    return " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])

chat_words_map_dict = {}
def chat_words_conversion(text):
    """
    Function to convert chat abbreviations to a full text.
    """
    global chat_words_list  # Indica que a variável é global
    chat_words_list = []
    for line in chat_words_str.split("\n"):
        if line != "":
            cw = line.split("=")[0]
            cw_expanded = line.split("=")[1]
            chat_words_list.append(cw)
            chat_words_map_dict[cw] = cw_expanded
    chat_words_list = set(chat_words_list)


    new_text = []
    for w in text.split():
        if w.upper() in chat_words_list:
            new_text.append(chat_words_map_dict[w.upper()])
        else:
            new_text.append(w)
    return " ".join(new_text)

spell = SpellChecker()
def correct_spellings(text):
    """
    Function to correct spellings in a text.
    """
    corrected_text = []
    misspelled_words = spell.unknown(text.split())
    for word in text.split():
        if word in misspelled_words:
            corrected_text.append(spell.correction(word))
        else:
            corrected_text.append(word)
    return " ".join(corrected_text)

def remove_quotes(text):
    """
    Function to remove Github quotes, that start with '>' character.
    """
    filtered_lines = []
    lines = text.splitlines()
    for line in lines:
        if not line.startswith('>'):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

collections = ['bitcoin-bitcoin.comments']

for collection in collections:
    comments_collection = open(collection + '.json', encoding='utf-8')
    data = json.load(comments_collection)

    txt_file = open(collection + '.txt', 'w', encoding='utf-8')

    size = len(data)
    count = 1


    for comment in data:
        # Quotes removal
        text = remove_quotes(comment['body'])
        # Words with numbers removal (PR and issue hash)
        text = re.sub(r'\w*\d\w*', '', text).strip()
        # Lower case
        text = text.lower()
        # URL removal
        text = remove_urls(text)
        # HTML code removal
        text = remove_html(text)
        # Codeblocks removal
        text = remove_codeblocks(text)
        # Expand contractions
        text = contractions.fix(text)
        # Nonascii characters removal
        text = remove_nonascii_characters(text)
        # Punctuation removal
        text = remove_punctuation(text)
        # Stopwords removal
        text = remove_stopwords(text)
        # Mentions removal
        text = remove_only_mentions(text)
        # Convert chat word abbreviation
        text = chat_words_conversion(text)
        # Convert emojis to text
        text = convert_emojis(text)
        # Convert emoticons to text
        text = convert_emoticons(text)
        # Lemmatization
        text = lemmatize_words(text)
        # Stemming
        text = stem_words(text)
        # Break line, multiples space, tab removal
        text = " ".join(text.split())

        print(str(count) + '/' + str(size) + ' comments processed')
        count += 1
        
        txt_file.write(str(comment["id"]) + '\t' + text + '\n')

    txt_file.close()