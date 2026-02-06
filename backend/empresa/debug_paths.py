
import os

def check_paths():
    base_path = os.getcwd()
    print(f"CWD: {base_path}")
    
    files_to_check = [
        r"InterMax.03.02.2026\Bancos\Extratos\Extratos.mdb",
        r"InterMax.03.02.2026\Bancos\Cadastros\Cadastros.mdb"
    ]
    
    for relative_path in files_to_check:
        full_path = os.path.join(base_path, relative_path)
        exists = os.path.exists(full_path)
        print(f"Checking: {full_path}")
        print(f"Exists: {exists}")
        if exists:
            print(f"Size: {os.path.getsize(full_path)} bytes")

if __name__ == "__main__":
    check_paths()
