import json
import re
import string
import nltk
import codecs
import contractions
import emoji
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from emo_unicode import EMOTICONS_EMO
from emo_unicode import UNICODE_EMOJI_ALIAS
from chat_abbreviations import chat_words_str


class CleanDATA:
    def __init__(self):
        self.collections = ['test.comments']

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
        Function that removes comments that contain only mentions.
        """
        result = re.fullmatch(r"^[\s]*@\b[\S]+\b[\s]*$", str_input)
        return "" if result else str_input

    def remove_codeblocks(self, str_input: str) -> str:
        """
        Function that removes all code blocks that have triple backticks ``` before and after the code.
        """
        result = re.sub(r"```[^```]*```", "", str_input)
        return re.sub(r"`[^`]*`", "", str_input)

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
        return text.translate(str.maketrans('', '', string.punctuation))

    def convert_emojis(self, text):
        """
        Function that convert emojis to text. !!!!!!!!!!!!!!!!!
        """
        for emot in UNICODE_EMOJI_ALIAS:
            text = re.sub(r'('+emot+')', " ".join(UNICODE_EMOJI_ALIAS[emot].replace(",","").replace(":","").split('_')), text)
        return text

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
        wordnet_map = {"N":wordnet.NOUN, "V":wordnet.VERB, "J":wordnet.ADJ, "R":wordnet.ADV}
        pos_tagged_text = nltk.pos_tag(text.split())
        return " ".join([lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text])

    def chat_words_conversion(self, text):
        """
        Function to convert chat abbreviations to a full text.
        """
        chat_words_map_dict = {}
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

    def correct_spellings(self, text):
        """
        Function to correct spellings in a text.
        """
        spell = SpellChecker()
        incorrect_words = spell.unknown(text.split())

        for word in incorrect_words:
            suggestion = spell.correction(word)
            if suggestion is not None:
                text = text.replace(word, suggestion)
        return text

    def remove_quotes(self, text):
        """
        Function to remove Github quotes, that start with '>' character.
        """
        filtered_lines = []
        lines = text.splitlines()
        for line in lines:
            if not line.startswith('>'):
                filtered_lines.append(line)
        return "\n".join(filtered_lines)

    def text_processing(self, collections: list):
        """
        Function to process the text in each collection.
        """
        for collection in collections:
            comments_collection = open(collection + '.json', encoding='utf-8')
            data = json.load(comments_collection)

            txt_file = open(collection + '.txt', 'w', encoding='utf-8')

            size = len(data)
            count = 1


            for comment in data:
                # Quotes removal
                text = self.remove_quotes(comment['body'])
                # URL removal
                text = self.remove_urls(text)
                # HTML code removal
                text = self.remove_html(text)
                # Mentions removal
                text = self.remove_only_mentions(text)
                # Convert emojis to text
                text = emoji.demojize(text, delimiters=(" ", " ")).replace('_', ' ')
                # Convert emoticons to text
                text = self.convert_emoticons(text)
                # Words with numbers removal (PR and issue hash)
                text = re.sub(r'\w*\d\w*', '', text).strip()
                # Lower case
                text = text.lower()
                # Codeblocks removal
                text = self.remove_codeblocks(text)
                # Expand contractions
                text = contractions.fix(text)
                # Nonascii characters removal
                text = self.remove_nonascii_characters(text)
                # Punctuation removal
                text = self.remove_punctuation(text)
                # Stopwords removal
                # text = self.remove_stopwords(text)
                # Convert chat word abbreviation
                text = self.chat_words_conversion(text)
                # Stemming
                text = self.stem_words(text)
                # Lemmatization
                text = self.lemmatize_words(text)
                # Correct the spelling of words
                text = self.correct_spellings(text)
                # Break line, multiples space, tab removal
                text = " ".join(text.split())

                print(str(count) + '/' + str(size) + ' comments processed')
                count += 1

                if text == '':
                    continue
                
                txt_file.write(str(comment["id"]) + '\t' + text + '\n')

            txt_file.close()


clean_data = CleanDATA()
clean_data.text_processing(clean_data.collections)