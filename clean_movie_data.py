import pandas as pd
import numpy as np
from datetime import datetime

def enhanced_cleaner(input_file, output_file):
    # 1. Load data with memory efficiency
    df = pd.read_csv(input_file, encoding='utf-8', low_memory=False)
    
    original_count = len(df)
    
    # 2. Remove duplicates
    df = df.drop_duplicates(subset=['Movie ID'], keep='first')
    
    # 3. Add Profit column
    df['Profit'] = df['Revenue'] - df['Budget']
    
    # 4. Standardize genre spellings
    genre_standardization = {
        'Sci-Fi': 'Science Fiction',
        'SciFi': 'Science Fiction',
        'Sci Fi': 'Science Fiction',
        'RomCom': 'Romantic Comedy',
        'Fantasty': 'Fantasy'
    }
    df['Genres'] = df['Genres'].replace(genre_standardization, regex=True)
    
    # 5. Rating normalization (10-point to 5-star)
    df['Rating_5star'] = (df['Rating'] / 2).round(1)
    
    # 6. Text field standardization
    text_cols = ['Title', 'Overview', 'Director', 'Writers', 'Cast']
    for col in text_cols:
        df[col] = (df[col].astype(str)
                   .str.replace(r'\s+', ' ', regex=True)  # Remove extra spaces
                   .str.strip()
                   .replace('nan', np.nan))
    
    # 7. Generate cleaning report
    cleaning_report = f"""
    ==== MOVIE DATA CLEANING REPORT ====
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Input file: {input_file}
    
    Records Processed:
    - Initial count: {original_count:,}
    - After deduplication: {len(df):,}
    - Duplicates removed: {original_count - len(df):,}
    
    Financial Stats:
    - Highest Profit: ${df['Profit'].max():,.2f}
    - Average Profit: ${df['Profit'].mean():,.2f}
    - Median Profit: ${df['Profit'].median():,.2f}
    
    Rating Distribution:
    - Average (10-point): {df['Rating'].mean():.1f}
    - Average (5-star): {df['Rating_5star'].mean():.1f}
    - Best Rated: {df['Rating'].max()}/10 ({df.loc[df['Rating'].idxmax(), 'Title']})
    
    Genre Standardization Applied:
    {pd.Series(genre_standardization).to_string()}
    """
    
    # 8. Save outputs
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    with open('movie_cleaning_report.txt', 'w') as f:
        f.write(cleaning_report)
    
    print(cleaning_report)
    print(f"\nCleaned data saved to: {output_file}")

# Execute the cleaner
enhanced_cleaner('cleaned_movies_with_main_genre.csv', 'profit_enhanced_movies.csv')