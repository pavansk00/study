import nltk

# Sentence for NER
sentence = "The Eiffel Tower was built from 1887 to 1889 by Gustave Eiffel, whose company specialized in building metal frameworks and structures."

# Tokenize the sentence
words = nltk.word_tokenize(sentence)

# Tag the words with parts of speech
tag_elements = nltk.pos_tag(words)

# Download the required NLTK models if not already downloaded
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Perform Named Entity Recognition
ner_tree = nltk.ne_chunk(tag_elements)

# Draw the NER tree
ner_tree.draw()
