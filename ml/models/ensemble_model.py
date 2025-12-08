from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from model_config_loader import load_model_params
except ImportError:
    def load_model_params(model_name):
        print(f"⚠️  WARNING: model_config_loader not found, using sklearn defaults for {model_name}")
        return {}

class EnsembleModel:
    @staticmethod
    def build_model():
        ensemble_params = load_model_params('Ensemble')
        
        try:
            rf_params = load_model_params('RandomForest')
            svm_params = load_model_params('SVM')
            lr_params = load_model_params('LogisticRegression')
        except:
            rf_params = {}
            svm_params = {}
            lr_params = {}
        
        if ensemble_params.get('voting') == 'soft':
            svm_params['probability'] = True
        
        base_models = [
            ('rf', RandomForestClassifier(**rf_params)),
            ('svm', SVC(**svm_params)),
            ('lr', LogisticRegression(**lr_params))
        ]
        
        model = VotingClassifier(estimators=base_models, **ensemble_params)
        return model
    
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction