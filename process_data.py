import pandas as pd
import numpy as np

# Read the original CSV file
df = pd.read_csv('src/data/salaries-2025.csv')

print(f"Loaded {len(df)} rows from salaries-2025.csv")

# Column mappings (using column indices since names are very long)
cols = list(df.columns)

# Create mappings for education levels
education_mapping = {
    'Bachiller': 1,
    'Técnica': 2,
    'Tecnóloga/o': 3,
    'Pregrado': 4,
    'Posgrado': 5
}

# Create mappings for English levels - simplified
def map_english_level(text):
    if pd.isna(text) or text == 'Cero':
        return 0
    elif 'A1' in str(text) or 'A2' in str(text):
        return 1
    elif 'B1' in str(text):
        return 2
    elif 'B2' in str(text):
        return 3
    elif 'C1' in str(text) or 'C2' in str(text):
        return 4
    else:
        return 1

# Create new dataframe with simplified columns
processed_df = pd.DataFrame()

# Map the columns using indices
processed_df['experience'] = pd.to_numeric(df.iloc[:, 1], errors='coerce')  # Años de experiencia
processed_df['max-title-text'] = df.iloc[:, 2]  # Nivel de formación
processed_df['main-programming-language'] = df.iloc[:, 7]  # Lenguaje principal
processed_df['workmode'] = df.iloc[:, 8]  # Modo de trabajo
processed_df['company-type'] = df.iloc[:, 10]  # Tipo de empresa
processed_df['english-level-text'] = df.iloc[:, 6]  # Nivel de inglés

# Handle salary data
processed_df['currency-usd'] = df.iloc[:, 13] # Currency USD
processed_df['total-salary-usd'] = pd.to_numeric(df.iloc[:, 15], errors='coerce')  # Total salary USD
processed_df['currency-cop'] = df.iloc[:, 16]  # Currency COP  
processed_df['total-salary-cop'] = pd.to_numeric(df.iloc[:, 18], errors='coerce')  # Total salary COP

# Map education levels to numbers
processed_df['max-title'] = processed_df['max-title-text'].map(education_mapping).fillna(1)

# Map English levels to numbers
processed_df['english-level'] = processed_df['english-level-text'].apply(map_english_level)

# Determine currency and salary - prioritize total compensation
processed_df['currency'] = 'Pesos'
processed_df['income-in-currency'] = 0

for idx, row in processed_df.iterrows():
    # Use USD if available and currency is USD
    if (pd.notna(row['total-salary-usd']) and 
        row['total-salary-usd'] > 0 and 
        str(row['currency-usd']).startswith('Dólares')):
        processed_df.at[idx, 'currency'] = 'Dólares'
        processed_df.at[idx, 'income-in-currency'] = row['total-salary-usd']
    # Otherwise use COP if available
    elif (pd.notna(row['total-salary-cop']) and 
          row['total-salary-cop'] > 0 and 
          str(row['currency-cop']).startswith('Pesos')):
        processed_df.at[idx, 'currency'] = 'Pesos'
        processed_df.at[idx, 'income-in-currency'] = row['total-salary-cop']

# Create experience ranges (simple mapping for now)
processed_df['min-experience'] = processed_df['experience'].fillna(0).astype(int)
processed_df['max-experience'] = processed_df['experience'].fillna(0).astype(int)

# Clean up company type names
processed_df['company-type'] = processed_df['company-type'].str.replace('empresa', '', case=False).str.strip()

# Select final columns matching the original structure
final_df = processed_df[[
    'currency',
    'main-programming-language',
    'company-type',
    'workmode',
    'min-experience',
    'max-experience',
    'english-level',
    'max-title',
    'income-in-currency'
]].copy()

# Remove rows with invalid data
final_df = final_df[
    (final_df['income-in-currency'] > 0) &
    (pd.notna(final_df['main-programming-language'])) &
    (final_df['main-programming-language'] != '') &
    (pd.notna(final_df['company-type'])) &
    (final_df['company-type'] != '') &
    (final_df['min-experience'] >= 0)
]

# Convert to appropriate data types
final_df['min-experience'] = final_df['min-experience'].astype(int)
final_df['max-experience'] = final_df['max-experience'].astype(int)
final_df['english-level'] = final_df['english-level'].astype(int)
final_df['max-title'] = final_df['max-title'].astype(int)
final_df['income-in-currency'] = final_df['income-in-currency'].astype(float)

# Save the processed file
final_df.to_csv('src/data/salaries-2025-processed.csv', index=False)

print(f"Processed {len(final_df)} valid records")
print("\nSample of processed data:")
print(final_df.head())
print("\nUnique programming languages:")
print(final_df['main-programming-language'].value_counts().head(10))
print("\nCurrency distribution:")
print(final_df['currency'].value_counts())
