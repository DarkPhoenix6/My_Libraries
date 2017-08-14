import collections


class Graph(object):

    def __init__(self, graph_dict=None, links=None, nodes=None):
        """ initializes a graph object
            If no dictionary or None is given, an empty dictionary will be used
        """
        if links is None:
            self.links = [None]
        else:
            self.links = list(links)
        if nodes is None:
            self.nodes = [nodes]
        elif type(nodes) == type(list):
            self.nodes = list(nodes)
        else:
            self.nodes = [i for i in range(nodes)]
        if graph_dict is None:
            graph_dict = {}
            self.__graph_dict = graph_dict
            self.create_graph_from_links()
        else:
            self.__graph_dict = graph_dict

    def create_graph_from_links(self):
        if self.nodes[0] is not None:
            for i in self.nodes:
                self.add_node(i)
        if self.links[0] is not None:
            for i in self.links:
                self.add_link(i)

    def add_node(self, node):
        self.add_vertex(node)

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_link(self, link):
        self.add_edge(link)

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list;
            between two vertices can be multiple edges!
        """
        edge = set(edge)
        vertex1 = edge.pop()
        if edge:
            # not a loop
            vertex2 = edge.pop()
        else:
            # a loop
            vertex2 = vertex1
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]
        if vertex2 in self.__graph_dict:
            self.__graph_dict[vertex2].append(vertex1)
        else:
            self.__graph_dict[vertex2] = [vertex1]

    def remove_edge(self, edge: list):
        if self.__graph_dict.get(edge[0], None).count(edge[1]) != 0:
            self.__graph_dict[edge[0]].remove(edge[1])
        if self.__graph_dict.get(edge[1], None).count(edge[0]) != 0:
            self.__graph_dict[edge[1]].remove(edge[0])

    def breadth_first_search(self, root):
        visited, queue = set(), collections.deque([root])
        while queue:
            print(queue)
            vertex = queue.popleft()
            for neighbour in self.__graph_dict[vertex]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return visited
