import json
from tqdm import tqdm
import pandas as pd
from transformers import pipeline

def detect_topic(text, candidate_topics, classifier):
    result = classifier(text, candidate_topics)
    return result['labels'], result['scores']


def detect_topics_in_all(
        candidate_topics,
        classifier,
        file_schema_path='data/processed/file_schema.json', 
        outpath='data/processed/topics.csv'
        ):
    
    # load the file schema to extract the debates' paths and metadata
    with open(file_schema_path, 'r') as f:
        file_schema = json.load(f)

    print(f'Detecting the following {len(candidate_topics)} topics: {candidate_topics}')

    counter = 0
    df = pd.DataFrame()
    for base_name in tqdm(file_schema.keys(), desc='Detect debates topics'):
        
        # Summarize the debate
        with open(file_schema[base_name]['conc_debate_path'], 'r') as f:
            text = f.read()

        labels, scores = detect_topic(text, candidate_topics=candidate_topics, classifier=classifier)

        # Collect scores:
        df_tmp_scores = pd.DataFrame([scores], columns=labels)
     
        # Collect metadata
        df_tmp = pd.DataFrame.from_dict({
            "ID": [file_schema[base_name]['text_id']],
            "date": [f"{file_schema[base_name]['year']}-{file_schema[base_name]['month']}-{file_schema[base_name]['day']}"],
            "chamber": [file_schema[base_name]['chamber']],
            "debate_num": [file_schema[base_name]['debate_num']],  
        })

        # Merge metadata and scores
        df_tmp = pd.concat([df_tmp, df_tmp_scores], axis=1)

        # Merge with the main dataframe
        df = pd.concat([df, df_tmp])
        counter += 1
    
    if counter != len(file_schema):
        print(f'Error: Processed {counter} debates, but there are {len(file_schema)} debates in the schema.')
    else:
        print(f'Processed {counter} debates.')

    # Export the results
    df.to_csv(outpath, index=False)


def main():
    classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")
    candidate_topics = ["security", "geopolitics", "technologies", "energy", "crime", "climate", "defence"]     
    
    detect_topics_in_all(
        candidate_topics=candidate_topics,
        classifier=classifier
    )


if __name__ == '__main__':
    main()