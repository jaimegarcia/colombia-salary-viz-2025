#!/usr/bin/env python3
"""
Data Processing Script for Colombia Salary Survey 2025
======================================================

This script processes the raw 2025 survey data and creates the processed CSV file
that matches the format expected by the React application.

The processing includes:
- Mapping Spanish survey headers to English simplified headers
- Converting education levels to numeric scale (1-5)
- Converting English levels to numeric scale (0-4)
- Using "remuneración total" as the primary salary field
- Filtering out invalid/incomplete records

Usage: python3 process_2025_data.py
"""
#TODO Review english level mapping and experience age ranges
import pandas as pd
import numpy as np

def load_and_process_data():
    """Load and process the 2025 salary survey data."""
    
    # Load the original data
    print("Loading original 2025 data...")
    df = pd.read_csv('salaries-2025.csv')
    print(f"Original records: {len(df)}")
    
    # Column mappings from Spanish to our processing needs
    currency_col_1 = '¿A usted le pagan en pesos colombianos (COP) o dólares americanos (USD) en su trabajo principal? Si le pagan en otra moneda seleccione dólares y convierta a la tasa de cambio del día que realizó la encuesta para las próximas preguntas'
    currency_col_2 = '¿A usted le pagan en pesos colombianos (COP) o dólares americanos (USD) en su trabajo principal? Si le pagan en otra moneda seleccione dólares y convierta a la tasa de cambio del día que realizó la encuesta para las próximas preguntas.1'
    experience_col = '¿Cuántos años de experiencia en desarrollo de software tiene?'
    language_col = '¿En cuál de los siguientes lenguajes de programación ocupa la mayor parte de su tiempo laboral?'
    education_col = '¿Cuál es su nivel de formación académica?'
    english_col = '¿Cuál es su nivel de inglés? Marco de referencia Europeo'
    company_col = '¿Para qué tipo de empresa trabaja?'
    workmode_col = 'Su modo de trabajo es'
    contract_col = '¿Cuál es el tipo de contrato que tiene con la empresa dónde ejerce su trabajo principal?'
    
    # Salary columns - using position is more reliable
    # First set of salary questions (columns 14-15)
    base_salary_1_col = 14   # Base salary first set
    total_salary_1_col = 15  # Total salary first set ("remuneración total")
    # Second set of salary questions (columns 17-18) 
    base_salary_2_col = 17   # Base salary second set
    total_salary_2_col = 18  # Total salary second set ("remuneración total")
    
    processed_records = []
    elimination_reasons = []
    
    for idx, row in df.iterrows():
        # Get basic information
        currency_1 = row.get(currency_col_1)
        currency_2 = row.get(currency_col_2)
        experience = row.get(experience_col)
        language = row.get(language_col)
        education = row.get(education_col)
        english_level = row.get(english_col)
        company_type = row.get(company_col)
        workmode = row.get(workmode_col)
        contract_type = row.get(contract_col)
        
        # Get salary data by position - check both sets
        total_salary_1 = row.iloc[total_salary_1_col] if len(row) > total_salary_1_col else None
        total_salary_2 = row.iloc[total_salary_2_col] if len(row) > total_salary_2_col else None
        
        # Convert salary values to numeric, handling strings and empty values
        def safe_numeric(value):
            if pd.isna(value) or value == '':
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        total_salary_1 = safe_numeric(total_salary_1)
        total_salary_2 = safe_numeric(total_salary_2)
        
        # Determine which set of data to use (prefer the one that has currency data)
        if not pd.isna(currency_1) and currency_1 != '':
            currency = currency_1
            salary = total_salary_1
        elif not pd.isna(currency_2) and currency_2 != '':
            currency = currency_2
            salary = total_salary_2
        else:
            currency = None
            salary = None
        
        # Track elimination reasons
        issues = []
        
        # Check for missing essential data
        if pd.isna(currency) or currency == '':
            issues.append("Missing currency")
        
        if pd.isna(experience):
            issues.append("Missing experience")
        
        if pd.isna(language) or language == '':
            issues.append("Missing language")
        
        # Determine currency type and salary value
        if not pd.isna(currency):
            if 'USD' in str(currency) or 'Dólares' in str(currency):
                currency_simple = 'Dólares'
            elif 'COP' in str(currency) or 'Pesos' in str(currency):
                currency_simple = 'Pesos'
            else:
                currency_simple = None
                issues.append("Unknown currency type")
        else:
            currency_simple = None
        
        # Check for missing salary
        if pd.isna(salary):
            issues.append("Missing salary")
        
        # Check for unrealistic salary values
        if not pd.isna(salary) and salary > 0:
            if currency_simple == 'Dólares':
                if salary < 5000:  # Less than $5k annual
                    issues.append(f"Unrealistic low USD salary: ${salary}")
                elif salary > 500000:  # More than $500k annual
                    issues.append(f"Unrealistic high USD salary: ${salary}")
            elif currency_simple == 'Pesos':
                if salary < 10000000:  # Less than 10M COP
                    issues.append(f"Unrealistic low COP salary: {salary/1e6:.1f}M")
                elif salary > 1000000000:  # More than 1B COP
                    issues.append(f"Unrealistic high COP salary: {salary/1e6:.1f}M")
        
        # Check for invalid experience
        if not pd.isna(experience):
            if experience < 0 or experience > 50:
                issues.append(f"Invalid experience: {experience}")
        
        # If there are issues, record elimination and skip
        if issues:
            elimination_reasons.append({
                'index': idx,
                'issues': '; '.join(issues),
                'currency': currency,
                'experience': experience,
                'language': language,
                'salary_1': total_salary_1,
                'salary_2': total_salary_2
            })
            continue
        
        # Process the valid record
        try:
            # Map education level to numeric (1-5)
            education_mapping = {
                'Técnico': 2,
                'Tecnólogo': 3,
                'Pregrado': 4,
                'Posgrado': 5
            }
            education_numeric = education_mapping.get(education, 1)  # Default to 1 if not found
            
            # Map English level to numeric (0-4)
            english_mapping = {
                'A1': 0,
                'A2': 1,
                'B1': 2,
                'B2': 3,
                'C1': 4,
                'C2': 4
            }
            # Extract level from the full description
            english_numeric = 0  # Default
            if not pd.isna(english_level):
                for level, value in english_mapping.items():
                    if level in str(english_level):
                        english_numeric = value
                        break
            
            # Simplify company type
            company_simple = "Sin Respuesta"
            if not pd.isna(company_type):
                if 'Extranjera' in str(company_type):
                    company_simple = "Extranjera"
                elif 'mercado extranjero' in str(company_type):
                    company_simple = "Colombiana con mercado extranjero"
                elif 'mercado nacional' in str(company_type):
                    company_simple = "Colombiana con mercado nacional"
                elif 'independiente' in str(company_type) or 'Freelance' in str(company_type):
                    company_simple = "Soy independiente (Freelance)"
            
            # Simplify workmode
            workmode_simple = "Sin Respuesta"
            if not pd.isna(workmode):
                if 'Remoto' in str(workmode):
                    workmode_simple = "Remoto"
                elif 'Presencial' in str(workmode):
                    workmode_simple = "Presencial"
                elif 'Híbrido' in str(workmode):
                    workmode_simple = "Híbrido"
            
            # Simplify contract type
            contract_simple = "Sin Respuesta"
            if not pd.isna(contract_type):
                if 'Laboral' in str(contract_type):
                    contract_simple = "Laboral"
                elif 'Prestación de servicios' in str(contract_type) or 'Contractor' in str(contract_type) or 'Independiente' in str(contract_type):
                    contract_simple = "Prestación de servicios/Contractor/Independiente"
            
            # Create the processed record
            processed_record = {
                'currency': currency_simple,
                'main-programming-language': language,
                'company-type': company_simple,
                'workmode': workmode_simple,
                'contract-type': contract_simple,
                'min-experience': int(experience),
                'max-experience': int(experience),
                'english-level': english_numeric,
                'max-title': education_numeric,
                'income-in-currency': float(salary)
            }
            
            processed_records.append(processed_record)
            
        except Exception as e:
            elimination_reasons.append({
                'index': idx,
                'issues': f'Processing error: {str(e)}',
                'currency': currency,
                'experience': experience,
                'language': language,
                'salary_1': total_salary_1,
                'salary_2': total_salary_2
            })
    
    return processed_records, elimination_reasons

