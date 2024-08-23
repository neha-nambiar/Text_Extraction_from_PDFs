from functions_manipulation import *
import pandas as pd
import re

df = pd.read_csv('extracted_data.csv')

columns_to_check = ['number', 'top_right_text', 'line1', 'line2', 'line3', 'line4']
df = df.dropna(subset=columns_to_check, how='all').reset_index(drop=True)

df['EPIC No'] = df['top_right_text'].str.replace(r'[^A-Z0-9]', '', regex=True)
df['Voter Full Name'] = df['line1'].apply(extract_and_format_name)
df['Relative\'s Name'], df['Relation Type'] = zip(*df['line2'].apply(extract_name_and_relation))
df['House No'] = df['line3'].apply(extract_house_number)
df['Part S.No'] = df['number'].apply(clean_number)
df['Age'] = df['line4'].apply(extract_age)
df['Gender'] = df['line4'].apply(extract_gender)

df = df.sort_values(by='Part S.No', ascending=True)

selected_columns = df[['Part S.No', 'Voter Full Name', 'Relative\'s Name',
                    'Relation Type', 'Age', 'Gender', 'House No', 'EPIC No']] 
selected_columns.to_excel('output.xlsx', index=False)
