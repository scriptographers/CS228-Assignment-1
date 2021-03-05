from z3 import *


class disconnect:
    def __init(self):
        return

    def printAllPathsUtil(self, u, d, visited, path, beta):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append(u)

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            beta.append(path.copy())
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if visited[i] == False:
                    self.printAllPathsUtil(i, d, visited, path, beta)

        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u] = False

    # Prints all paths from 's' to 'd'

    def printAllPaths(self, s, d):

        # Mark all the vertices as not visited
        visited = [False for i in range(self.vertices[-1] + 1)]

        # Create an array to store paths
        path = []
        beta = []

        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path, beta)
        return beta

    def find_minimal(self, graph, s, t):
        self.graph = graph
        v = set()
        for i in range(len(graph)):
            v.add(graph[i][0])
            v.add(graph[i][1])
        self.vertices = sorted(v)
        all_paths = self.printAllPaths(s, t)
        all_edges = []
        for i in range(len(all_paths)):
            p = []
            for j in range(len(all_paths[i]) - 1):
                a1 = min(all_paths[i][j], all_paths[i][j + 1])
                a2 = max(all_paths[i][j], all_paths[i][j + 1])
                v = Bool("e_{}_{}".format(a1, a2))
                p.append(v)
            all_edges.append(Or(p))
        x = And(all_edges)
        s = Solver()
        s.add(x)
        r = s.check()
        if r == sat:
            m = s.model()
            q = 0
            for i in range(len(m)):
                if is_true(m[m.__getitem__(i)]):
                    q += 1
            return q
        else:
            raise Exception("Unsat")


graph = [(2, 5), (2, 3), (3, 4), (4, 5), (3, 5), (5, 6), (3, 6)]
s = 2
t = 6

x = disconnect()

num = x.find_minimal(graph, s, t)

print("Edges to delete:")
print(num)
