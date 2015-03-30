from ant import Ant
from antcolony import AntColony

class GraphBit:
    def __init__(self, num_nodes, delta_mat, output, tau_mat=None):
        """Set up the graph

        num_nodes -- number of nodes in the graph
        delta_mat -- matrix showing the length between nodes
        tau_mat -- matrix to hold the pheromone trail between nodes

        """
        self.output = output
        self.output.write("Delta matrix length = %s\n" % (len(delta_mat),))
        if len(delta_mat) != num_nodes:
            raise Exception("len(delta) != num_nodes")
        self.num_nodes = num_nodes
        self.delta_mat = delta_mat 
        if tau_mat is None:
            self.tau_mat = []
            # Start with the amount of pheromone between nodes
            # as zero.
            for i in range(0, num_nodes):
                self.tau_mat.append([0] * num_nodes)

    def delta(self, r, s):
        """Return the length between nodes r and s."""
        return self.delta_mat[r][s]

    def tau(self, r, s):
        """Return the amount of pheromones between nodes r and s."""
        return self.tau_mat[r][s]

    def etha(self, r, s):
        """Return the inverse of the length between nodes r and s."""
        return 1.0 / self.delta(r, s)

    def update_tau(self, r, s, val):
        """Update the amount of pheromone between nodes r and s."""
        self.tau_mat[r][s] = val

    def reset_tau(self):
        """Reset the tau matrix for a new iteration.

        Makes the elements of the tau matrix the reciprocal of
        the number of nodes multiplied by half of the average
        length of the and edge.
        """
        avg = self.average_delta()
        self.tau0 = 1.0 / (self.num_nodes * 0.5 * avg)
        output.write("Average = %s\n" % (avg,))
        self.output.write("Tau0 = %s\n" % (self.tau0))
        for r in range(0, self.num_nodes):
            for s in range(0, self.num_nodes):
                self.tau_mat[r][s] = self.tau0


    def average_delta(self):
        """Return the average edge length between nodes."""
        return self.average(self.delta_mat)


    def average_tau(self):
        """Return the average pheromone trail between nodes."""
        return self.average(self.tau_mat)

    def average(self, matrix):
        """Return the average value of the elements of a matrix."""
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
    global output
    number_nodes = 10

    if len(argv) >= 3 and argv[0]:
        number_nodes = int(argv[0])

    if number_nodes <= 10:
        number_ants = 20
        number_iterations = 12
        number_repetitions = 1
    else:
        number_ants = 28
        number_iterations = 20
        number_repetitions = 1


    output = open("tspoutput.txt", "w")
    stuff = pickle.load(open(argv[1], "r"))
    cities = stuff[0]
    edge_cost_mat = stuff[1]
    # If the user has chose to optimize for less nodes than
    # are supplied in the file, change the size of the edge
    # cost matrix so it only contains the costs for
    #the user's chosen edges
    if number_nodes < len(edge_cost_mat):
        edge_cost_mat = edge_cost_mat[0:number_nodes]
        for i in range(0, number_nodes):
            edge_cost_mat[i] = edge_cost_mat[i][0:number_nodes]



    try:
        #create a graph from the read file 
        graph = GraphBit(number_nodes, edge_cost_mat, output)
        best_path_vec = None
        best_path_cost = sys.maxint
        
        for i in range(0, number_repetitions):
            output.write("Repetition %s\n" % i)
            print "Repetition %s" % i
            # reset the amount of pheromone trail on edges
            # at the start of each iteration.
            graph.reset_tau()
            # Create the colony of ant workers.
            workers = AntColony(graph, number_ants, number_iterations,output)
            output.write("Colony Started\n")
            # Start the optimization on the workers colony.
            workers.start_optimizer()
            # Update the best path if the current path costs less
            if workers.best_path_cost < best_path_cost:
                output.write("Colony Path\n")
                best_path_vec = workers.best_path_vec
                best_path_cost = workers.best_path_cost

        print "\n------------------------------------------------------------"
        print "                     Results                                "
        print "------------------------------------------------------------"        
        print "\nBest path = %s" % (best_path_vec,)
        result_city_vec = []
        for node in best_path_vec:
            print cities[node] + " ",
            result_city_vec.append(cities[node])
        print "\nBest path cost = %s\n" % (best_path_cost,)
        results = [best_path_vec, result_city_vec, best_path_cost]
        pickle.dump(results, open(argv[2], 'w+'))
    except Exception, e:
        print "exception: " + str(e)
        traceback.print_exc()
        output.close()


if __name__ == "__main__":
    main(sys.argv[1:])

    
