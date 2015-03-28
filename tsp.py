import math
import random

class Ant():
    def __init__(self, ID, start_node, colony):
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
        """ Carry out the next stage of a tour.

        Dcides and store the next node the ant will move 
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
        self.__init__(self.ID, self.start_node, self.colony)

    def end(self):
        """ return false if there are nodes to visit"""
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
            print "Exploitation"
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
            print "Exploration"
            sum = 0
            node = -1
            for node in self.nodes_to_visit.values():
                if graph.tau(curr_node, node) == 0:
                    raise Exception("tau = 0")
                sum += graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
            if sum == 0:
                raise Exception("sum = 0")
            avg = sum / len(self.nodes_to_visit)
            print "avg = %s" % (avg,)
            for node in self.nodes_to_visit.values():
                p = graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
                if p > avg:
                    print "p = %s" % (p,)
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


import random
import sys



class AntColony:
    def __init__(self, graph, num_ants, num_iterations):
        """ Set up the ant colony

        graph -- the graph with the nodes and edges the ants will
            traverse
        num_ants -- number of ants in the colony
        num_iterations -- number of iterations the optimizer should
            run for
        """
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.Alpha = 0.1
        #reset the best values gained 
        self.reset()

    def reset(self):
        """Reset the optimizer."""
        self.best_path_cost = sys.maxint
        self.best_path_vec = None
        self.best_path_mat = None
        self.last_best_path_iteration = 0

    def start(self):
        """Start the optimizer."""
        self.ants = self.create_ants()
        self.iter_counter = 0
        # If it is not the last iteration, do an iteration
        # and update the pheromone trails according to the
        # best path.
        while self.iter_counter < self.num_iterations:
            self.iteration()
            self.global_pheromone_updating_rule()

    def iteration(self):
        """Carry out an iteration where all ants complete a tour"""
        self.avg_path_cost = 0
        self.ant_counter = 0
        self.iter_counter += 1
        for ant in self.ants:
            ant.tour()

    def num_ants(self):
        """Return the number of ants."""
        return len(self.ants)

    def num_iterations(self):
        """Return the number of iterations."""
        return self.num_iterations

    def iteration_counter(self):
        """Return the iteration."""
        return self.iter_counter

    def update(self, ant):
        """Update the best path information"""
        print "Update called by %s" % (ant.ID,)
        self.ant_counter += 1
        self.avg_path_cost += ant.path_cost
        if ant.path_cost < self.best_path_cost:
            self.best_path_cost = ant.path_cost
            self.best_path_mat = ant.path_mat
            self.best_path_vec = ant.path_vec
            self.last_best_path_iteration = self.iter_counter
        if self.ant_counter == len(self.ants):
            #if it is the final ant, calculate the average path cost
            # and print the updated information to screen.
            self.avg_path_cost /= len(self.ants)
            print "Best: %s, %s, %s, %s" % (self.best_path_vec, self.best_path_cost,
                self.iter_counter, self.avg_path_cost,)


    def done(self):
        """Return true if the required number of iterations are complete."""
        return self.iter_counter == self.num_iterations

    def create_ants(self):
        """Return a vector of ants and resets the best path

        Each ant is randomly given a start node
        """
        self.reset()
        ants = []
        for i in range(0, self.num_ants):
            ant = Ant(i, random.randint(0, self.graph.num_nodes - 1), self)
            ants.append(ant)

        return ants
 
    def global_pheromone_updating_rule(self):
        """Update the pheromones on the shortest path."""
        deposition = 0
        for r in range(0, self.graph.num_nodes):
            for s in range(0, self.graph.num_nodes):
                if r != s:
                    # Find the inverse of the cost of the best path for
                    # each edge. It is only non-zero for edges on the
                    # best path.
                    delt_tau = self.best_path_mat[r][s] / self.best_path_cost
                    evaporation = (1 - self.Alpha) * self.graph.tau(r, s)
                    #Strengthen the pheromones on the edges on the best path.
                    deposition = self.Alpha * delt_tau
                    self.graph.update_tau(r, s, evaporation + deposition)

class GraphBit:
    def __init__(self, num_nodes, delta_mat, tau_mat=None):
        print len(delta_mat)
        if len(delta_mat) != num_nodes:
            raise Exception("len(delta) != num_nodes")
        self.num_nodes = num_nodes
        self.delta_mat = delta_mat 
        if tau_mat is None:
            self.tau_mat = []
            for i in range(0, num_nodes):
                self.tau_mat.append([0] * num_nodes)

    def delta(self, r, s):
        return self.delta_mat[r][s]

    def tau(self, r, s):
        return self.tau_mat[r][s]

    def etha(self, r, s):
        return 1.0 / self.delta(r, s)

    def update_tau(self, r, s, val):
        self.tau_mat[r][s] = val

    def reset_tau(self):
        avg = self.average_delta()
        self.tau0 = 1.0 / (self.num_nodes * 0.5 * avg)
        print "Average = %s" % (avg,)
        print "Tau0 = %s" % (self.tau0)
        for r in range(0, self.num_nodes):
            for s in range(0, self.num_nodes):
                self.tau_mat[r][s] = self.tau0


    def average_delta(self):
        return self.average(self.delta_mat)


    def average_tau(self):
        return self.average(self.tau_mat)

    def average(self, matrix):
        sum = 0
        for r in range(0, self.num_nodes):
            for s in range(0, self.num_nodes):
                sum += matrix[r][s]

        avg = sum / (self.num_nodes * self.num_nodes)
        return avg

import pickle
import sys
import traceback


def main(argv):
    nm = 10

    if len(argv) >= 3 and argv[0]:
        nm = int(argv[0])

    if nm <= 10:
        na = 20
        ni = 12
        nr = 1
    else:
        na = 28
        ni = 20
        nr = 1

    stuff = pickle.load(open(argv[1], "r"))
    cities = stuff[0]
    cm = stuff[1]
    #why are we doing this?
    if nm < len(cm):
        cm = cm[0:nm]
        for i in range(0, nm):
            cm[i] = cm[i][0:nm]



    try:
        graph = GraphBit(nm, cm)
        best_path_vec = None
        best_path_cost = sys.maxint
        
        for i in range(0, nr):
            print "Repetition %s" % i
            graph.reset_tau()
            workers = AntColony(graph, na, ni)
            print "Colony Started"
            workers.start()
            if workers.best_path_cost < best_path_cost:
                print "Colony Path"
                best_path_vec = workers.best_path_vec
                best_path_cost = workers.best_path_cost

        print "\n------------------------------------------------------------"
        print "                     Results                                "
        print "------------------------------------------------------------"        
        print "\nBest path = %s" % (best_path_vec,)
        city_vec = []
        for node in best_path_vec:
            print cities[node] + " ",
            city_vec.append(cities[node])
        print "\nBest path cost = %s\n" % (best_path_cost,)
        results = [best_path_vec, city_vec, best_path_cost]
        pickle.dump(results, open(argv[2], 'w+'))
    except Exception, e:
        print "exception: " + str(e)
        traceback.print_exc()


if __name__ == "__main__":
    main(sys.argv[1:])

    
