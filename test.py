import random
import string

def generate_password(length=16):
    # Define character sets
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation

    # Ensure at least one character from each set
    password = [
        random.choice(lowercase_letters),
        random.choice(uppercase_letters),
        random.choice(digits),
        random.choice(special_characters)
    ]

    # Fill the rest of the password with random characters
    password.extend(random.choices(
        lowercase_letters + uppercase_letters + digits + special_characters,
        k=length - 4
    ))

    # Shuffle the characters
    random.shuffle(password)

    # Convert the list of characters to a string
    return ''.join(password)

# Generate a password
password = generate_password()
print("Generated Password:", password)
