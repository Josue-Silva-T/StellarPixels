import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def compare(textC, examU):
    text1 = preprocess(textC)
    text2 = preprocess(examU)

    vectorizer = TfidfVectorizer()
    tfidf_matriz = vectorizer.fit_transform([text1, text2])

    similarity = cosine_similarity(tfidf_matriz[0], tfidf_matriz[1])
    
    return similarity[0][0] 