from sklearn.neighbors import KNeighborsClassifier

class KNNModel:
    @staticmethod
    def build_model():
        model = KNeighborsClassifier(n_neighbors=5, algorithm='auto', n_jobs=-1)
        return model
        
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
        
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction