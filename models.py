import numpy as np
import pandas as pd

data = pd.read_csv("iris.csv")
data.columns = ["Sepal_len_cm", "Sepal_wid_cm", "Petal_len_cm", "Petal_wid_cm", "Type"]
data.head(10)


class perceptron:
    def activation_func(value):
        return (np.exp(value) - np.exp(-value)) / (np.exp(value) + np.exp(-value))

    def perceptron_train(in_data, labels, alpha):
        X = np.array(in_data)
        y = np.array(labels)
        weights = np.random.random(X.shape[1])
        original = weights
        bias = np.random.random_sample()
        for key in range(X.shape[0]):
            a = activation_func(np.matmul(np.transpose(weights), X[key]))
            yn = 0
            if a >= 0.7:
                yn = 1
            elif a <= (-0.7):
                yn = -1
            weights = weights + alpha * (yn - y[key]) * X[key]
            print("Iteration " + str(key) + ": " + str(weights))
        print("Difference: " + str(weights - original))
        return weights

    def perceptron_test(in_data, label_shape, weights):
        X = np.array(in_data)
        y = np.zeros(label_shape)
        for key in range(X.shape[1]):
            a = activation_func((weights * X[key]).sum())
            y[key] = 0
            if a >= 0.7:
                y[key] = 1
            elif a <= (-0.7):
                y[key] = -1
        return y

    def score(result, labels):
        difference = result - np.array(labels)
        correct_ctr = 0
        for elem in range(difference.shape[0]):
            if difference[elem] == 0:
                correct_ctr += 1
        score = correct_ctr * 100 / difference.size
        return score
