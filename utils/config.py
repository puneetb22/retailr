"""
Configuration utilities for POS system
Handles loading and saving application settings
"""

import os
import json

CONFIG_FILE = "pos_config.json"

def load_config():
    """Load configuration from file or return default if not exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return get_default_config()
    else:
        # Return default config
        return get_default_config()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_default_config():
    """Return default configuration"""
    return {
        "shop_name": "Agritech Products Shop",
        "shop_address": "Main Road, Maharashtra",
        "shop_phone": "+91 1234567890",
        "shop_gst": "27AABCU9603R1ZX",
        "invoice_prefix": "AGT",
        "invoice_template": "default",
        "low_stock_threshold": 10,
        "version": "1.0.0"
    }