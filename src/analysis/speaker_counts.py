import pandas as pd
import json

def get_speaker_count(file_schema_path, outdir):

    with open(file_schema_path, 'r') as f:
            file_schema = json.load(f)

    df = pd.DataFrame()
    for base_name in file_schema.keys():

        # get metadata
        data = pd.read_table(file_schema[base_name]["src_path_tsv"], sep = "\t", index_col=False)

        grouping_cols = [col for col in data.columns if "Speaker" in col] + ["Party_status", "Party_orientation"]
        speaker_count = data.groupby(grouping_cols, as_index=False).size()
        df_out = speaker_count
        # add metadata
        df_out["Debate_ID"] = base_name
        df_out["Date"] = f'{file_schema[base_name]["year"]}-{file_schema[base_name]["month"]}-{file_schema[base_name]["day"]}'
        df_out["House"] = file_schema[base_name]["chamber"]
        df_out["Debate_Num"] = file_schema[base_name]["debate_num"]
        df_out = df_out[["Date", "Debate_Num", "House", "Debate_ID"] + grouping_cols + ["size"]]
        df_out = df_out.drop(columns=["Speaker_birth", "Speaker_gender"])

        # append to main dataframe
        df = pd.concat([df, df_out])
        
    df.to_csv(f'{outdir}/speaker_count.csv', index=False)
    print("Speaker count data saved to ./data/processed/speaker_count.csv")

def main():
    get_speaker_count('./data/processed/file_schema.json', './data/processed')

if __name__ == "__main__":
    main()