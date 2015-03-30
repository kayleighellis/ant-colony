from ant import Ant
from antcolony import AntColony
from graph import Graph


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

    
