
# Python Functions to Text Processing

Set of functions designed for text preprocessing.

Code reads a JSON referring to a collection of comments from Github issues and reviews and returns a .txt with the id and the treated comment.


## Functions

- Function to removes all the emojis in a text.
- Function to removes all the emoticons in a text.
- Function to removes all the URL in a text.
- Function to removes all the HTML Tags in a text.
- Function that removes comments that contain only a mentions.
- Function that removes all code blocks that have triple backticks ``` before and after the code.
- Function to removes stopwords in a text.
- Function that removes all punctuation from a text.
- Function that removes non ASCII characters in a text.
- Function that convert emoticons to text.
- Function to convert chat abbreviations to a full text.
- Function to correct spellings in a text. (autocorrect library)
- Function to remove Github quotes, that start with '>' character.
- Stemming Function
- Lemmatization Function

### The code also does:

- Remove any mentions in a text (e.g. @leoopl)
- Remove words whos contains number and words (like commit hash)
- Convert emojis to text (emoji library)
- Expand contractions (contractions library)
- Remove break line, multiples space, tab...

