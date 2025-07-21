from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

class EnsembleModel:
    @staticmethod
    def build_model():
        base_models = [
            ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
            ('svm', SVC(probability=True, random_state=42)),
            ('lr', LogisticRegression(random_state=42, max_iter=1000))
        ]
        model = VotingClassifier(estimators=base_models, voting='soft', n_jobs=-1)
        return model
    
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction