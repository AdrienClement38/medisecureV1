from shared.services.authenticator.basic_authenticator import BasicAuthenticator
import traceback

try:
    auth = BasicAuthenticator()
    password = "test_password"
    print(f"Hashing password: {password}")
    hashed = auth.get_password_hash(password)
    print(f"Hashed: {hashed}")
    
    print(f"Verifying password...")
    result = auth.verify_password(password, hashed)
    print(f"Verification result: {result}")

    print("Verifying wrong password...")
    result_wrong = auth.verify_password("wrong", hashed)
    print(f"Wrong password result: {result_wrong}")
    
except Exception:
    traceback.print_exc()
