from autocorrect import Speller
import re
import unidecode
import nltk

# nltk.download("punkt")
# from nltk.corpus import stopwords

# stopwords = stopwords.words("english")
from contraction_map import CONTRACTION_MAP

# stoplist = set(stopwords)
# from nltk.tokenize import word_tokenize
import re
import unidecode
from bs4 import BeautifulSoup


# def removing_stopwords(text):
#     """This function will remove stopwords which doesn't add much meaning to a sentence
#        & they can be remove safely without comprimising meaning of the sentence.

#     arguments:
#          input_text: "text" of type "String".

#     return:
#         value: Text after omitted all stopwords.

#     Example:
#     Input : This is Kajal from delhi who came here to study.
#     Output : ["'This", 'Kajal', 'delhi', 'came', 'study', '.', "'"]

#     """
#     # repr() function actually gives the precise information about the string
#     text = repr(text)
#     # Text without stopwords
#     No_StopWords = [
#         word for word in word_tokenize(text) if word.lower() not in stoplist
#     ]
#     # Convert list of tokens_without_stopwords to String type.
#     words_string = " ".join(No_StopWords)
#     return words_string


# The code for removing special characters
def removing_special_characters(text):
    """Removing all the special characters except the one that is passed within
       the regex to match, as they have imp meaning in the text provided.


    arguments:
         input_text: "text" of type "String".

    return:
        value: Text with removed special characters that don't require.

    Example:
    Input : Hello, K-a-j-a-l. Thi*s is $100.05 : the payment that you will recieve! (Is this okay?)
    Output :  Hello, Kajal. This is $100.05 : the payment that you will recieve! Is this okay?

    """
    # The formatted text after removing not necessary punctuations.
    Formatted_Text = re.sub(r"[^a-zA-Z0-9:$-,%.?!]+", " ", text)
    # In the above regex expression,I am providing necessary set of punctuations that are frequent in this particular dataset.
    return Formatted_Text


# The code for lemmatization
# w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
# lemmatizer = nltk.stem.WordNetLemmatizer()


# def lemmatization(text):
#     """This function converts word to their root words
#        without explicitely cut down as done in stemming.

#     arguments:
#          input_text: "text" of type "String".

#     return:
#         value: Text having root words only, no tense form, no plural forms

#     Example:
#     Input : text reduced
#     Output :  text reduce

#     """
#     lemma = ""
#     # Converting words to their root forms
#     for w in w_tokenizer.tokenize(text):
#         lemma += lemmatizer.lemmatize(w, "v") + " "
#     return lemma


def spelling_correction(text):
    """
    This function will correct spellings.

    arguments:
         input_text: "text" of type "String".

    return:
        value: Text after corrected spellings.

    Example:
    Input : This is Oberois from Dlhi who came heree to studdy.
    Output : This is Oberoi from Delhi who came here to study.


    """
    # Check for spellings in English language
    spell = Speller(lang="en")
    Corrected_text = spell(text)
    return Corrected_text


def remove_singular_characters(input_str):
    result_str = ""
    i = 0

    while i < len(input_str):
        # Check if the current character is a singular character
        word = {"a", "i"}
        if (
            input_str[i].isalpha()
            and len(input_str[i]) == 1
            and input_str[i] not in word
        ):
            i += 1
        else:
            # Append the character to the result string
            result_str += input_str[i]
            i += 1

    return result_str


# def remove_singular_characters(input_str):
#     # Download the nltk punkt tokenizer if you haven't already

#     words_to_remove = [
#         "b",
#         "c",
#         "d",
#         "e",
#         "f",
#         "g",
#         "h",
#         "j",
#         "k",
#         "l",
#         "m",
#         "n",
#         "o",
#         "p",
#         "q",
#         "r",
#         "s",
#         "t",
#         "u",
#         "v",
#         "w",
#         "x",
#         "y",
#         "z",
#     ]

#     # Tokenize the paragraph into words
#     words = word_tokenize(input_str)

#     # Filter out the specified words
#     filtered_words = [word for word in words if word.lower() not in words_to_remove]

#     # Join the filtered words back into a paragraph
#     filtered_paragraph = " ".join(filtered_words)

#     return filtered_paragraph


def remove_newlines_tabs(text):
    """
    This function will remove all the occurrences of newlines, tabs, and combinations like: \\n, \\.

    arguments:
        input_text: "text" of type "String".

    return:
        value: "text" after removal of newlines, tabs, \\n, \\ characters.

    Example:
    Input : This is her \\ first day at this place.\n Please,\t Be nice to her.\\n
    Output : This is her first day at this place. Please, Be nice to her.

    """

    # Replacing all the occurrences of \n,\\n,\t,\\ with a space.
    Formatted_text = (
        text.replace("\\n", " ")
        .replace("\n", " ")
        .replace("\t", " ")
        .replace("\\", " ")
        .replace(". com", ".com")
    )
    return Formatted_text


