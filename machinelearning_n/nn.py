import numpy as np

def main():
    """
    This is sample code for linear regression, which demonstrates how to use the
    Graph class.

    Once you have answered Questions 2 and 3, you can run `python nn.py` to
    execute this code.
    """

    # This is our data, where x is a 4x2 matrix and y is a 4x1 matrix
    x = np.array([[0., 0.],
                  [0., 1.],
                  [1., 0.],
                  [1., 1.]])
    y = np.dot(x, np.array([[7.],
                            [8.]])) + 3

    # Let's construct a simple model to approximate a function from 2D
    # points to numbers, f(x) = x_0 * m_0 + x_1 * m_1 + b
    # Here m and b are variables (trainable parameters):
    m = Variable(2,1)
    b = Variable(1)

    # We train our network using batch gradient descent on our data
    for iteration in range(10000):
        # At each iteration, we first calculate a loss that measures how
        # good our network is. The graph keeps track of all operations used
        graph = Graph([m, b])
        input_x = Input(graph, x)
        input_y = Input(graph, y)
        xm = MatrixMultiply(graph, input_x, m)
        xm_plus_b = MatrixVectorAdd(graph, xm, b)
        loss = SquareLoss(graph, xm_plus_b, input_y)
        # Then we use the graph to perform backprop and update our variables
        graph.backprop()
        graph.step(0.01)

    # After training, we should have recovered m=[[7],[8]] and b=[3]
    print("Final values are: {}".format([m.data[0,0], m.data[1,0], b.data[0]]))
    assert np.isclose(m.data[0,0], 7)
    assert np.isclose(m.data[1,0], 8)
    assert np.isclose(b.data[0], 3)
    print("Success!")

class Graph(object):
    """
    A graph that keeps track of the computations performed by a neural network
    in order to implement back-propagation.

    Each evaluation of the neural network (during both training and test-time)
    will create a new Graph. The computation will add nodes to the graph, where
    each node is either a DataNode or a FunctionNode.

    A DataNode represents a trainable parameter or an input to the computation.
    A FunctionNode represents doing a computation based on two previous nodes in
    the graph.

    The Graph is responsible for keeping track of all nodes and the order they
    are added to the graph, for computing gradients using back-propagation, and
    for performing updates to the trainable parameters.

    For an example of how the Graph can be used, see the function `main` above.
    """

    def __init__(self, variables):
        """
        Initializes a new computation graph.

        variables: a list of Variable objects that store the trainable parameters
            for the neural network.

        Hint: each Variable is also a node that needs to be added to the graph,
        so don't forget to call `self.add` on each of the variables.
        """
        "*** YOUR CODE HERE ***"

        self.graph = {} #used for get_output, get_inputs, get_gradient
        self.nodes = [] #used for get_nodes
        self.variables = variables

        for variableNode in variables:
            self.add(variableNode)

    def get_nodes(self):
        """
        Returns a list of all nodes that have been added to this Graph, in the
        order they were added. This list should include all of the Variable
        nodes that were passed to `Graph.__init__`.

        Returns: a list of nodes
        """
        return self.nodes

    def get_inputs(self, node):
        """
        Retrieves the inputs to a node in the graph. Assume the `node` has
        already been added to the graph.

        Returns: a list of numpy arrays

        Hint: every node has a `.get_parents()` method
        """
        "*** YOUR CODE HERE ***"
        inputs = []
        for par in node.get_parents():
            inputs.append(self.get_output(par)) #add null check?
        return inputs


    def get_output(self, node):
        """
        Retrieves the output to a node in the graph. Assume the `node` has
        already been added to the graph.

        Returns: a numpy array or a scalar
        """
        "*** YOUR CODE HERE ***"
        nodeData = self.graph[node]
        return nodeData[0]

    def get_gradient(self, node):
        """
        Retrieves the gradient for a node in the graph. Assume the `node` has
        already been added to the graph.

        If `Graph.backprop` has already been called, this should return the
        gradient of the loss with respect to the output of the node. If
        `Graph.backprop` has not been called, it should instead return a numpy
        array with correct shape to hold the gradient, but with all entries set
        to zero.

        Returns: a numpy array
        """
        "*** YOUR CODE HERE ***"
        return self.graph[node][1]


    def add(self, node):
        """
        Adds a node to the graph.

        This method should calculate and remember the output of the node in the
        forwards pass (which can later be retrieved by calling `get_output`)
        We compute the output here because we only want to compute it once,
        whereas we may wish to call `get_output` multiple times.

        Additionally, this method should initialize an all-zero gradient
        accumulator for the node, with correct shape.
        """
        "*** YOUR CODE HERE ***"

        self.nodes.append(node)
        inputs = self.get_inputs(node)
        output = node.forward(inputs)
                        #[output, gradient, has_called_backprop]
        self.graph[node] = [output, np.zeros_like(output), False]

    def backprop(self):
        """
        Runs back-propagation. Assume that the very last node added to the graph
        represents the loss.

        After back-propagation completes, `get_gradient(node)` should return the
        gradient of the loss with respect to the `node`.

        Hint: the gradient of the loss with respect to itself is 1.0, and
        back-propagation should process nodes in the exact opposite of the order
        in which they were added to the graph.
        """
        loss_node = self.get_nodes()[-1]
        assert np.asarray(self.get_output(loss_node)).ndim == 0

        "*** YOUR CODE HERE ***"

        self.graph[loss_node][1] = 1.0

        for node in self.nodes[::-1]: #this includes the loss_node, don't know if I should start after
            self.graph[node][2] = True
            inputs = self.get_inputs(node)
            gradient = self.get_gradient(node) #this returns a numpy array when spec suggests this to be a number
            backwardOuput = node.backward(inputs, gradient)
            # print(backwardOuput)
            #Use the outputs of the backward method to update the gradient accumulators for the node's parents.
            for parent, backOut in zip(node.get_parents(), backwardOuput):
                # zip(node.get_parents(), backwardOuput)
                # print(backOut)
                self.graph[parent][1] += backOut



    def step(self, step_size):
        """
        Updates the values of all variables based on computed gradients.
        Assume that `backprop()` has already been called, and that gradients
        have already been computed.

        Hint: each Variable has a `.data` attribute
        """
        "*** YOUR CODE HERE ***"
        for variableNode in self.variables:
            variableNode.data = variableNode.data - (step_size * self.graph[variableNode][1])

