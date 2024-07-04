import csv
import json
import re
import string
import nltk
import codecs
import contractions
import emoji
import os
import unicodedata
import pandas as pd
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from autocorrect import Speller
from emo_unicode import EMOTICONS_EMO
from emo_unicode import UNICODE_EMOJI_ALIAS
from chat_abbreviations import chat_words_str


class CleanDATA:
    def __init__(self):
        # self.collections = ['test.comments']
        self.collections = ['mui-material-ui.comments', 'mui-material-ui.reviews', 'opencv-opencv.comments', 'opencv-opencv.reviews', 'rails-rails.comments', 'rails-rails.reviews', 'symfony-symfony.comments', 'symfony-symfony.reviews', 'tensorflow-tensorflow.comments', 'tensorflow-tensorflow.reviews', 'godotengine-godot.comments', 'godotengine-godot.reviews', 'hashicorp-terraform.comments', 'hashicorp-terraform.reviews', 'microsoft-vscode.comments', 'microsoft-vscode.reviews', 'moby-moby.comments', 'moby-moby.reviews', 'angular-angular.comments', 'angular-angular.reviews', 'bitcoin-bitcoin.comments', 'bitcoin-bitcoin.reviews', 'cockroachdb-cockroach.comments', 'cockroachdb-cockroach.reviews', 'facebook-react.comments', 'facebook-react.reviews']
        self.folder_path = os.path.join(os.path.dirname(__file__), 'data')
        self.punctuation_table = str.maketrans('', '', string.punctuation)

    # def remove_rarewords(self, text):
    #   """custom function to remove the rare words"""
    #   n_rare_words = 10
    #   RAREWORDS = set([w for (w, wc) in cnt.most_common()[:-n_rare_words-1:-1]])
    #   return " ".join([word for word in str(text).split() if word not in RAREWORDS])


    def remove_emoji(self, text):
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
        return emoji_pattern.sub(r'', text)

    def remove_emoticons(self, text):
        """
        Function to removes all the emoticons in a text.
        """
        emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in EMOTICONS_EMO) + u')')
        return emoticon_pattern.sub(r'', text)

    def remove_urls(self, text):
        """
        Function to removes all the URL in a text.
        """
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)

    def remove_html(self, text):
        """
        Function to removes all the HTML Tags in a text.
        """
        html_pattern = re.compile('<.*?>')
        return html_pattern.sub(r'', text)

    def remove_only_mentions(self, str_input: str) -> str:
        """
        Function that removes comments that contain only a mentions.
        """
        result = re.fullmatch(r"^[\s]*@\b[\S]+\b[\s]*$", str_input)
        return "" if result else str_input

    def remove_codeblocks(self, str_input: str) -> str:
        """
        Function that removes all code blocks that have triple backticks ``` before and after the code.
        """
        return re.sub(r"```.*?```", "", str_input, flags=re.DOTALL)

    def remove_stopwords(self, text):
        """
        Function to removes stopwords in a text.
        """
        STOPWORDS = set(stopwords.words('english'))
        return " ".join([word for word in str(text).split() if word not in STOPWORDS])

    def remove_punctuation(self, text):
        """
        Function that removes all punctuation from a text.
        """
        return text.translate(self.punctuation_table)

    def remove_nonascii_characters(self, str_input: str) -> str:
        """
        Function that removes non ASCII characters in a text.
        """
        result = codecs.encode(str_input, "utf-8")
        return result.decode("ascii", "ignore")


    def convert_emoticons(self, text):
        """
        Function that convert emoticons to text.
        """
        emoticon_dict = EMOTICONS_EMO
        regex_pattern = re.compile('|'.join(re.escape(emoticon) for emoticon in emoticon_dict.keys()))
        return regex_pattern.sub(lambda match: emoticon_dict[match.group(0)], text)

    def stem_words(self, text):
        """
        Function to stem words in a text.
        """
        stemmer = PorterStemmer()
        return " ".join([stemmer.stem(word) for word in text.split()])

    def lemmatize_words(self, text):
        """
        Function to lemmatize words in a text.
        """
        lemmatizer = WordNetLemmatizer()
        wordnet_map = {"N": wordnet.NOUN, "V": wordnet.VERB, "J": wordnet.ADJ, "R": wordnet.ADV}
        pos_tagged_text = nltk.pos_tag(nltk.word_tokenize(text))
        return " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])

    def chat_words_conversion(self, text):
        """
        Function to convert chat abbreviations to a full text.
        """
        chat_words_map_dict = {}
        
        for line in chat_words_str.split("\n"):
            if line.strip():
                cw, cw_expanded = line.split("=")
                chat_words_map_dict[cw.strip()] = cw_expanded.strip()

        chat_words_regex = r"\b(" + "|".join(re.escape(word) for word in chat_words_map_dict.keys()) + r")\b"
        regex_pattern = re.compile(chat_words_regex)

        return regex_pattern.sub(lambda x: chat_words_map_dict[x.group()], text)

    def correct_spellings(self, text):
        """
        Function to correct spellings in a text. spell = Speller(fast=True)
        """
        spell = Speller(fast=True)
        corrected_words = [spell(word) for word in text.split()]
        return ' '.join(corrected_words)

    def remove_quotes(self, text):
        """
        Function to remove Github quotes, that start with '>' character.
        """
        filtered_lines = [line for line in text.splitlines() if not line.startswith('>')]
        return "\n".join(filtered_lines)
    
    def comments_count(self, collections: list):
        """
        Function to count the total of comments.
        """
        comments_count = 0
        txt_path = os.path.join(os.path.dirname(__file__), 'NewDataCleanResults')
        for collection in collections:
            file_path = os.path.join(txt_path, collection + '.txt')
            with open(file_path, 'r', encoding='utf-8') as file:
                comments_count += len(file.readlines())
        print('Total comments: ' + str(comments_count)) 

    def text_processing(self, collections: list):
        """
        Function to process the text in each collection.
        """
        if not os.path.exists('NewDataCleanResults'):
            os.makedirs('NewDataCleanResults')

        for collection in collections:
            file_path = os.path.join(self.folder_path, collection + '.json')
            comments_collection = open(file_path, encoding='utf-8')
            data = json.load(comments_collection)

            # Create a dataframe from the json file to remove duplicates from the comments
            df = pd.DataFrame(data)
            df = df.drop_duplicates(subset=['body'])

            csv_file = open(os.path.join('NewDataCleanResults', collection + '.csv'), 'w', encoding='utf-8')
            writer = csv.writer(csv_file)

            print('Processing comments from ' + collection + '...')

            # Quotes removal
            df['body'] = df['body'].apply(lambda text: self.remove_quotes(text))
            # URL removal
            df['body'] = df['body'].apply(lambda text: self.remove_urls(text))
            # HTML code removal
            df['body'] = df['body'].apply(lambda text: self.remove_html(text))
            # Codeblocks removal
            df['body'] = df['body'].apply(lambda text: self.remove_codeblocks(text))
            # Mention removal
            df['body'] = df['body'].apply(lambda text: re.sub(r'@[\w]+', '', text))
            # Convert emojis to text
            df['body'] = df['body'].apply(lambda text: emoji.demojize(text, delimiters=(" ", " ")).replace('_', ' '))
            # Convert emoticons to text
            # df['body'] = df['body'].apply(lambda text: self.convert_emoticons(text))
            # Words with numbers removal (PR and issue hash)
            df['body'] = df['body'].apply(lambda text: re.sub(r'\w*\d\w*', '', text).strip())
            # Lower case
            # df['body'] = df['body'].apply(lambda text: text.lower())
            # Convert chat word abbreviation
            df['body'] = df['body'].apply(lambda text: self.chat_words_conversion(text))
            # Expand contractions
            df['body'] = df['body'].apply(lambda text: contractions.fix(text))
            # Nonascii characters removal
            # df['body'] = df['body'].apply(lambda text: self.remove_nonascii_characters(text))
            # Punctuation removal
            # df['body'] = df['body'].apply(lambda text: self.remove_punctuation(text))
            # Lemmatization
            # df['body'] = df['body'].apply(lambda text: self.lemmatize_words(text))
            # Correct the spelling of words
            # df['body'] = df['body'].apply(lambda text: self.correct_spellings(text))
            # Break line, multiples space, tab removal
            df['body'] = df['body'].apply(lambda text: " ".join(text.split()))
            #     # Stopwords removal
            #     df['body'] = df['body'].apply(lambda text: self.remove_stopwords(text))
            #     # Stemming
            #     df['body'] = df['body'].apply(lambda text: self.stem_words(text))
            # Remove comments without letters
            df = df[df['body'].apply(lambda s: bool(re.search(r'[a-zA-Z]', s)))]

            df = df.drop_duplicates(subset=['body'])
            size = len(df)

            for index, row in df.iterrows():
              if row['body'] == '':
                continue
              writer.writerow([str(row["id"]) + '\t' + row['body']])
            #   txt_file.write(str(row["id"]) + '\t' + row['body'] + '\n')
            print(str(size) + ' comments processed')
            # txt_file.close()


clean_data = CleanDATA()
clean_data.comments_count(clean_data.collections)