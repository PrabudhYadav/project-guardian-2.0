import json
import csv
import re
import sys
import ast 

def is_phone(value):
    return bool(re.match(r'^(?:\+91[-\s]?)?\d{10}$', str(value)))

def is_aadhar(value):
    cleaned = re.sub(r'\s+', '', str(value))
    return bool(re.match(r'^\d{12}$', cleaned))

def is_passport(value):
    return bool(re.match(r'^[A-Z][0-9]{7,8}$', str(value)))

def is_upi(value):
    return bool(re.match(r'^[\w.-]+@(upi|ybl|axisbank|phonepe|gpay|oksbi|okicici|okaxis|okhdfcbank|paytm|apl|jio|airtel)$', str(value)))

def mask_phone(value):
    value = re.sub(r'^\+91[-\s]?', '+91-', str(value)) 
    if value.startswith('+91-'):
        return '+91-' + value[5:7] + 'X' * 6 + value[-2:]
    return value[:2] + 'X' * 6 + value[-2:]

def mask_aadhar(value):
    return value[:4] + 'X' * 4 + value[-4:]

def mask_passport(value):
    return value[0] + 'X' * (len(value) - 2) + value[-1]

def mask_upi(value):
    local, bank = value.split('@', 1)
    masked_local = local[:len(local)//2] + 'X' * (len(local) - len(local)//2)
    return masked_local + '@' + bank

def mask_name(value):
    words = re.split(r'\s+', value)
    masked_words = [w[0] + 'X' * (len(w) - 1) for w in words if len(w) > 0]
    return ' '.join(masked_words)

def mask_email(value):
    if '@' not in value:
        return value
    local, domain = value.split('@', 1)
    if '.' in local:
        parts = local.split('.')
        masked_parts = [p[0] + 'X' * (len(p) - 1) for p in parts if len(p) > 0]
        masked_local = '.'.join(masked_parts)
    else:
        masked_local = local[0] + 'X' * (len(local) - 1) if len(local) > 0 else ''
    return masked_local + '@' + domain

def mask_address(value):
    parts = [p.strip() for p in value.split(',')]
    masked_parts = []
    for p in parts:
        if p.isdigit():
            masked_parts.append('X' * len(p))
        else:
            masked_parts.append(' '.join(w[0] + 'X' * (len(w) - 1) for w in p.split()))
    return ', '.join(masked_parts)

def mask_device(value):
    return value[:3] + 'X' * (len(value) - 3) if len(value) > 3 else value

def mask_ip(value):
    parts = value.split('.')
    if len(parts) == 4:
        return parts[0] + '.' + parts[1] + '.X.X'
    return 'X.X.X.X'

standalone_keys = {
    'phone': (is_phone, mask_phone),
    'aadhar': (is_aadhar, mask_aadhar),
    'passport': (is_passport, mask_passport),
    'upi_id': (is_upi, mask_upi),
}

def process_record(record_id, data_json):
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError:
        fixed_json = data_json.replace("'", '"')
        try:
            data = json.loads(fixed_json)
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(data_json)
            except (ValueError, SyntaxError):
                fixed_json = re.sub(r'([0-9a-zA-Z"])\s*(["{])', r'\1,\2', fixed_json)
                try:
                    data = json.loads(fixed_json)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON for record_id: {record_id}")
                    print(data_json)
                    print(e)
                    sys.exit(1)

    standalone_present = False
    for key, (detector, masker) in standalone_keys.items():
        if key in data and detector(str(data[key])):
            standalone_present = True
            data[key] = masker(str(data[key]))

    has_full_name = False
    if 'name' in data:
        name_val = str(data['name'])
        if len(re.split(r'\s+', name_val)) >= 2:
            has_full_name = True
    if 'first_name' in data and 'last_name' in data:
        has_full_name = True

    combo_pii = False
    if has_full_name and 'email' in data:
        combo_pii = True
    elif has_full_name and 'address' in data:
        combo_pii = True
    elif 'email' in data and 'address' in data:
        combo_pii = True
    elif (has_full_name or 'email' in data) and ('ip_address' in data or 'device_id' in data):
        combo_pii = True

    is_pii = standalone_present or combo_pii

    if combo_pii:
        if has_full_name:
            if 'name' in data:
                data['name'] = mask_name(str(data['name']))
            if 'first_name' in data:
                data['first_name'] = mask_name(str(data['first_name']))
            if 'last_name' in data:
                data['last_name'] = mask_name(str(data['last_name']))
        if 'email' in data:
            data['email'] = mask_email(str(data['email']))
        if 'address' in data:
            data['address'] = mask_address(str(data['address']))
        if 'device_id' in data:
            data['device_id'] = mask_device(str(data['device_id']))
        if 'ip_address' in data:
            data['ip_address'] = mask_ip(str(data['ip_address']))

    redacted_json = json.dumps(data, ensure_ascii=False)
    return redacted_json, is_pii


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'iscp_pii_dataset_-_Sheet1.csv'
    output_file = 'redacted_output_prabudh_kumar_yadav.csv'  # Used your name based on the path

    import os
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found. Provide the path as argument or place it in the current directory.")
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        data_col = None
        for fn in fieldnames:
            if fn.lower() == 'data_json':
                data_col = fn
                break
        if data_col is None:
            print(f"Error: No 'data_json' column found. Available columns: {fieldnames}")
            sys.exit(1)

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL, doublequote=True)
            writer.writerow(['record_id', 'redacted_data_json', 'is_pii'])
            for row in reader:
                record_id = int(row['record_id']) 
                data_json = row[data_col]
                redacted_json, is_pii = process_record(record_id, data_json)

                writer.writerow([record_id, redacted_json, is_pii])