class DataNode(object):
    """
    DataNode is the parent class for Variable and Input nodes.

    Each DataNode must define a `.data` attribute, which represents the data
    stored at the node.
    """

    @staticmethod
    def get_parents():
        # A DataNode has no parent nodes, only a `.data` attribute
        return []

    def forward(self, inputs):
        # The forwards pass for a data node simply returns its data
        return self.data

    @staticmethod
    def backward(inputs, gradient):
        # A DataNode has no parents or inputs, so there are no gradients to
        # compute in the backwards pass
        return []

class Variable(DataNode):
    """
    A Variable stores parameters used in a neural network.

    Variables should be created once and then passed to all future Graph
    constructors. Use `.data` to access or modify the numpy array of parameters.
    """

    def __init__(self, *shape):
        """
        Initializes a Variable with a given shape.

        For example, Variable(5) will create 5-dimensional vector variable,
        while Variable(10, 10) will create a 10x10 matrix variable.

        The initial value of the variable before training starts can have a big
        effect on how long the network takes to train. The provided initializer
        works well across a wide range of applications.
        """
        assert shape
        limit = np.sqrt(3.0 / np.mean(shape))
        self.data = np.random.uniform(low=-limit, high=limit, size=shape)

class Input(DataNode):
    """
    An Input node packages a numpy array into a node in a computation graph.
    Use this node for inputs to your neural network.

    For trainable parameters, use Variable instead.
    """

    def __init__(self, graph, data):
        """
        Initializes a new Input and adds it to a graph.
        """
        assert isinstance(data, np.ndarray), "data must be a numpy array"
        assert data.dtype.kind == "f", "data must have floating-point entries"
        self.data = data
        graph.add(self)

class FunctionNode(object):
    """
    A FunctionNode represents a value that is computed based on other nodes in
    the graph. Each function must implement both a forward and backward pass.
    """

    def __init__(self, graph, *parents):
        self.parents = parents
        graph.add(self)

    def get_parents(self):
        return self.parents

    @staticmethod
    def forward(inputs):
        raise NotImplementedError

    @staticmethod
    def backward(inputs, gradient):
        raise NotImplementedError

class Add(FunctionNode):
    """
    Adds two vectors or matrices, element-wise

    Inputs: [x, y]
        x may represent either a vector or a matrix
        y must have the same shape as x
    Output: x + y
    """

    @staticmethod
    def forward(inputs):
        "*** YOUR CODE HERE ***"
        # print('input',inputs)
        # print('sum',np.sum(inputs,axis = 0))
        #if the inputs are (array([1,2]), array([2,1])), the result is array[3,3]
        return np.sum(inputs,axis = 0)

    @staticmethod
    def backward(inputs, gradient):
        "*** YOUR CODE HERE ***"
        # print('inputs',inputs)
        # print('gradient', gradient)
        #there are two parent nodes in the quesiton, but gradient and input may have multi-dimensions i.e.
        # input = array of shape(1,5) and so does gradient. Their shapes are correspondent.
        
        new_gradient_val = gradient
        # print(gradient)
        # num_of_parent_nodes = len(inputs)#all is 2 #how many parents nodes are there, so we need how many gradients returned back in a list
        
        
        # new_g_shape = inputs[0].shape[0]#each gradient in the list has same shape as inputs values' shape, but we don't need it\
        #because each gradient given already has the same shape as the inputs
        
        # g = new_gradient_val
        # print('new_gradient_val',g)
        g = np.array(new_gradient_val)
        g_list = [g]
        
        
        return g_list*2


