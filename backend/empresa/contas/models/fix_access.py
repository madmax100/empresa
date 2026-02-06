
import os

file_path = r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa\contas\models\access.py'
snippet_path = r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa\contas\models\notas_consumo_snippet.py'

# 1. Read and truncate corrupted file
try:
    with open(file_path, 'rb') as f:
        content = f.read()

    # Find the last valid marker from EstoqueInicial
    marker = b"super().save(*args, **kwargs)"
    idx = content.rfind(marker)

    if idx != -1:
        print(f"Marker found at index {idx}")
        # Keep content up to the marker + length of marker
        clean_content = content[:idx + len(marker)]
        
        # Write back the clean content
        with open(file_path, 'wb') as f:
            f.write(clean_content)
            f.write(b"\n\n")
        print("File truncated successfully.")
    else:
        print("Marker not found! Aborting truncation.")
        exit(1)

    # 2. Append the snippet correctly
    if os.path.exists(snippet_path):
        with open(snippet_path, 'r', encoding='utf-8') as f:
            snippet_content = f.read()
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(snippet_content)
        print("Snippet appended successfully.")
    else:
        print("Snippet file not found!")
        exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)