def strip_html_tags(text):
    """
    This function will remove all the occurrences of html tags from the text.

    arguments:
        input_text: "text" of type "String".

    return:
        value: "text" after removal of html tags.

    Example:
    Input : This is a nice place to live. <IMG>
    Output : This is a nice place to live.
    """
    # Initiating BeautifulSoup object soup.
    soup = BeautifulSoup(text, "html.parser")
    # Get all the text other than html tags.
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def remove_links(text):
    """
    This function will remove all the occurrences of links.

    arguments:
        input_text: "text" of type "String".

    return:
        value: "text" after removal of all types of links.

    Example:
    Input : To know more about this website: kajalyadav.com  visit: https://kajalyadav.com//Blogs
    Output : To know more about this website: visit:

    """

    # Removing all the occurrences of links that starts with https
    remove_https = re.sub(r"http\S+", "", text)
    # Remove all the occurrences of text that ends with .com
    remove_com = re.sub(r"\ [A-Za-z]*\.com", " ", remove_https)
    return remove_com


def remove_whitespace(text):
    """This function will remove
        extra whitespaces from the text
    arguments:
        input_text: "text" of type "String".

    return:
        value: "text" after extra whitespaces removed .

    Example:
    Input : How   are   you   doing   ?
    Output : How are you doing ?

    """
    pattern = re.compile(r"\s+")
    Without_whitespace = re.sub(pattern, " ", text)
    # There are some instances where there is no space after '?' & ')',
    # So I am replacing these with one space so that It will not consider two words as one token.
    text = Without_whitespace.replace("?", " ? ").replace(")", ") ")
    return text


# Code for accented characters removal
def accented_characters_removal(text):
    # this is a docstring
    """
    The function will remove accented characters from the
    text contained within the Dataset.

    arguments:
        input_text: "text" of type "String".

    return:
        value: "text" with removed accented characters.

    Example:
    Input : Málaga, àéêöhello
    Output : Malaga, aeeohello

    """
    # Remove accented characters from text using unidecode.
    # Unidecode() - It takes unicode data & tries to represent it to ASCII characters.
    text = unidecode.unidecode(text)
    return text


def reducing_incorrect_character_repeatation(text):
    """
    This Function will reduce repeatition to two characters
    for alphabets and to one character for punctuations.

    arguments:
         input_text: "text" of type "String".

    return:
        value: Finally formatted text with alphabets repeating to
        two characters & punctuations limited to one repeatition

    Example:
    Input : Realllllllllyyyyy,        Greeeeaaaatttt   !!!!?....;;;;:)
    Output : Reallyy, Greeaatt !?.;:)

    """
    # Pattern matching for all case alphabets
    Pattern_alpha = re.compile(r"([A-Za-z])\1{1,}", re.DOTALL)

    # Limiting all the  repeatation to two characters.
    Formatted_text = Pattern_alpha.sub(r"\1\1", text)

    # Pattern matching for all the punctuations that can occur
    Pattern_Punct = re.compile(r"([.,/#!$%^&*?;:{}=_`~()+-])\1{1,}")

    # Limiting punctuations in previously formatted string to only one.
    Combined_Formatted = Pattern_Punct.sub(r"\1", Formatted_text)

    # The below statement is replacing repeatation of spaces that occur more than two times with that of one occurrence.
    Final_Formatted = re.sub(" {2,}", " ", Combined_Formatted)
    return Final_Formatted


def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    """expand shortened words to the actual form.
    e.g. don't to do not

    arguments:
         input_text: "text" of type "String".

    return:
         value: Text with expanded form of shorthened words.

    Example:
    Input : ain't, aren't, can't, cause, can't've
    Output :  is not, are not, cannot, because, cannot have

    """
    # Tokenizing text into tokens.
    list_Of_tokens = text.split(" ")

    # Checking for whether the given token matches with the Key & replacing word with key's value.

    # Check whether Word is in lidt_Of_tokens or not.
    for Word in list_Of_tokens:
        # Check whether found word is in dictionary "Contraction Map" or not as a key.
        if Word in CONTRACTION_MAP:
            # If Word is present in both dictionary & list_Of_tokens, replace that word with the key value.
            list_Of_tokens = [
                item.replace(Word, CONTRACTION_MAP[Word]) for item in list_Of_tokens
            ]

    # Converting list of tokens to String.
    String_Of_tokens = " ".join(str(e) for e in list_Of_tokens)
    return String_Of_tokens


# def remove_words_not_in_english(text):
#     dictionary = set(nltk.corpus.words.words())

#     # Get the words in the sentence
#     words = nltk.word_tokenize(text)

#     # Remove words not in the dictionary
#     words = [word for word in words if word in dictionary]

#     # Rejoin the words into a sentence
#     text = " ".join(words)

#     return text