class MatrixMultiply(FunctionNode):
    """
    Represents matrix multiplication.

    Inputs: [A, B]
        A represents a matrix of shape (n x m)
        B represents a matrix of shape (m x k)
    Output: a matrix of shape (n x k)
    """

    @staticmethod
    def forward(inputs):
        "*** YOUR CODE HERE ***"
        # print('input',inputs)
        return np.matmul(inputs[0],inputs[1])


    @staticmethod
    def backward(inputs, gradient):
        "*** YOUR CODE HERE ***"
        # print('A shape',inputs[0].shape)
        # print('B shape',inputs[1].shape)
        # # print("\n")
        # print('gradient',gradient.shape)

        return [np.matmul(gradient,inputs[1].T),np.matmul(inputs[0].T,gradient)]

class MatrixVectorAdd(FunctionNode):
    """
    Adds a vector to each row of a matrix.

    Inputs: [A, x]
        A represents a matrix of shape (n x m)
        x represents a vector (m)
    Output: a matrix of shape (n x m)
    """

    @staticmethod
    def forward(inputs):
        "*** YOUR CODE HERE ***"
        return inputs[0] + inputs[1]

    @staticmethod
    def backward(inputs, gradient):
        "*** YOUR CODE HERE ***"
        # print('A shape',inputs[0].shape)
        # print('x shape',inputs[1].shape)
        # # print("\n")
        # print('gradient',gradient.shape)
        # A = inputs[0]
        # B = inputs[1]
        # np.matmul(np.ones((1,A.shape[0])),gradient) this returned the same as np.sum(gradient, axis = 0) but the
        # in the form of a 2 array, the correct form is list(or 1-d vector form)
        return [gradient, np.sum(gradient,axis = 0)]

class ReLU(FunctionNode):
    """
    An element-wise Rectified Linear Unit nonlinearity: max(x, 0).
    This nonlinearity replaces all negative entries in its input with zeros.

    Input: [x]
        x represents either a vector or matrix
    Output: same shape as x, with no negative entries
    """

    @staticmethod
    def forward(inputs):
        "*** YOUR CODE HERE ***"
        # print('input',inputs)
        return inputs[0].clip(0,float('inf'))

    @staticmethod
    def backward(inputs, gradient):
        "*** YOUR CODE HERE ***"
        # print('input',inputs)
        inputs = inputs[0]
        clear_negative = np.where(inputs > 0, inputs, 0)
        helper = np.where(clear_negative == 0,clear_negative, 1)
        # print('help',helper)
        return [helper *gradient]
        

class SquareLoss(FunctionNode):
    """
    Inputs: [a, b]
        a represents a matrix of size (batch_size x dim)
        b must have the same shape as a
    Output: a number

    This node first computes 0.5 * (a[i,j] - b[i,j])**2 at all positions (i,j)
    in the inputs, which creates a (batch_size x dim) matrix. It then calculates
    and returns the mean of all elements in this matrix.
    """

    @staticmethod
    def forward(inputs):
        "*** YOUR CODE HERE ***"
        a = inputs[0]
        b = inputs[1]
        return np.mean(0.5*(a-b)**2)

    @staticmethod
    def backward(inputs, gradient):
        "*** YOUR CODE HERE ***"
        a = inputs[0]
        b = inputs[1]
        flat_dim = a.shape[0]*a.shape[1]
        return [(a-b)*gradient/flat_dim,(b-a)*gradient/flat_dim]

class SoftmaxLoss(FunctionNode):
    """
    A batched softmax loss, used for classification problems.

    IMPORTANT: do not swap the order of the inputs to this node!

    Inputs: [logits, labels]
        logits: a (batch_size x num_classes) matrix of scores, that is typically
            calculated based on previous layers. Each score can be an arbitrary
            real number.
        labels: a (batch_size x num_classes) matrix that encodes the correct
            labels for the examples. All entries must be non-negative and the
            sum of values along each row should be 1.
    Output: a number

    We have provided the complete implementation for your convenience.
    """
    @staticmethod
    def softmax(input):
        exp = np.exp(input - np.max(input, axis=1, keepdims=True))
        return exp / np.sum(exp, axis=1, keepdims=True)

    @staticmethod
    def forward(inputs):
        softmax = SoftmaxLoss.softmax(inputs[0])
        labels = inputs[1]
        assert np.all(labels >= 0), \
            "Labels input to SoftmaxLoss must be non-negative. (Did you pass the inputs in the right order?)"
        assert np.allclose(np.sum(labels, axis=1), np.ones(labels.shape[0])), \
            "Labels input to SoftmaxLoss do not sum to 1 along each row. (Did you pass the inputs in the right order?)"

        return np.mean(-np.sum(labels * np.log(softmax), axis=1))

    @staticmethod
    def backward(inputs, gradient):
        softmax = SoftmaxLoss.softmax(inputs[0])
        return [
            gradient * (softmax - inputs[1]) / inputs[0].shape[0],
            gradient * (-np.log(softmax)) / inputs[0].shape[0]
        ]

if __name__ == '__main__':
    main()
