import bcrypt
from typing import Tuple

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password (bcrypt hash)
    """
    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Password hashing failed: {str(e)}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against bcrypt hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"❌ Password verification error: {str(e)}")
        return False

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets minimum security requirements
    
    Requirements:
    - At least 6 characters
    - (Optional: At least one uppercase, one lowercase, one digit)
    
    Returns:
        (is_valid: bool, message: str)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Optional: Uncomment for stronger requirements
    # has_upper = any(c.isupper() for c in password)
    # has_lower = any(c.islower() for c in password)
    # has_digit = any(c.isdigit() for c in password)
    # 
    # if not (has_upper and has_lower and has_digit):
    #     return False, "Password must contain uppercase, lowercase, and digits"
    
    return True, "Password is valid"
