from sklearn.tree import DecisionTreeClassifier as SKLearnDecisionTreeClassifier

class DecisionTreeModel:
    @staticmethod
    def build_model():
        model = SKLearnDecisionTreeClassifier(random_state=42)
        return model
    
    @staticmethod
    def train_model(model, X_train, y_train):
        model.fit(X_train, y_train)
        return model
    
    @staticmethod
    def predict(model, X_test):
        prediction = model.predict(X_test)
        return prediction