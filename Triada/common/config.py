import os
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path=None):
        load_dotenv()

        self.settings = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.settings = yaml.safe_load(f) or {}

    def get(self, key, default=None):
        # Priority: ENV > YAML > Default
        env_key = key.upper().replace('.', '_')
        val = os.getenv(env_key)
        if val is not None:
            return val

        keys = key.split('.')
        curr = self.settings
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return default
        return curr
