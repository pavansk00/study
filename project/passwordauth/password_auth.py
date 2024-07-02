import secrets
import string
import hashlib
from getpass import getpass

user_details_file_path = "user.txt"

PUNCTUATIONS = "@$%&*#!^_~"

DEFAULT_PASSWORD_LENGTH = 10

INVALID_LENGTH_MESSAGE = F'''Password length must be between 8 and 16. 
Password length must be a number.
Generating password with default length of {DEFAULT_PASSWORD_LENGTH} characters.
'''

def generate_password(length=10):
    characters = string.ascii_letters + string.digits +PUNCTUATIONS
    pwd = ''.join(secrets.choice(characters) for _ in range(length))
    return pwd

def hash_pasword(pwd):
    pwd_byte = pwd.encode("utf-8")
    hash_pasword = hashlib.sha256(pwd_byte).hexdigest()
    return hash_pasword

def save_user(username, hashed_pwd):
    """Save user-details to the users detail file"""
    with open(user_details_file_path, "a") as f:
        f.write(f"{username} {hashed_pwd}\n")
        
def user_exists(username):
    try:
        with open(user_details_file_path, "r") as f:
            for line in f:
                parts = line.split()
                if parts[0] == username:
                    return True
    except FileNotFoundError as fl_err:
        print(f"{fl_err.args[-1]}: {user_details_file_path}")
        print(f"System will create file: {user_details_file_path}")
    return False
        
def authentication(username, password):
    with open(user_details_file_path , 'r') as f:
        for line in f:
            part = line.split()
            if part[0] == username:
                hashed_pasword = part[1]
                if hashed_pasword == hash_pasword(password):
                    return True
                else:
                    return False
    return False

def validate_input(password_length):
    try:
        password_length = int(password_length)
        if password_length < 8 or password_length > 16:
            raise ValueError("Password length must be between 8 and 16")
        return password_length
    except ValueError:
        print(INVALID_LENGTH_MESSAGE)
        return DEFAULT_PASSWORD_LENGTH
    
def register():
    username = input("Enter username: ")
    if user_exists(username):
        print("User already exists.")
        return
    length = input("Enter Auto Generated Password Length (Number 8-16): ")
    length = validate_input(length)
    password = generate_password(length)

    hashed_password = hash_pasword(password)
    save_user(username, hashed_password)
    print("User created successfully.")
    print("Your password is:", password)
        
def login():
    username = input("Enter username: ")
    if not user_exists(username):
        print("User does not exist.")
        return

    password = getpass("Password: ")
    if not authentication(username, password):
        print("Incorrect password.")
        return
    print("Login successful.")    
                
    
def main():
    while True:
        print("1. Register\n2. Login\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

