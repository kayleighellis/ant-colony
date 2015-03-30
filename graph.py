class Graph:
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
        self.output.write("Average = %s\n" % (avg,))
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
