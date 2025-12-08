import json
import os
from pathlib import Path

class ModelConfigLoader:
    
    def __init__(self, config_path=None):
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.config_path = project_root / "ml" / "models" / "model_params.json"
            
            if not self.config_path.exists():
                self.config_path = Path("model_params.json")
        else:
            self.config_path = Path(config_path)
        
        self.config_cache = None
    
    def _load_config_file(self):
        if self.config_cache is not None:
            return self.config_cache
        
        if not self.config_path.exists():
            print(f"⚠️  WARNING: Config file '{self.config_path}' not found")
            print(f"   Using sklearn default parameters for all models")
            self.config_cache = {}
            return self.config_cache
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_cache = json.load(f)
            print(f"✓ Loaded model parameters from: {self.config_path}")
            return self.config_cache
        
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Invalid JSON in config file: {e}")
            print(f"   Using sklearn default parameters for all models")
            self.config_cache = {}
            return self.config_cache
        
        except Exception as e:
            print(f"❌ ERROR: Failed to load config file: {e}")
            print(f"   Using sklearn default parameters for all models")
            self.config_cache = {}
            return self.config_cache
    
    def _convert_type(self, value, param_name):
        if value is None:
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            if value.lower() == "none":
                return None
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
            return value
        
        if isinstance(value, (list, dict)):
            return value
        
        return value
    
    def _validate_params(self, model_name, params):
        validated = {}
        
        for param_name, param_value in params.items():
            try:
                converted_value = self._convert_type(param_value, param_name)
                
                if param_name in ['n_estimators', 'n_neighbors', 'max_iter']:
                    if isinstance(converted_value, int) and converted_value <= 0:
                        print(f"⚠️  WARNING: {model_name}.{param_name} must be > 0, got {converted_value}")
                        print(f"   Skipping parameter {param_name}")
                        continue
                
                if param_name == 'max_depth':
                    if converted_value is not None and isinstance(converted_value, int) and converted_value <= 0:
                        print(f"⚠️  WARNING: {model_name}.{param_name} must be > 0 or None, got {converted_value}")
                        print(f"   Skipping parameter {param_name}")
                        continue
                
                if param_name == 'C':
                    if isinstance(converted_value, (int, float)) and converted_value <= 0:
                        print(f"⚠️  WARNING: {model_name}.{param_name} must be > 0, got {converted_value}")
                        print(f"   Skipping parameter {param_name}")
                        continue
                
                validated[param_name] = converted_value
                
            except Exception as e:
                print(f"⚠️  WARNING: Failed to validate {model_name}.{param_name}: {e}")
                print(f"   Skipping parameter {param_name}")
                continue
        
        return validated
    
    def load_model_params(self, model_name):
        config = self._load_config_file()
        
        if model_name not in config:
            print(f"⚠️  WARNING: Model '{model_name}' not found in config file")
            print(f"   Using sklearn default parameters for {model_name}")
            return {}
        
        params = config[model_name]
        
        if not params:
            print(f"ℹ️  INFO: No parameters specified for '{model_name}' in config")
            print(f"   Using sklearn default parameters")
            return {}
        
        validated_params = self._validate_params(model_name, params)
        
        print(f"✓ Loaded {len(validated_params)} parameters for {model_name}: {list(validated_params.keys())}")
        
        return validated_params
    
    def get_all_models(self):
        config = self._load_config_file()
        return list(config.keys())
    
    def reload_config(self):
        self.config_cache = None
        return self._load_config_file()


_loader_instance = None

def get_loader():
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = ModelConfigLoader()
    return _loader_instance

def load_model_params(model_name):
    loader = get_loader()
    return loader.load_model_params(model_name)