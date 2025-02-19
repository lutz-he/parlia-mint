import re
import json
from tqdm import tqdm
import pandas as pd
from gensim import corpora
from gensim.models import LdaModel
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text.lower())
    # Remove punctuation and stopwords
    tokens = [word for word in tokens if word not in string.punctuation and word not in stopwords.words('english')]
    return tokens

def load_debates(file_schema_path='data/processed/file_schema.json'):
    with open(file_schema_path, 'r') as f:
        file_schema = json.load(f)

    texts = []
    for base_name in file_schema.keys():
        with open(file_schema[base_name]['conc_debate_path'], 'r') as f:
            texts.append(f.read())
    
    return texts

def apply_lda(texts, num_topics=5):
    # Preprocess texts with progress bar
    processed_texts = [preprocess_text(text) for text in tqdm(texts, desc="Preprocessing texts")]

    # Create a dictionary and corpus for LDA with progress bar
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in tqdm(processed_texts, desc="Creating corpus")]

    # Apply LDA 
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    doc_topics = [lda_model.get_document_topics(bow) for bow in corpus]
    return lda_model, doc_topics

def print_lda_topics(lda_model, num_words=5):
    for idx, topic in lda_model.print_topics(num_words=num_words):
        print(f"Topic {idx}: {topic}")

def print_doc_topics(doc_topics):
    for doc_idx, topics in enumerate(doc_topics):
        print(f"Document {doc_idx}:")
        for topic, prob in topics:
            print(f"  Topic {topic}: {prob:.4f}")

def save_doc_topics_to_csv(doc_topics, output_path='data/processed/debate_topics.csv'):
    data = []
    for doc_idx, topics in enumerate(doc_topics):
        for topic, prob in topics:
            data.append({'Document': doc_idx, 'Topic': topic, 'Probability': prob})
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)

def relate_docidx_to_base_name(file_schema_path='data/processed/file_schema.json', debate_topics_path='data/processed/debate_topics.csv'):
    with open(file_schema_path, 'r') as f:
        file_schema = json.load(f)
    
    def get_date_from_base_name(base_name):
        year, month, day, debate_num = re.findall(r'\d+', base_name)
        return f"{year}-{month}-{day}"

    df = pd.read_csv(debate_topics_path)
    df['Debate_ID'] = df['Document'].apply(lambda x: list(file_schema.keys())[x])
    df['Date'] = df["Debate_ID"].apply(lambda x: get_date_from_base_name(x))
    df["Debate_Num"] = df["Debate_ID"].apply(lambda x: file_schema[x]["debate_num"])
    df["House"] = df["Debate_ID"].apply(lambda x: file_schema[x]["chamber"])
    df = df[["Date", "Debate_Num", "House", "Debate_ID", "Topic", "Probability"]]
    df.to_csv(debate_topics_path, index=False)

def main():
    file_schema_path = 'data/processed/file_schema.json'
    texts = load_debates(file_schema_path)
    lda_model, doc_topics = apply_lda(texts, num_topics=5)
    print_lda_topics(lda_model)
    print_doc_topics(doc_topics)
    save_doc_topics_to_csv(doc_topics)
    relate_docidx_to_base_name()



if __name__ == '__main__':
    main()