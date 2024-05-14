import os
import camelot
import json

pdf_directory = './Schedule/'

def df_to_dict(df):
    return df.to_dict(orient='records')

all_tables_dict = {}

for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        file_path = os.path.join(pdf_directory, filename)

        tables = camelot.read_pdf(file_path, flavor='stream', pages='1-end')

        tables_dict = {}

        for i, table in enumerate(tables):
            tables_dict[f"{filename}_table_{i + 1}"] = df_to_dict(table.df)

        all_tables_dict[filename] = tables_dict

# Запись всех таблиц в файл JSON
with open('tables.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_tables_dict, json_file, ensure_ascii=False, indent=4)

print("Таблицы успешно записаны в файл tables.json")
