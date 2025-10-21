import random
import string

def generate_password(min_length: int = 10, max_length: int = 15) -> str:
    length = random.randint(min_length, max_length)
    
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(special_chars)
    ]
    
    all_chars = uppercase + lowercase + digits + special_chars
    password += [random.choice(all_chars) for _ in range(length - 4)]
    
    random.shuffle(password)
    
    return ''.join(password)
