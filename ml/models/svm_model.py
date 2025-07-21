from sklearn.svm import SVC

class SVMModel:
    @staticmethod
    def build_model():
        model = SVC(
            kernel='rbf', 
            C=1.0, 
            gamma='scale', 
            random_state=42
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