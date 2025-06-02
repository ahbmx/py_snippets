Here's how to integrate **Option 2 (Encrypted Config Files)** into a Python script, making it secure and easy to use:

---

### **Step-by-Step Implementation**

#### **1. Install Required Packages**
```bash
pip install cryptography configparser
```

#### **2. Create `secure_config.ini` (Encrypted Config File)**
```ini
[Database]
user = gAAAAABmY5XK... (encrypted)
password = gAAAAABmY5XK... (encrypted)

[API]
key = gAAAAABmY5XK... (encrypted)
```

#### **3. Create `credentials_manager.py`**
```python
from cryptography.fernet import Fernet
import configparser
import base64
import os

class CredentialsManager:
    def __init__(self, config_file="secure_config.ini", key_file="secret.key"):
        self.config_file = config_file
        self.key_file = key_file
        self.key = self._load_or_create_key()

    def _load_or_create_key(self):
        """Load encryption key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        f = Fernet(self.key)
        return f.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt an encrypted string."""
        f = Fernet(self.key)
        return f.decrypt(ciphertext.encode()).decode()

    def save_credentials(self, credentials: dict):
        """Save encrypted credentials to config file."""
        config = configparser.ConfigParser()
        for section, data in credentials.items():
            config[section] = {}
            for key, value in data.items():
                encrypted_value = self.encrypt(value)
                config[section][key] = encrypted_value

        with open(self.config_file, "w") as f:
            config.write(f)

    def load_credentials(self) -> dict:
        """Load and decrypt credentials from config file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file '{self.config_file}' not found.")

        config = configparser.ConfigParser()
        config.read(self.config_file)

        credentials = {}
        for section in config.sections():
            credentials[section] = {}
            for key, value in config[section].items():
                decrypted_value = self.decrypt(value)
                credentials[section][key] = decrypted_value

        return credentials
```

---

### **4. Usage Example**
#### **(A) First Run: Store Encrypted Credentials**
```python
from credentials_manager import CredentialsManager

# Initialize manager
manager = CredentialsManager()

# Define credentials (plaintext)
credentials = {
    "Database": {
        "user": "admin",
        "password": "SuperSecret123!"
    },
    "API": {
        "key": "abc123xyz456"
    }
}

# Encrypt and save to config file
manager.save_credentials(credentials)
print("Credentials encrypted and saved!")
```

#### **(B) Subsequent Runs: Retrieve Decrypted Credentials**
```python
from credentials_manager import CredentialsManager

# Initialize manager
manager = CredentialsManager()

# Load and decrypt credentials
creds = manager.load_credentials()

# Use in your script
db_user = creds["Database"]["user"]
db_pass = creds["Database"]["password"]
api_key = creds["API"]["key"]

print(f"DB User: {db_user}")
print(f"DB Pass: {db_pass}")
print(f"API Key: {api_key}")
```

---

### **5. Security Notes**
1. **`secret.key`** is the encryption key → **Never commit to Git!** (Add to `.gitignore`).
2. **`secure_config.ini`** contains encrypted data → Safe to store (but still restrict access).
3. **Rotate keys periodically** for better security.

---

### **6. Folder Structure**
```
project/
│
├── .gitignore           # Add secret.key and secure_config.ini
├── credentials_manager.py
├── secure_config.ini    # (Generated)
└── secret.key           # (Generated)
```

---

### **Why This Works**
✅ **No plaintext passwords** in config files.  
✅ **Key is stored separately** (not in source code).  
✅ **Config file can be shared** (if key is secured).  
✅ **Easy to integrate** into existing scripts.  

For **production**, consider **AWS Secrets Manager** or **Azure Key Vault**, but this is great for **local/dev environments**. 🚀
