#!/usr/bin/env python3
"""
Show All Eliminated Records from Colombia Salary Survey 2025
============================================================

This script shows every single record that was eliminated during processing,
along with the specific reasons for elimination.

Usage: python3 show_all_eliminated.py
"""

import pandas as pd
import numpy as np

def load_datasets():
    """Load both original and processed datasets."""
    try:
        original_df = pd.read_csv('salaries-2025.csv')
        processed_df = pd.read_csv('salaries-2025-processed.csv')
        return original_df, processed_df
    except FileNotFoundError as e:
        print(f"Error: Could not find data files. Make sure you're in the data directory.")
        print(f"Missing file: {e.filename}")
        return None, None

def analyze_eliminated_records(original_df):
    """Identify and show all eliminated records with their specific issues."""
    
    # Column mappings for easier reference (exact column names from CSV)
    currency_col = '¿A usted le pagan en pesos colombianos (COP) o dólares americanos (USD) en su trabajo principal? Si le pagan en otra moneda seleccione dólares y convierta a la tasa de cambio del día que realizó la encuesta para las próximas preguntas'
    experience_col = '¿Cuántos años de experiencia en desarrollo de software tiene?'
    language_col = '¿En cuál de los siguientes lenguajes de programación ocupa la mayor parte de su tiempo laboral?'
    base_salary_usd_col = '¿Cuál es la REMUNERACIÓN BASE ANUAL de su trabajo principal? No incluya otras compensaciones como bonos ni stock. Exprese el valor en la moneda seleccionada anteriormente. Sugerencia: use el ingreso total del año anterior sin incluir stock o bonos por desempeño.'
    total_salary_usd_col = '¿Cuál es la REMUNERACIÓN TOTAL de su trabajo principal? Incluya otras compensaciones como bonos y stock. Exprese el valor en la moneda seleccionada anteriormente. Sugerencia: use el ingreso total del año anterior incluyendo stock y bonos por desempeño valorados al precio de venta o al final del año.'
    # Note: COP columns have the same names but appear later in the CSV (columns 19-20)
    
    eliminated_records = []
    
    for idx, row in original_df.iterrows():
        issues = []
        
        # Get basic info
        currency = row.get(currency_col)
        experience = row.get(experience_col)
        language = row.get(language_col)
        
        # Get salary data - USD columns are 16-17, COP data is in columns 19-20 (duplicated structure)
        base_salary_usd = row.iloc[15] if len(row) > 15 else None  # Column 16 (0-indexed = 15)
        total_salary_usd = row.iloc[16] if len(row) > 16 else None  # Column 17 (0-indexed = 16)
        base_salary_cop = row.iloc[18] if len(row) > 18 else None  # Column 19 (0-indexed = 18) 
        total_salary_cop = row.iloc[19] if len(row) > 19 else None  # Column 20 (0-indexed = 19)
        
        # Check for missing currency
        if pd.isna(currency) or currency == '':
            issues.append("Missing currency")
        
        # Determine which salary columns to use based on currency
        if not pd.isna(currency):
            if 'USD' in str(currency) or 'Dólares' in str(currency):
                base_salary = base_salary_usd
                total_salary = total_salary_usd
                salary_type = "USD"
            elif 'COP' in str(currency) or 'Pesos' in str(currency):
                base_salary = base_salary_cop
                total_salary = total_salary_cop
                salary_type = "COP"
            else:
                base_salary = None
                total_salary = None
                salary_type = "Unknown"
        else:
            base_salary = None
            total_salary = None
            salary_type = "Unknown"
        
        # Check for missing all salaries
        if pd.isna(base_salary) and pd.isna(total_salary):
            issues.append("Missing all salaries")
        
        # Check experience
        if pd.isna(experience):
            issues.append("Missing experience")
        elif experience < 0 or experience > 50:
            issues.append(f"Invalid experience: {experience}")
        
        # Check for unrealistic values if we have salary data and currency
        if not pd.isna(total_salary) and total_salary > 0:
            if salary_type == "USD":
                if total_salary < 5000:  # Annual < $5k
                    issues.append(f"Unrealistic USD low: ${total_salary:,.0f}")
                elif total_salary > 500000:  # Annual > $500k
                    issues.append(f"Unrealistic USD high: ${total_salary:,.0f}")
            elif salary_type == "COP":
                if total_salary < 10000000:  # Annual < 10M COP (~$2.3k USD)
                    issues.append(f"Unrealistic COP low: {total_salary/1e6:.1f}M COP")
                elif total_salary > 1000000000:  # Annual > 1B COP (~$233k USD)
                    issues.append(f"Unrealistic COP high: {total_salary/1e6:.1f}M COP")
        
        # Check if total is less than base
        if not pd.isna(base_salary) and not pd.isna(total_salary):
            if total_salary < base_salary:
                issues.append(f"Total ({total_salary:,.0f}) < Base ({base_salary:,.0f})")
        
        # Check for missing language
        if pd.isna(language) or language == '':
            issues.append("Missing programming language")
        
        # If there are any issues, this record would be eliminated
        if issues:
            eliminated_records.append({
                'original_index': idx,
                'currency': currency,
                'experience': experience,
                'language': language,
                'base_salary_usd': base_salary_usd,
                'total_salary_usd': total_salary_usd,
                'base_salary_cop': base_salary_cop,
                'total_salary_cop': total_salary_cop,
                'effective_base': base_salary,
                'effective_total': total_salary,
                'salary_type': salary_type,
                'issues': issues
            })
    
    return eliminated_records

