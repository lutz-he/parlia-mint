from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
from tqdm import tqdm
import pandas as pd

model_name = 't5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def summarize(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize_all_debates(file_schema_path='data/processed/file_schema.json', outpath='data/processed/summaries.csv'):
    # load the file schema to extract the debates' paths and metadata
    with open(file_schema_path, 'r') as f:
        file_schema = json.load(f)

    counter = 0
    df = pd.DataFrame()
    for base_name in tqdm(file_schema.keys(), desc='Summarizing debates'):
        
        # Summarize the debate
        with open(file_schema[base_name]['conc_debate_path'], 'r') as f:
            text = f.read()

        summary = summarize(text)
     
        # Collect metadata and store the summary
        df_tmp = pd.DataFrame.from_dict({
            "ID": [file_schema[base_name]['text_id']],
            "date": [f"{file_schema[base_name]['year']}-{file_schema[base_name]['month']}-{file_schema[base_name]['day']}"],
            "chamber": [file_schema[base_name]['chamber']],
            "debate_num": [file_schema[base_name]['debate_num']],
            "summary": [summary]
        })

        df = pd.concat([df, df_tmp])
        counter += 1
    

    if counter != len(file_schema):
        print(f'Error: Summarized {counter} debates, but there are {len(file_schema)} debates in the schema.')
    else:
        print(f'Summarized {counter} debates.')
    df.to_csv(outpath, index=False)
        

def main():    
    summarize_all_debates()


if __name__ == '__main__':
    main()