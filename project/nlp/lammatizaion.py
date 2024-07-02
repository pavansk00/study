"""Wordnet Lemmatizer
Lemmatization technique is like stemming. The output we will get after lemmatization is called ‘lemma’, which is a root word rather than root stem, the output of stemming. After lemmatization, we will be getting a valid word that means the same thing.

NLTK provides WordNetLemmatizer class which is a thin wrapper around the wordnet corpus. This class uses morphy() function to the WordNetCorpusReader class to find a lemma. Let us understand it with an example:

Q&A, chatbots, text summarization"""


import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

'''
POS- Noun-n
verb-v
adjective-a
adverb-r
'''
print(lemmatizer.lemmatize("going", pos='v'))  # 'go'

words = ["eating", "eats", "eaten", "writing", "writes", "programming", "programs", "history", "finally", "finalized"]

for word in words:
    print(word + "---->" + lemmatizer.lemmatize(word, pos='v'))

# Output:
# eating---->eat
# eats---->eat
# eaten---->eat
# writing---->write
# writes---->write
# programming---->program
# programs---->program
# history---->history
# finally---->finally
# finalized---->finalize

print(lemmatizer.lemmatize("goes", pos='v'))  # 'go'

print(lemmatizer.lemmatize("fairly", pos='v'), lemmatizer.lemmatize("sportingly"))  # ('fairly', 'sportingly')
