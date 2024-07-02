import nltk
from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Dr. APJ Abdul Kalam's speech
paragraph = """I have three visions for India. In 3000 years of our history, people from all over 
               the world have come and invaded us, captured our lands, conquered our minds. 
               From Alexander onwards, the Greeks, the Turks, the Moguls, the Portuguese, the British,
               the French, the Dutch, all of them came and looted us, took over what was ours. 
               Yet we have not done this to any other nation. We have not conquered anyone. 
               We have not grabbed their land, their culture, 
               their history and tried to enforce our way of life on them. 
               Why? Because we respect the freedom of others.That is why my 
               first vision is that of freedom. I believe that India got its first vision of 
               this in 1857, when we started the War of Independence. It is this freedom that
               we must protect and nurture and build on. If we are not free, no one will respect us.
               My second vision for India’s development. For fifty years we have been a developing nation.
               It is time we see ourselves as a developed nation. We are among the top 5 nations of the world
               in terms of GDP. We have a 10 percent growth rate in most areas. Our poverty levels are falling.
               Our achievements are being globally recognised today. Yet we lack the self-confidence to
               see ourselves as a developed nation, self-reliant and self-assured. Isn’t this incorrect?
               I have a third vision. India must stand up to the world. Because I believe that unless India 
               stands up to the world, no one will respect us. Only strength respects strength. We must be 
               strong not only as a military power but also as an economic power. Both must go hand-in-hand. 
               My good fortune was to have worked with three great minds. Dr. Vikram Sarabhai of the Dept. of 
               space, Professor Satish Dhawan, who succeeded him and Dr. Brahm Prakash, father of nuclear material.
               I was lucky to have worked with all three of them closely and consider this the great opportunity of my life. 
               I see four milestones in my career"""

# Initialize stopwords
stop_words = set(stopwords.words('english'))

# Initialize stemmers and lemmatizer
porter_stemmer = PorterStemmer()
snowball_stemmer = SnowballStemmer('english')
wordnet_lemmatizer = WordNetLemmatizer()

# Tokenize sentences
sentences = nltk.sent_tokenize(paragraph)

# Process each sentence: remove stopwords, apply stemming and lemmatization
processed_sentences_porter = []
processed_sentences_snowball = []
processed_sentences_lemmatizer = []

for sentence in sentences:
    words = nltk.word_tokenize(sentence)
    words_filtered = [word for word in words if word.lower() not in stop_words]
    
    # Apply Porter Stemmer
    words_stemmed_porter = [porter_stemmer.stem(word) for word in words_filtered]
    processed_sentences_porter.append(' '.join(words_stemmed_porter))
    
    # Apply Snowball Stemmer
    words_stemmed_snowball = [snowball_stemmer.stem(word) for word in words_filtered]
    processed_sentences_snowball.append(' '.join(words_stemmed_snowball))
    
    # Apply Lemmatizer
    words_lemmatized = [wordnet_lemmatizer.lemmatize(word, pos='v') for word in words_filtered]
    processed_sentences_lemmatizer.append(' '.join(words_lemmatized))

# Print the results
print("Original Sentences:")
print(sentences)
print("\nProcessed Sentences with Porter Stemmer:")
print(processed_sentences_porter)
print("\nProcessed Sentences with Snowball Stemmer:")
print(processed_sentences_snowball)
print("\nProcessed Sentences with Lemmatizer:")
print(processed_sentences_lemmatizer)
