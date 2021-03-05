from z3 import *

class disconnect_try:
    def __init__(self, graph):
        v={1}
        v.remove(1)
        for i in range(len(graph)):
            v.add(graph[i][0])
            v.add(graph[i][1])
        self.vertices=sorted(v)

        #adjacency list
        self.graph=[set({}) for i in range((self.vertices[-1])+1)]
        for i in range(len(graph)):
            self.graph[graph[i][0]].add(graph[i][1])
            self.graph[graph[i][1]].add(graph[i][0])

    def print_vertices(self):
        print(self.vertices)
        print(self.graph)

    def printAllPathsUtil(self, u, d, visited, path, beta): 
  
        # Mark the current node as visited and store in path 
        visited[u]= True
        path.append(u) 
  
        # If current vertex is same as destination, then print 
        # current path[] 
        if u == d: 
            beta.append(path.copy())
        else: 
            # If current vertex is not destination 
            # Recur for all the vertices adjacent to this vertex 
            for i in self.graph[u]: 
                if visited[i]== False: 
                    self.printAllPathsUtil(i, d, visited, path, beta) 
                      
        # Remove current vertex from path[] and mark it as unvisited 
        path.pop() 
        visited[u]= False
   
   
    # Prints all paths from 's' to 'd' 
    def printAllPaths(self, s, d): 
  
        # Mark all the vertices as not visited 
        visited =[False for i in range(self.vertices[-1]+1)]
  
        # Create an array to store paths 
        path = [] 
        beta = []
  
        # Call the recursive helper function to print all paths 
        self.printAllPathsUtil(s, d, visited, path, beta) 
        return beta

def find_minimal(graph, s, t):
    q=disconnect_try(graph)
    all_paths=q.printAllPaths(s,t)
    all_edges=[]
    for i in range(len(all_paths)):
        p=[]
        for j in range(len(all_paths[i])-1):
            a1=min(all_paths[i][j], all_paths[i][j+1])
            a2=max(all_paths[i][j], all_paths[i][j+1])
            v=Bool("e_{}_{}".format(a1, a2))
            p.append(v)
        all_edges.append(Or(p))
    x=And(all_edges)

    s= Solver()

    s . add ( x ) # add formula to the solver
    r = s . check () # check satisfiability
    if r == sat :
        m=s.model()
        ara=0
        for i in range(len(m)):
            if is_true(m[m.__getitem__(i)]):
                ara+=1
        return ara
    else :
        return "unsat"

