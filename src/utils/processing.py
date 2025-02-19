from helpers import get_file_schema, collect_all_debates
import json

def main():
    path = 'data/raw/subset/ParlaMint-NL-en.txt/2022/'
    get_file_schema(path)
    print('File schema created.')
    
    with open('data/processed/file_schema.json', 'r') as f:
        file_schema = json.load(f)
    print(f'File schema loaded: {len(file_schema)} debates.')

    collect_all_debates(file_schema)


if __name__ == '__main__':
    main()

