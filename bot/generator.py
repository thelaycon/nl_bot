from cryptography.fernet import Fernet


print("Choose Account Type: ")
print("1. Standard Plan")
print("2. Premium Plan")
print("           ")

plan = int(input())

def generate_key(plan):
    key = Fernet.generate_key()
    f = Fernet(key)
    if plan == 1:
        account_plan = "STPLAN".encode()
    elif plan == 2:
        account_plan = 'PRPLAN'.encode()
    else:
        raise ValueError("Choose 1 or 2")
    cipher = f.encrypt(account_plan).decode()
    cipher_a = cipher[0:50]
    cipher_b = cipher[50:]
    license_key = cipher_a + key.decode() + cipher_b
    print(license_key)


generate_key(plan)
