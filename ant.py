import math
import random

class Ant():
    def __init__(self, ID, start_node, colony,output):
        self.output=output
        self.ID = ID
        self.start_node = start_node
        self.colony = colony
        self.curr_node = self.start_node
        self.graph = self.colony.graph
        
        # Create a vector to store the path this ant takes through the graph.
        self.path_vec = []
        self.path_vec.append(self.start_node)
        self.path_cost = 0
        
        # Decide on the parameters for the optimizer.
        self.Beta = 1.0
        self.Q0 = 0.5
        self.Rho = 0.99
        
        # Create a vector to store the nodes of the graph that are
        # yet to be visited by the ant. 
        self.nodes_to_visit = {}
        # Store all of the nodes that are not the starting node.  
        for i in range(0, self.graph.num_nodes):
            if i != self.start_node:
                self.nodes_to_visit[i] = i

        # Create a matrix with column and row dimension equaling
        # the number of nodes in the graph and all entries 0 this
        # matrix will describe which edges have been used to make
        # the path.
        self.path_mat = []
        for i in range(0, self.graph.num_nodes):
            self.path_mat.append([0] * self.graph.num_nodes)


    def tour(self):
        """Carry out the next stage of a tour.

        Decides and store the next node the ant will move 
        to on it's tour of the graph and updates the information
        on the path and the pheromone trail.
        """
        graph = self.colony.graph
        while not self.end():
            new_node = self.next_node_rule(self.curr_node)
            # add the cost of moving to the next node to the path cost
            self.path_cost += graph.delta(self.curr_node, new_node)
            # update the path the ant is taking with the new node
            self.path_vec.append(new_node)
            # mark the edge from the current node to the new node as used
            self.path_mat[self.curr_node][new_node] = 1
            # update the pheromone trail on the new edge
            self.local_pheromone_updating_rule(self.curr_node, new_node)
            self.curr_node = new_node
        # add the cost of moving to the new node to the path cost            
        self.path_cost += graph.delta(self.path_vec[-1], self.path_vec[0])
        # update the best values the ants have found so far
        self.colony.update(self)
        # update the initial values 
        self.__init__(self.ID, self.start_node, self.colony,self.output)

    def end(self):
        """Return false if there are nodes to visit."""
        return not self.nodes_to_visit

       
    def next_node_rule(self, curr_node):
        """ Return which node to move to.

        curr_node -- the node the ant is currently at.
        """ 
        graph = self.colony.graph
        q = random.random()
        max_node = -1
        # if q < Q0 the next node is chosen based on the amount of
        # pheromone on a trail and the distance between the current
        # node and the next
        if q < self.Q0:
            self.output.write("Exploitation\n")
            max_val = -1
            val = None
            # look at the nodes that have not been visited yet to
            # choose the next to visit
            for node in self.nodes_to_visit.values():
                if graph.tau(curr_node, node) == 0:
                    raise Exception("tau = 0")
                val = graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
                # if the value on the edge is larger than the maximum
                # value found so far update the maximum value, and
                # note which node produced it  
                if val > max_val:
                    max_val = val
                    max_node = node
        else:
            # the next node is chosen so it has a probability that it
            # has a short edge and high pheromone trail  
            self.output.write("Exploration\n")
            sum = 0
            node = -1
            for node in self.nodes_to_visit.values():
                if graph.tau(curr_node, node) == 0:
                    raise Exception("tau = 0")
                sum += graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
            if sum == 0:
                raise Exception("sum = 0")
            avg = sum / len(self.nodes_to_visit)
            self.output.write("avg = %s\n" % (avg,))
            for node in self.nodes_to_visit.values():
                p = graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
                if p > avg:
                    self.output.write("p = %s\n" % (p,))
                    max_node = node
            if max_node == -1:
                max_node = node
        if max_node < 0:
            raise Exception("max_node < 0")
        # take the new node (max_node) out of the nodes to visit matrix
        del self.nodes_to_visit[max_node]
        return max_node

    def local_pheromone_updating_rule(self, curr_node, next_node):
        """Update the pheromones on the tau matrix

        Update the amount of pheromone on the edge between the current node
        and the node the ant is moving to.
        This is intended to avoid a partically strong edge being
        chosen by all the ants
        """
        graph = self.colony.graph
        val = (1 - self.Rho) * graph.tau(curr_node, next_node) + (self.Rho * graph.tau0)
        graph.update_tau(curr_node, next_node, val)


