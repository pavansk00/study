
##  Tokenization
## Sentence-->paragraphs
import nltk
from nltk.tokenize import sent_tokenize
#nltk.download('punkt')

corpus="""Hello Welcome,to Krish Naik's NLP Tutorials.
Please do watch the entire course! to become expert in NLP.
"""

documents=sent_tokenize(corpus)
print("sent_tokeniz \n")
for sentence in documents:
    print(sentence)
print("\n")
## Tokenization 
## Paragraph-->words
## sentence--->words
from nltk.tokenize import word_tokenize

doc1 = word_tokenize(corpus)
print("word_tokenize \n")
print(doc1)
print("\n")

from nltk.tokenize import wordpunct_tokenize

doc2 = wordpunct_tokenize(corpus)
print("wordpunct_tokenize \n")
print(doc2)
print("\n")

from nltk.tokenize import TreebankWordTokenizer
tokenizer=TreebankWordTokenizer()

doc3 = tokenizer.tokenize(corpus)
print("TreebankWordTokenizer \n")
print(doc3)
print("\n")