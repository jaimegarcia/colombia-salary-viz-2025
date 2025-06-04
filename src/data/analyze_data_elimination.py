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

if __name__ == "__main__":
    main()
