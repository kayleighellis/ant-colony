import random
import sys

from ant import Ant


class AntColony:
    def __init__(self, graph, num_ants, num_iterations,output):
        """ Set up the ant colony

        graph -- the graph with the nodes and edges the ants will
            traverse
        num_ants -- number of ants in the colony
        num_iterations -- number of iterations the optimizer should
            run for
        """
        self.output = output
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.Alpha = 0.1
        #reset the best values gained 
        self.reset()
        #output.write("I CAN WRITE HERE")

    def reset(self):
        """Reset the optimizer."""
        self.best_path_cost = sys.maxint
        self.best_path_vec = None
        self.best_path_mat = None
        self.last_best_path_iteration = 0

    def start_optimizer(self):
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
        self.output.write("Update called by %s\n" % (ant.ID,))
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
            self.output.write("I CAN WRITE HERE")

    
            print "Iteration %s: \nBest path yet: %s,\nPath cost: %s,\nAverage path cost: %s" % ( self.iter_counter, self.best_path_vec, self.best_path_cost, self.avg_path_cost,)


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
            ant = Ant(i, random.randint(0, self.graph.num_nodes - 1), self,self.output)
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
