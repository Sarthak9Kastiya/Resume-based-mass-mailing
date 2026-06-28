import pdfplumber
import pandas as pd
from typing import List, Dict
import json
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_target_file(file_path: str) -> List[Dict]:
    """
    Parses Excel or CSV files and returns a list of dictionaries representing targets.
    Handles many real-world column naming conventions.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format for targets. Use CSV or Excel.")

        # Normalize column names to lowercase and strip whitespace
        df.columns = df.columns.str.strip().str.lower()
        
        print(f"[Parser] Detected columns: {list(df.columns)}")

        # Comprehensive column name mappings
        col_map = {
            'name': ['name', 'full name', 'target name', 'professor name', 'faculty name', 'prof name', 'professor', 'faculty'],
            'email': ['email', 'email address', 'e-mail', 'mail', 'mail id', 'mail_id', 'mailid', 'email id', 'email_id', 'emailid', 'contact email', 'e mail'],
            'organization': ['organization', 'company', 'university', 'org', 'college', 'college name', 'college_name', 'institution', 'institute', 'school', 'affiliation', 'iim'],
            'designation_or_department': ['designation', 'department', 'title', 'role', 'position', 'dept', 'area', 'area of interest', 'area_of_interest', 'specialization', 'field', 'subject', 'domain', 'expertise'],
            'provided_url': ['url', 'linkedin', 'website', 'link', 'profile', 'profile url', 'webpage', 'homepage']
        }

        def get_col(canonical_name):
            """Try exact match, then substring match."""
            # 1. Exact match
            for potential_name in col_map[canonical_name]:
                if potential_name in df.columns:
                    return potential_name
            # 2. Substring / fuzzy match: check if any known alias is contained in any actual column name
            for potential_name in col_map[canonical_name]:
                for actual_col in df.columns:
                    if potential_name in actual_col or actual_col in potential_name:
                        return actual_col
            return None

        name_col = get_col('name')
        email_col = get_col('email')
        org_col = get_col('organization')
        desig_col = get_col('designation_or_department')
        url_col = get_col('provided_url')

        print(f"[Parser] Mapped: name={name_col}, email={email_col}, org={org_col}, desig={desig_col}, url={url_col}")

        if not name_col or not email_col:
            raise ValueError(
                f"Could not find Name and Email columns. "
                f"Detected columns: {list(df.columns)}. "
                f"Name mapped to: {name_col}, Email mapped to: {email_col}. "
                f"Please ensure your file has columns for Name and Email."
            )

        targets = []
        for _, row in df.iterrows():
            if pd.isna(row[name_col]) or pd.isna(row[email_col]):
                continue  # Skip rows without name or email
            
            name_val = str(row[name_col]).strip()
            email_val = str(row[email_col]).strip()
            
            # Basic validation: email should contain @
            if '@' not in email_val:
                print(f"[Parser] Skipping row with invalid email: {email_val}")
                continue
            
            target = {
                "name": name_val,
                "email": email_val,
            }
            
            if org_col and not pd.isna(row[org_col]):
                target['organization'] = str(row[org_col]).strip()
                
            if desig_col and not pd.isna(row[desig_col]):
                target['designation_or_department'] = str(row[desig_col]).strip()
                
            if url_col and not pd.isna(row[url_col]):
                target['provided_url'] = str(row[url_col]).strip()

            # Capture dynamic data
            mapped_cols = {name_col, email_col, org_col, desig_col, url_col}
            dynamic_data = {}
            for col in df.columns:
                if col not in mapped_cols and not pd.isna(row[col]):
                    dynamic_data[col] = str(row[col]).strip()
            if dynamic_data:
                target['dynamic_data'] = json.dumps(dynamic_data)

            targets.append(target)
        
        print(f"[Parser] Successfully parsed {len(targets)} targets")
        return targets

    except Exception as e:
        print(f"Error parsing target file: {e}")
        raise e
