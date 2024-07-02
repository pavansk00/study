"""Stemming
Stemming is the process of reducing a word to its word stem that affixes to suffixes and prefixes or to the roots of words known as a lemma. Stemming is important in natural language understanding (NLU) and natural language processing (NLP).

Classification Problem
Comments of product is a positive review or negative review
Reviews----> eating, eat, eaten [going, gone, goes]--->go"""

words = ["eating", "eats", "eaten", "writing", "writes", "programming", "programs", "history", "finally", "finalized"]

# PorterStemmer
from nltk.stem import PorterStemmer

stemming = PorterStemmer()

for word in words:
    print(word + "---->" + stemming.stem(word))

# Output:
# eating---->eat
# eats---->eat
# eaten---->eaten
# writing---->write
# writes---->write
# programming---->program
# programs---->program
# history---->histori
# finally---->final
# finalized---->final

print(stemming.stem('congratulations'))  # 'congratul'
print(stemming.stem("sitting"))  # 'sit'

# RegexpStemmer class
# NLTK has RegexpStemmer class with the help of which we can easily implement Regular Expression Stemmer algorithms.
# It basically takes a single regular expression and removes any prefix or suffix that matches the expression. Let us see an example:

from nltk.stem import RegexpStemmer

reg_stemmer = RegexpStemmer('ing$|s$|e$|able$', min=4)

print(reg_stemmer.stem('eating'))  # 'eat'
print(reg_stemmer.stem('ingeating'))  # 'ingeat'

# Snowball Stemmer
# It is a stemming algorithm which is also known as the Porter2 stemming algorithm as it is a better version of the Porter Stemmer since some issues of it were fixed in this stemmer.

from nltk.stem import SnowballStemmer

snowball_stemmer = SnowballStemmer('english')

for word in words:
    print(word + "---->" + snowball_stemmer.stem(word))

# Output:
# eating---->eat
# eats---->eat
# eaten---->eaten
# writing---->write
# writes---->write
# programming---->program
# programs---->program
# history---->histori
# finally---->final
# finalized---->final

print(stemming.stem("fairly"), stemming.stem("sportingly"))  # ('fairli', 'sportingli')
print(snowball_stemmer.stem("fairly"), snowball_stemmer.stem("sportingly"))  # ('fair', 'sport')

print(snowball_stemmer.stem('goes'))  # 'goe'
print(stemming.stem('goes'))  # 'goe'
