from sklearn.ensemble import RandomForestClassifier

class RandomForestModel:
    @staticmethod
    def build_model():
        model = RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            max_depth=10, 
            n_jobs=-1
        )
        return model
    
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction