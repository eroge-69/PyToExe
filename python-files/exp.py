import matplotlib.pyplot as plt
import numpy as np
import math
nrs=int(input())
N = int(input())
epochs = int(input())
eta = float(input())
mini_batch_size = int(input())
output_massive = np.zeros (N)
dispersion = 0
exp_dispersion = np.zeros (epochs)
class NeuralNetwork(object):
    
    def __init__(self, sizes):
        np.random.seed(1)
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]
    
    def sigmoid(self, x):
        return 1.0/(1.0 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return np.exp(-x)/((1.0 + np.exp(-x))**2)
    
    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            print("a=", a)
            print("b=", b)
            print("w=", w)
            a = self.sigmoid(np.dot(w, a)+b)
            print("a=", a)
        return a
    
    def SGD (self, training_data, epochs, mini_batch_size, eta, dispersion):
        n = len(training_data)
        for i in range (epochs):
            np.random.shuffle(training_data)
            for j in range(N):
                 output_massive[j] = self.feedforward(training_data[j][0]).item()
            mini_batches = [training_data[k:k+mini_batch_size] for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch (mini_batch, eta)
            exp_dispersion [i] = self.explained_dispersion(dispersion).item()
             
    def update_mini_batch(self, mini_batch, eta):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb for b, nb in zip(self.biases, nabla_b)]        
    
    def backprop(self, x, y):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = self.sigmoid(z)
            activations.append(activation)
        delta = self.cost_derivative(activations[-1], y) * self.sigmoid_derivative(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = self.sigmoid_derivative(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)
    
    def explained_dispersion(self, dispersion):
        S = 0
        for j in range (N):
            S += (training_data[j][1]-output_massive[j])**2
        S = S/N
        ex_dispersion = 100*(dispersion-S)/dispersion
        return  ex_dispersion
    
    def cost_derivative(self, output_activations, y):
        return (output_activations-y)
    
if __name__ == "__main__":
     NeuralNetwork = NeuralNetwork ([1, nrs, 1])
     inputs0 = (np.random.uniform(0, 1) for i in range(N))
     arrtrain_inputs0 = np.fromiter(inputs0, float).T
     outputs0 = (math.log10(1+arrtrain_inputs0[i]) for i in range(N))
     arrtrain_outputs0 = np.fromiter(outputs0, float).T
     inputs = (np.random.uniform(0, 1) for i in range(N))
     arrtrain_inputs = np.fromiter(inputs, float)
     outputs = (math.log10(1+arrtrain_inputs[i]) for i in range(N))
     arrtrain_outputs = np.fromiter(outputs, float)
     training_data = list(zip(arrtrain_inputs0, arrtrain_outputs0))
     middle_y = np.full((N, 1), math.fsum(arrtrain_outputs0)/len(arrtrain_outputs0)).T
     dispersion0 = np.subtract(arrtrain_outputs0, middle_y).T
     dispersion = math.fsum (dispersion0[i].item()**2 for i in range (N))/N
     output_massive_before = np.zeros(N)
     for j in range(N):
          output_massive_before[j] = NeuralNetwork.feedforward(arrtrain_inputs0[j]).item()
     NeuralNetwork.SGD (training_data, epochs, mini_batch_size, eta,  dispersion)
     for j in range(N):
          output_massive[j] = NeuralNetwork.feedforward(arrtrain_inputs[j]).item()
     exp_dispersion [0] = 0
     fig, ax = plt.subplots()
     ax.plot(range(1, epochs+1), exp_dispersion, 'bo', label='learning', linewidth=1)
     plt.xlabel("epoch")
     plt.ylabel("explained dispersion, %")
     ax.legend(frameon=False)
     plt.show()
     fig, bx = plt.subplots()
     bx.plot(arrtrain_inputs0, arrtrain_outputs0 , 'bo', label='actual')
     bx.plot(arrtrain_inputs0, output_massive_before, 'ro', label='before_learning')
     bx.plot(arrtrain_inputs, output_massive, 'go', label='after_learning')
     plt.xlabel("X")
     plt.ylabel("log10(1+x)")
     ax.legend(frameon=False)
     plt.show()
     
     
    