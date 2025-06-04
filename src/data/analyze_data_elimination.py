#!/usr/bin/env python3
"""
Data Elimination Analysis for Colombia Salary Survey 2025
=========================================================

This script analyzes what data was eliminated during processing and why.
It compares the original survey responses with the processed dataset.

Usage: python3 analyze_data_elimination.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

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

def analyze_cop_salary_thresholds(processed_df):
    """Analyze COP salary distribution to understand thresholds."""
    print("=" * 60)
    print("COP SALARY ANALYSIS")
    print("=" * 60)
    
    cop_salaries = processed_df[processed_df['currency'] == 'Pesos']['income-in-currency']
    
    # Current exchange rate (approximate)
    usd_rate = 4300
    
    print(f"Total COP salary records: {len(cop_salaries):,}")
    print(f"\nCOP Salary Statistics:")
    print(f"  Mean: {cop_salaries.mean()/1e6:.1f}M COP (${cop_salaries.mean()/usd_rate:,.0f} USD)")
    print(f"  Median: {cop_salaries.median()/1e6:.1f}M COP (${cop_salaries.median()/usd_rate:,.0f} USD)")
    print(f"  Std Dev: {cop_salaries.std()/1e6:.1f}M COP")
    print(f"  Min: {cop_salaries.min()/1e6:.1f}M COP (${cop_salaries.min()/usd_rate:,.0f} USD)")
    print(f"  Max: {cop_salaries.max()/1e6:.1f}M COP (${cop_salaries.max()/usd_rate:,.0f} USD)")
    
    print(f"\nPercentile Analysis:")
    percentiles = [25, 50, 75, 90, 95, 99]
    for p in percentiles:
        val = np.percentile(cop_salaries, p)
        print(f"  {p:2d}th percentile: {val/1e6:6.1f}M COP (${val/usd_rate:8,.0f} USD)")
    
    # Define thresholds
    p99 = np.percentile(cop_salaries, 99)
    print(f"\n🔍 EXTREMELY HIGH COP SALARIES (>99th percentile = {p99/1e6:.1f}M COP):")
    extreme_salaries = cop_salaries[cop_salaries > p99]
    for salary in sorted(extreme_salaries, reverse=True):
        print(f"  {salary/1e6:6.1f}M COP (${salary/usd_rate:8,.0f} USD)")
    
    # Low salary analysis
    print(f"\n🔍 VERY LOW COP SALARIES (<1M COP = ~${1000000/usd_rate:,.0f} USD):")
    low_salaries = cop_salaries[cop_salaries < 1000000]
    for salary in sorted(low_salaries):
        print(f"  {salary/1e6:6.1f}M COP (${salary/usd_rate:8,.0f} USD)")
    
    return p99

def analyze_usd_salary_thresholds(processed_df):
    """Analyze USD salary distribution to understand thresholds."""
    print("\n" + "=" * 60)
    print("USD SALARY ANALYSIS")
    print("=" * 60)
    
    usd_salaries = processed_df[processed_df['currency'] == 'Dólares']['income-in-currency']
    
    print(f"Total USD salary records: {len(usd_salaries):,}")
    print(f"\nUSD Salary Statistics:")
    print(f"  Mean: ${usd_salaries.mean():,.0f}")
    print(f"  Median: ${usd_salaries.median():,.0f}")
    print(f"  Std Dev: ${usd_salaries.std():,.0f}")
    print(f"  Min: ${usd_salaries.min():,.0f}")
    print(f"  Max: ${usd_salaries.max():,.0f}")
    
    print(f"\nPercentile Analysis:")
    percentiles = [25, 50, 75, 90, 95, 99]
    for p in percentiles:
        val = np.percentile(usd_salaries, p)
        print(f"  {p:2d}th percentile: ${val:8,.0f}")
    
    # Define thresholds
    p99 = np.percentile(usd_salaries, 99)
    print(f"\n🔍 EXTREMELY HIGH USD SALARIES (>99th percentile = ${p99:,.0f}):")
    extreme_salaries = usd_salaries[usd_salaries > p99]
    for salary in sorted(extreme_salaries, reverse=True):
        print(f"  ${salary:8,.0f}")
    
    # Low salary analysis  
    print(f"\n🔍 VERY LOW USD SALARIES (<$2,500):")
    low_salaries = usd_salaries[usd_salaries < 2500]
    for salary in sorted(low_salaries):
        print(f"  ${salary:8,.0f}")
    
    return p99

def identify_eliminated_records(original_df):
    """Identify all records that would be eliminated and their reasons."""
    
    # Column mappings
    currency_col = '¿A usted le pagan en pesos colombianos (COP) o dólares americanos (USD) en su trabajo principal? Si le pagan en otra moneda seleccione dólares y convierta a la tasa de cambio del día que realizó la encuesta para las próximas preguntas'
    experience_col = '¿Cuántos años de experiencia en desarrollo de software tiene?'
    language_col = '¿En cuál de los siguientes lenguajes de programación ocupa la mayor parte de su tiempo laboral?'
    
    # Get salary columns by position (more reliable than complex names)
    base_salary_usd_col = 15  # Column 16 (0-indexed)
    total_salary_usd_col = 16  # Column 17 (0-indexed)
    base_salary_cop_col = 18  # Column 19 (0-indexed)
    total_salary_cop_col = 19  # Column 20 (0-indexed)
    
    eliminated_records = []
    
    for idx, row in original_df.iterrows():
        issues = []
        
        # Get basic info
        currency = row.get(currency_col)
        experience = row.get(experience_col)
        language = row.get(language_col)
        
        # Get salary data by position
        base_salary_usd = row.iloc[base_salary_usd_col] if len(row) > base_salary_usd_col else None
        total_salary_usd = row.iloc[total_salary_usd_col] if len(row) > total_salary_usd_col else None
        base_salary_cop = row.iloc[base_salary_cop_col] if len(row) > base_salary_cop_col else None
        total_salary_cop = row.iloc[total_salary_cop_col] if len(row) > total_salary_cop_col else None
        
        # Check for missing currency
        if pd.isna(currency) or currency == '':
            issues.append("Missing Currency")
        
        # Determine effective salary based on currency
        if not pd.isna(currency):
            if 'USD' in str(currency) or 'Dólares' in str(currency):
                effective_base = base_salary_usd
                effective_total = total_salary_usd
                salary_type = "USD"
            elif 'COP' in str(currency) or 'Pesos' in str(currency):
                effective_base = base_salary_cop
                effective_total = total_salary_cop
                salary_type = "COP"
            else:
                effective_base = None
                effective_total = None
                salary_type = "Unknown"
        else:
            effective_base = None
            effective_total = None
            salary_type = "Unknown"
        
        # Check for missing all salaries
        if pd.isna(effective_base) and pd.isna(effective_total):
            issues.append("Missing All Salaries")
        
        # Check experience
        if pd.isna(experience):
            issues.append("Missing Experience")
        elif experience < 0 or experience > 50:
            issues.append("Invalid Experience")
        
        # Check language
        if pd.isna(language) or language == '':
            issues.append("Missing Language")
        
        # Check for unrealistic values
        if not pd.isna(effective_total) and effective_total > 0:
            if salary_type == "USD":
                if effective_total < 2500:
                    issues.append("Unrealistic Usd Low")
                elif effective_total > 500000:
                    issues.append("Unrealistic Usd High")
            elif salary_type == "COP":
                if effective_total < 10000000:  # < 10M COP
                    issues.append("Unrealistic Cop Low")
                elif effective_total > 1000000000:  # > 1B COP
                    issues.append("Unrealistic Cop High")
        
        # Check if total < base
        if not pd.isna(effective_base) and not pd.isna(effective_total):
            if effective_total < effective_base:
                issues.append("Total Less Than Base")
        
        # If there are any issues, this record would be eliminated
        if issues:
            eliminated_records.append({
                'original_index': idx,
                'currency': currency,
                'experience_years': experience,
                'programming_language': language,
                'salary_type': salary_type,
                'base_salary_usd': base_salary_usd,
                'total_salary_usd': total_salary_usd,
                'base_salary_cop': base_salary_cop,
                'total_salary_cop': total_salary_cop,
                'effective_base_salary': effective_base,
                'effective_total_salary': effective_total,
                'issues': '; '.join(issues),
                'issue_count': len(issues)
            })
    
    return eliminated_records

def save_eliminated_records_csv(eliminated_records):
    """Save eliminated records to CSV file."""
    if not eliminated_records:
        print("No eliminated records to save.")
        return None
    
    df_eliminated = pd.DataFrame(eliminated_records)
    output_file = 'eliminated_records_2025.csv'
    df_eliminated.to_csv(output_file, index=False)
    
    print(f"\n💾 ELIMINATED RECORDS SAVED TO CSV:")
    print(f"   File: {output_file}")
    print(f"   Records: {len(eliminated_records):,}")
    print(f"   Columns: {len(df_eliminated.columns)}")
    
    # Show sample issues breakdown
    issue_counts = {}
    for record in eliminated_records:
        for issue in record['issues'].split('; '):
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    
    print(f"\n   Top Issues:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"     - {issue}: {count:,} records")
    
    return output_file

def analyze_data_quality_issues(original_df):
    """Analyze the original dataset for data quality issues."""
    print("\n" + "=" * 60)
    print("DATA QUALITY ANALYSIS")
    print("=" * 60)
    
    # Column mappings for easier reference
    currency_col = '¿A usted le pagan en pesos colombianos (COP) o dólares americanos (USD) en su trabajo principal? Si le pagan en otra moneda seleccione dólares y convierta a la tasa de cambio del día que realizó la encuesta para las próximas preguntas'
    experience_col = '¿Cuántos años de experiencia en desarrollo de software tiene?'
    language_col = '¿En cuál de los siguientes lenguajes de programación ocupa la mayor parte de su tiempo laboral?'
    
    # Salary columns (complex names from survey)
    salary_base_usd = '¿Cuál es la REMUNERACIÓN BASE ANUAL de su trabajo principal? No incluya otras compensaciones como bonos ni stock. Exprese el valor en la moneda seleccionada anteriormente. Sugerencia: use el ingreso total del año anterior sin incluir stock o bonos por desempeño.'
    salary_total_usd = '¿Cuál es la REMUNERACIÓN TOTAL de su trabajo principal? Incluya otras compensaciones como bonos y stock. Exprese el valor en la moneda seleccionada anteriormente. Sugerencia: use el ingreso total del año anterior incluyendo stock y bonos por desempeño valorados al precio de venta o al final del año.'
    salary_base_cop = salary_base_usd + '.1'
    salary_total_cop = salary_total_usd + '.1'
    
    print(f"Original dataset: {len(original_df):,} records")
    
    issues = {
        'missing_currency': 0,
        'missing_experience': 0,
        'missing_language': 0,
        'missing_all_salaries': 0,
        'unrealistic_usd_low': 0,
        'unrealistic_usd_high': 0,
        'unrealistic_cop_low': 0,
        'unrealistic_cop_high': 0,
        'total_less_than_base': 0,
        'invalid_experience': 0
    }
    
    problematic_records = []
    
    for idx, row in original_df.iterrows():
        record_issues = []
        
        # Check for missing core data
        if pd.isna(row[currency_col]):
            issues['missing_currency'] += 1
            record_issues.append("Missing currency")
            
        if pd.isna(row[experience_col]):
            issues['missing_experience'] += 1
            record_issues.append("Missing experience")
            
        if pd.isna(row[language_col]):
            issues['missing_language'] += 1
            record_issues.append("Missing language")
        
        # Check experience validity
        if not pd.isna(row[experience_col]):
            exp = row[experience_col]
            if exp < 0 or exp > 50:
                issues['invalid_experience'] += 1
                record_issues.append(f"Invalid experience: {exp}")
        
        # Analyze salary data based on currency
        currency = row[currency_col]
        if currency == 'Dólares americanos (USD)':
            base_salary = row[salary_base_usd]
            total_salary = row[salary_total_usd]
            
            # Check if both salaries are missing
            if pd.isna(base_salary) and pd.isna(total_salary):
                issues['missing_all_salaries'] += 1
                record_issues.append("Missing all USD salaries")
            else:
                # Check for unrealistic USD values
                for sal_name, salary in [('base', base_salary), ('total', total_salary)]:
                    if not pd.isna(salary):
                        if salary < 1000:  # Less than $1000 annual
                            issues['unrealistic_usd_low'] += 1
                            record_issues.append(f"Unrealistic low USD {sal_name}: ${salary}")
                        elif salary > 500000:  # More than $500k annual
                            issues['unrealistic_usd_high'] += 1
                            record_issues.append(f"Unrealistic high USD {sal_name}: ${salary}")
                
                # Check if total < base
                if not pd.isna(base_salary) and not pd.isna(total_salary) and total_salary < base_salary:
                    issues['total_less_than_base'] += 1
                    record_issues.append(f"Total (${total_salary}) < Base (${base_salary})")
                    
        elif currency == 'Pesos colombianos (COP)':
            base_salary = row[salary_base_cop]
            total_salary = row[salary_total_cop]
            
            # Check if both salaries are missing
            if pd.isna(base_salary) and pd.isna(total_salary):
                issues['missing_all_salaries'] += 1
                record_issues.append("Missing all COP salaries")
            else:
                # Check for unrealistic COP values
                for sal_name, salary in [('base', base_salary), ('total', total_salary)]:
                    if not pd.isna(salary):
                        if salary < 5000000:  # Less than 5M COP (~$1,200) annual
                            issues['unrealistic_cop_low'] += 1
                            record_issues.append(f"Unrealistic low COP {sal_name}: {salary/1e6:.1f}M")
                        elif salary > 1000000000:  # More than 1B COP (~$230k) annual
                            issues['unrealistic_cop_high'] += 1
                            record_issues.append(f"Unrealistic high COP {sal_name}: {salary/1e6:.1f}M")
                
                # Check if total < base
                if not pd.isna(base_salary) and not pd.isna(total_salary) and total_salary < base_salary:
                    issues['total_less_than_base'] += 1
                    record_issues.append(f"Total ({total_salary/1e6:.1f}M) < Base ({base_salary/1e6:.1f}M)")
        
        # Store problematic records
        if record_issues:
            problematic_records.append({
                'index': idx,
                'currency': currency,
                'experience': row[experience_col],
                'language': row[language_col],
                'issues': record_issues
            })
    
    # Print summary
    print(f"\nIssue Summary:")
    total_issues = sum(issues.values())
    for issue_type, count in issues.items():
        percentage = (count / len(original_df)) * 100
        print(f"  {issue_type.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nTotal records with issues: {len(problematic_records):,}")
    print(f"Total individual issues found: {total_issues:,}")
    
    # Show examples of problematic records
    print(f"\n🔍 EXAMPLES OF PROBLEMATIC RECORDS:")
    for i, record in enumerate(problematic_records[:10]):  # Show first 10
        print(f"\nRecord {i+1} (Index {record['index']}):")
        print(f"  Currency: {record['currency']}")
        print(f"  Experience: {record['experience']}")
        print(f"  Language: {record['language']}")
        print(f"  Issues: {'; '.join(record['issues'])}")
    
    if len(problematic_records) > 10:
        print(f"\n... and {len(problematic_records) - 10:,} more problematic records")
    
    return len(problematic_records)

def main():
    """Main analysis function."""
    print("COLOMBIA SALARY SURVEY 2025 - DATA ELIMINATION ANALYSIS")
    print("=" * 60)
    
    # Load datasets
    original_df, processed_df = load_datasets()
    if original_df is None or processed_df is None:
        return
    
    print(f"📊 Dataset Overview:")
    print(f"  Original records: {len(original_df):,}")
    print(f"  Processed records: {len(processed_df):,}")
    eliminated = len(original_df) - len(processed_df)
    print(f"  Eliminated records: {eliminated:,} ({eliminated/len(original_df)*100:.1f}%)")
    
    # Analyze salary thresholds in processed data
    cop_threshold = analyze_cop_salary_thresholds(processed_df)
    usd_threshold = analyze_usd_salary_thresholds(processed_df)
    
    # Analyze data quality issues in original data
    problematic_count = analyze_data_quality_issues(original_df)
    
    # Identify and save eliminated records to CSV
    eliminated_records = identify_eliminated_records(original_df)
    csv_file = save_eliminated_records_csv(eliminated_records)
    
    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"📈 Salary Thresholds (from processed data):")
    print(f"  Extremely high COP: >{cop_threshold/1e6:.1f}M COP (>${cop_threshold/4300:,.0f} USD)")
    print(f"  Extremely high USD: >${usd_threshold:,.0f}")
    print(f"  Very low COP: <1M COP (~$250 USD)")
    print(f"  Very low USD: <$2500")
    
    print(f"\n📊 Data Quality:")
    print(f"  Records with data quality issues: {problematic_count:,}")
    print(f"  Estimated elimination rate: {eliminated/len(original_df)*100:.1f}%")
    
    print(f"\n💡 Recommendations:")
    print(f"  - The {eliminated/len(original_df)*100:.1f}% elimination rate is reasonable for survey data")
    print(f"  - Most eliminations were due to missing/invalid salary data")
    print(f"  - Remaining {len(processed_df):,} records provide reliable salary insights")
    print(f"  - Consider data validation in future surveys to reduce elimination")
    
    if csv_file:
        print(f"\n✅ Eliminated records exported to: {csv_file}")
        print(f"   You can now analyze the {len(eliminated_records):,} eliminated records in detail.")

if __name__ == "__main__":
    main()
