import os
from cryptography.fernet import Fernet

def main():
    # Prompt for .log filename (assumes key.key is in the same folder)
    log_file = input("Enter the .log filename (e.g. logfile.log): ")
    key_path = "key.key"
    
    if not os.path.exists(log_file) or not os.path.exists(key_path):
        print("Log file or key file not found in the current directory.")
        return
    
    with open(key_path, 'rb') as f:
        key = f.read()
    cipher = Fernet(key)
    
    with open(log_file, 'rb') as f:
        encrypted_lines = f.readlines()
    
    decrypted_lines = [cipher.decrypt(line.strip()).decode() for line in encrypted_lines]
    
    output_file = "decrypted_log.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(decrypted_lines))
    print(f"Decrypted content written to {output_file}")

if __name__ == "__main__":
    main()
