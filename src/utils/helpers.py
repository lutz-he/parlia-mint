import os
import tarfile
from glob import glob
import re
import json
import json
import pandas as pd
from tqdm import tqdm

def create_subset(
    tar_path="data/raw/ParlaMint-NL-en.ana.tgz", 
    output_dir="data/raw/subset", 
    folder_to_extract="ParlaMint-NL-en.txt", 
    years=[2021, 2022]):

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the tar file
    with tarfile.open(tar_path, "r:gz") as tar:
        # Loop over the specified years first
        for year in years:
            year_folder = os.path.join(output_dir, f"{folder_to_extract}/{year}")
            if not os.path.exists(year_folder):
                # Extract folders that match the specified year
                for member in tar.getmembers():
                    if f"{folder_to_extract}/{year}/" in member.name:
                        tar.extract(member, output_dir)
            else:
                print(f"Skipping extraction for {year} as it already exists in {output_dir}")

    print(f"Files from '{folder_to_extract}' for years {years} created in {output_dir}")


def get_file_schema(path='data/raw/subset/ParlaMint-NL-en.txt/2022', outpath='data/processed/file_schema.json'):

    files = glob(f'{path}*.txt') + glob(f'{path}*.tsv')
    text_ids = [os.path.basename(file).split('.')[0].replace('-meta', '') for file in files]

    schema = {}
    for text_id in text_ids:
        base_name = text_id.split('_')[-1]
        year, month, day, debate_num = re.findall(r'\d+', base_name)
        chamber = re.findall(r'[a-zA-Z]+', base_name)[0]
        src_path_txt = [f for f in files if f.endswith('.txt') and base_name in f][0]
        src_path_tsv = [f for f in files if f.endswith('.tsv') and base_name in f][0]

        schema[base_name] = {
            'year': year,
            'month': month,
            'day': day,
            'chamber': chamber,
            'debate_num': debate_num,
            'text_id': text_id,
            'src_path_txt': src_path_txt,
            'src_path_tsv': src_path_tsv
        }
    
    with open(outpath, 'w') as f:
        json.dump(schema, f, indent=4)


def preprocess_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Fix unclosed quotation marks
    fixed_lines = []
    for line in lines:
        if line.count('"') % 2 != 0:
            line = line.replace('"', '')  # Remove unclosed quotation marks
        fixed_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)


def collect_debate(base_name, file_schema, outdir='data/processed/debates/'):
    txt_path = file_schema[base_name]['src_path_txt']
    tsv_path = file_schema[base_name]['src_path_tsv']

    # Preprocess the text file to fix unclosed quotation marks
    preprocess_text_file(txt_path)

    try:
        with open(txt_path, 'r') as f:
            txt = pd.read_table(f, header=None, names=['Text_ID', 'text'], sep='\t')
    except pd.errors.ParserError as e:
        print(f"Error parsing file {txt_path}: {e}")
        return

    with open(tsv_path, 'r') as f:
        tsv = pd.read_table(f, sep='\t', index_col=False)
    
    tsv_subset = tsv[['ID', 'Speaker_name', 'Speaker_party']]
    df_text = txt.merge(tsv_subset, left_on='Text_ID', right_on='ID', how='left').drop(columns='ID')

    def conc_row(row, df = df_text):
        """
        Concatenates the text of a row with the speaker's name and party if it is the first row for that speaker,
        otherwise returns only the text.

        Args:
            row (pd.Series): A pandas Series representing a row of a DataFrame. The Series must contain the following columns:
                - 'name': The index of the row.
                - 'Speaker_name': The name of the speaker.
                - 'Speaker_party': The party of the speaker.
                - 'text': The text spoken by the speaker.

        Returns:
            str: A string containing the speaker's name, party, and text if it is the first row for that speaker,
                 otherwise just the text.
        """
        if row.name > 0 and df.at[row.name - 1, 'Speaker_name'] == row['Speaker_name'] and df.at[row.name - 1, 'Speaker_party'] == row['Speaker_party']:
            return f"{row['text']}"
        else:
            return f"{row['Speaker_name']} ({row['Speaker_party']}): {row['text']}"

    # Join all text rows into a single document
    doc = '\n'.join(df_text.apply(conc_row, axis=1))

    # Write the document to a file from which it can be read later
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print(f"Created directory: {outdir}")

    outpath = f'{outdir}{base_name}.txt'
    with open(outpath, 'w') as f:
        f.write(doc)
    
    # add outpath to file_schema
    file_schema[base_name]['conc_debate_path'] = outpath
    with open('data/processed/file_schema.json', 'w') as f:
        json.dump(file_schema, f, indent=4)



def collect_all_debates(file_schema, outdir='data/processed/debates/'):
    for base_name in tqdm(file_schema.keys(), desc='Collecting debates', colour='green'):
        collect_debate(base_name, file_schema, outdir=outdir)