def save_processed_data(processed_records, elimination_reasons):
    """Save the processed data and elimination report."""
    
    # Save processed data
    df_processed = pd.DataFrame(processed_records)
    df_processed.to_csv('salaries-2025-processed.csv', index=False)
    
    print(f"\n✅ PROCESSING COMPLETE:")
    print(f"   Processed records: {len(processed_records)}")
    print(f"   Eliminated records: {len(elimination_reasons)}")
    print(f"   Output file: salaries-2025-processed.csv")
    
    # Save elimination report
    if elimination_reasons:
        df_eliminated = pd.DataFrame(elimination_reasons)
        df_eliminated.to_csv('eliminated_records_2025.csv', index=False)
        print(f"   Elimination report: eliminated_records_2025.csv")
        
        # Show elimination breakdown
        issue_counts = {}
        for record in elimination_reasons:
            for issue in record['issues'].split('; '):
                issue_counts[issue.split(':')[0]] = issue_counts.get(issue.split(':')[0], 0) + 1
        
        print(f"\n📊 ELIMINATION BREAKDOWN:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {issue}: {count} records")
    
    return len(processed_records), len(elimination_reasons)

def main():
    """Main processing function."""
    print("COLOMBIA SALARY SURVEY 2025 - DATA PROCESSING")
    print("=" * 60)
    
    try:
        # Process the data
        processed_records, elimination_reasons = load_and_process_data()
        
        # Save results
        processed_count, eliminated_count = save_processed_data(processed_records, elimination_reasons)
        
        # Summary
        total_original = processed_count + eliminated_count
        elimination_rate = (eliminated_count / total_original) * 100
        
        print(f"\n📈 SUMMARY:")
        print(f"   Original records: {total_original}")
        print(f"   Processed records: {processed_count}")
        print(f"   Elimination rate: {elimination_rate:.1f}%")
        
        print(f"\n✅ Data processing complete. The processed data is ready for the React application.")
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
