from sklearn.neighbors import KNeighborsClassifier
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

class KNNModel:
    @staticmethod
    def build_model():
        params = load_model_params('KNN')
        model = KNeighborsClassifier(**params)
        return model
        
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
        
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction