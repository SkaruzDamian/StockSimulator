from sklearn.linear_model import LogisticRegression

class LogisticRegressionModel:
    @staticmethod
    def build_model():
        model = LogisticRegression(random_state=42, max_iter=1000, solver='lbfgs', n_jobs=-1)
        return model
    
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction