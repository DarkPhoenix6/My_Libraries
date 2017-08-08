class Graph(object):

    def __init__(self, graph_dict=None, links=None, nodes=None):
        """ initializes a graph object
            If no dictionary or None is given, an empty dictionary will be used
        """
        if graph_dict == None:
            graph_dict = {}
            self.__graph_dict = graph_dict
            self.nodes = list(nodes)
            self.links = list(links)
            self.create_graph_from_links()
        else:
            self.__graph_dict = graph_dict
            self.nodes = nodes
            self.links = links

    def create_graph_from_links(self):
        for i in self.nodes:
            self.add_node(i)
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