def save_eliminated_to_csv(eliminated_records):
    """Save all eliminated records to a CSV file for easier analysis."""
    
    # Convert to DataFrame
    records_for_csv = []
    for record in eliminated_records:
        records_for_csv.append({
            'original_index': record['original_index'],
            'currency': record['currency'],
            'experience_years': record['experience'],
            'programming_language': record['language'],
            'salary_type': record['salary_type'],
            'base_salary_usd': record['base_salary_usd'],
            'total_salary_usd': record['total_salary_usd'],
            'base_salary_cop': record['base_salary_cop'],
            'total_salary_cop': record['total_salary_cop'],
            'effective_base_salary': record['effective_base'],
            'effective_total_salary': record['effective_total'],
            'issues': '; '.join(record['issues']),
            'issue_count': len(record['issues'])
        })
    
    df_eliminated = pd.DataFrame(records_for_csv)
    
    # Save to CSV
    output_file = 'eliminated_records_2025.csv'
    df_eliminated.to_csv(output_file, index=False)
    
    print(f"💾 SAVED TO CSV: {output_file}")
    print(f"   Total eliminated records: {len(eliminated_records)}")
    print(f"   Columns saved: {len(df_eliminated.columns)}")
    print(f"   File location: {output_file}")
    
    return output_file, df_eliminated

def show_sample_eliminated(eliminated_records, sample_size=10):
    """Display a sample of eliminated records for quick review."""
    
    print(f"\nSAMPLE OF ELIMINATED RECORDS (showing first {sample_size})")
    print("=" * 80)
    
    for i, record in enumerate(eliminated_records[:sample_size], 1):
        print(f"\n🚫 RECORD #{i} (Index: {record['original_index']})")
        print(f"   Currency: {record['currency']}")
        print(f"   Experience: {record['experience']} years")
        print(f"   Language: {record['language']}")
        print(f"   Issues: {', '.join(record['issues'])}")
    
    if len(eliminated_records) > sample_size:
        print(f"\n... and {len(eliminated_records) - sample_size} more records (see CSV for full details)")
    
    print(f"\n{'=' * 80}")

def categorize_issues(eliminated_records):
    """Categorize and count the types of issues."""
    
    issue_categories = {}
    
    for record in eliminated_records:
        for issue in record['issues']:
            # Categorize issues
            if "Missing currency" in issue:
                category = "Missing Currency"
            elif "Missing all salaries" in issue:
                category = "Missing All Salaries"
            elif "Missing experience" in issue:
                category = "Missing Experience"
            elif "Missing programming language" in issue:
                category = "Missing Language"
            elif "Invalid experience" in issue:
                category = "Invalid Experience"
            elif "Unrealistic USD low" in issue:
                category = "Unrealistic USD (Low)"
            elif "Unrealistic USD high" in issue:
                category = "Unrealistic USD (High)"
            elif "Unrealistic COP low" in issue:
                category = "Unrealistic COP (Low)"
            elif "Unrealistic COP high" in issue:
                category = "Unrealistic COP (High)"
            elif "Total" in issue and "< Base" in issue:
                category = "Total < Base Salary"
            else:
                category = "Other"
            
            issue_categories[category] = issue_categories.get(category, 0) + 1
    
    print("\n📊 ISSUE BREAKDOWN:")
    print("=" * 50)
    total_issues = sum(issue_categories.values())
    for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_issues) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    print(f"  TOTAL ISSUES: {total_issues}")

def main():
    """Main function to show all eliminated records and save to CSV."""
    print("COLOMBIA SALARY SURVEY 2025 - ALL ELIMINATED RECORDS")
    print("=" * 80)
    
    # Load datasets
    original_df, processed_df = load_datasets()
    if original_df is None or processed_df is None:
        return
    
    print(f"📊 Dataset Overview:")
    print(f"   Original records: {len(original_df):,}")
    print(f"   Processed records: {len(processed_df):,}")
    eliminated_count = len(original_df) - len(processed_df)
    print(f"   Eliminated records: {eliminated_count:,} ({eliminated_count/len(original_df)*100:.1f}%)")
    
    # Analyze eliminated records
    eliminated_records = analyze_eliminated_records(original_df)
    
    # Show breakdown of issues
    categorize_issues(eliminated_records)
    
    # Save to CSV
    output_file, df_eliminated = save_eliminated_to_csv(eliminated_records)
    
    # Show sample of eliminated records
    show_sample_eliminated(eliminated_records)
    
    print(f"\n✅ COMPLETE!")
    print(f"   All {len(eliminated_records)} eliminated records saved to: {output_file}")
    print(f"   Open the CSV file to explore the data in detail.")

if __name__ == "__main__":
    main()
