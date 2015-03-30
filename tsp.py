from ant import Ant
from antcolony import AntColony
from graph import Graph


import pickle
import sys
import traceback
import argparse


def main(argv):
    global output
    # Allow the user to optionally specify Beta, Rho and Q0.
    parser = argparse.ArgumentParser(description='Process some optimization parameters.')
    parser.add_argument("number_of_nodes", type=int)
    parser.add_argument("input_file")
    parser.add_argument("--Beta", type=float, default=1.0)
    parser.add_argument("--Q0", type=float, default=0.5)
    parser.add_argument("--Rho", type=float, default=0.99)
    parser.add_argument("--Repetitions", type=int, default=1)
    parser.add_argument("output_file")
    args = parser.parse_args()
    Beta = args.Beta
    Q0 = args.Q0
    Rho = args.Rho
    number_nodes = args.number_of_nodes

    if number_nodes <= 10:
        number_ants = 20
        number_iterations = 12
        number_repetitions = args.Repetitions
    else:
        number_ants = 28
        number_iterations = 20
        number_repetitions = args.Repetitions

    output = open("tspoutput.txt", "w")
    stuff = pickle.load(open(args.input_file, "r"))
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
        graph = Graph(number_nodes, edge_cost_mat, output)
        best_path_vec = None
        best_path_cost = sys.maxint
        
        for i in range(0, number_repetitions):
            output.write("Repetition %s\n" % i)
            print "Repetition %s" % i
            # reset the amount of pheromone trail on edges
            # at the start of each iteration.
            graph.reset_tau()
            # Create the colony of ant workers.
            workers = AntColony(graph, number_ants, number_iterations,output, Beta, Q0, Rho)
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
        pickle.dump(results, open(args.output_file, 'w+'))
    except Exception, e:
        print "exception: " + str(e)
        traceback.print_exc()
        output.close()


if __name__ == "__main__":
    main(sys.argv[1:])

    
