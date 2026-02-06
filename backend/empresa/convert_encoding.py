
try:
    with open('debug_json_out.txt', 'r', encoding='utf-16') as f:
        content = f.read()
    with open('debug_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print(f"Error: {e}")
