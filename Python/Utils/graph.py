from __future__ import division
import collections
import queue
import threading
import concurrent.futures
import time


class MyThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        # print ("Starting " + self.name)
        # Get lock to synchronize threads
        threadLock.acquire()
        # print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


threadLock = threading.Lock()
threads = []
threadID = 1
queueLock = threading.Lock()
workQueue = queue.Queue()


def mod_gen(n, m, s=0):
    """
    Generator function that yields n tuples of m length containing consecutive indices within bounds n
    Such that the set of tuples generated from mod_gen(3, 3) would be ((2, 0, 1), (0, 1, 2), (1, 2, 0))
    :param n: The number of tuples to generate and the bounds of the indices in the tuple
    :param m: The number of indices per tuple
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(n):
        yield (tuple([(i + k + s) % n for k in range(int(m // 2) - m + 1, int(m // 2 + 1))]))


def memoize(fn):
    """returns a memoized version of any function that can be called
    with the same list of arguments.
    Usage: foo = memoize(foo)"""

    def handle_item(x):
        if isinstance(x, dict):
            return make_tuple(sorted(x.items()))
        elif hasattr(x, '__iter__'):
            return make_tuple(x)
        else:
            return x

    def make_tuple(L):
        return tuple(handle_item(x) for x in L)

    def foo(*args, **kwargs):
        items_cache = make_tuple(sorted(kwargs.items()))
        args_cache = make_tuple(args)
        if (args_cache, items_cache) not in foo.past_calls:
            foo.past_calls[(args_cache, items_cache)] = fn(*args,**kwargs)
        return foo.past_calls[(args_cache, items_cache)]
    foo.past_calls = {}
    foo.__name__ = 'memoized_' + fn.__name__
    return foo


class Graph(object):

    def __init__(self, graph_dict=None, links=None, nodes=None, bidirectional=False):
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
            self.graph_dict = graph_dict
            self.create_graph_from_links(bidirectional)
        else:
            self.graph_dict = graph_dict
        self.path_dict = {}

    def create_graph_from_links(self, bidirectional=False):
        if self.nodes[0] is not None:
            for i in self.nodes:
                self.add_node(i)
        if self.links[0] is not None:
            for i in self.links:
                self.add_link(i, bidirectional)

    def add_node(self, node):
        self.add_vertex(node)

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        if vertex not in self.graph_dict:
            self.graph_dict[vertex] = set()

    def add_link(self, link, bidirectional=False):
        self.add_edge(link, bidirectional)

    def add_edge(self, edge, bidirectional=False):
        """
            :param edge: is of type set, tuple or list, between two vertices can be multiple edges!
            :param bidirectional: is teh edge traversable bidirectionally
        """
        edge = set(edge)
        vertex1 = edge.pop()
        if edge:
            # not a loop
            vertex2 = edge.pop()
        else:
            # a loop
            vertex2 = vertex1
        if vertex1 in self.graph_dict:
            self.graph_dict[vertex1].add(vertex2)
        else:
            self.graph_dict[vertex1] = set()
            self.graph_dict[vertex1].add(vertex2)
        if bidirectional:
            if vertex2 in self.graph_dict:
                self.graph_dict[vertex2].add(vertex1)
            else:
                self.graph_dict[vertex2] = set()
                self.graph_dict[vertex2].add(vertex1)

    def remove_edge(self, edge: list):
        if self.graph_dict.get(edge[0], None).count(edge[1]) != 0:
            self.graph_dict[edge[0]].remove(edge[1])
        if self.graph_dict.get(edge[1], None).count(edge[0]) != 0:
            self.graph_dict[edge[1]].remove(edge[0])

    @memoize
    def breadth_first_search(self, root):
        visited, queue = set(), collections.deque([root])
        while queue:
            print(queue)
            vertex = queue.popleft()
            for neighbour in self.graph_dict[vertex]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return visited

    def has_node(self, node):
        if node in self.graph_dict:
            return True
        else:
            return False

    def has_edge(self, edge: list):
        if self.graph_dict.get(edge[0], None).count(edge[1]) != 0 or \
                        self.graph_dict.get(edge[1], None).count(edge[0]) != 0:
            return True
        else:
            return False

    @memoize
    def bfs_shortest_path(self, start, goal):
        # keep track of explored nodes
        explored = []
        # keep track of all the paths to be checked
        queue = [[start]]
        graph = self.graph_dict
        # return path if start is goal
        if start == goal:
            return [start]

        # keeps looping until all possible paths have been checked
        while queue:
            # pop the first path from the queue
            path = queue.pop(0)
            # get the last node from the path
            node = path[-1]
            if node not in explored:
                neighbours = graph[node]
                # go through all neighbour nodes, construct a new path and
                # push it into the queue
                for neighbour in neighbours:
                    new_path = list(path)
                    new_path.append(neighbour)
                    queue.append(new_path)
                    # return path if neighbour is goal
                    if neighbour == goal:
                        return new_path

                # mark node as explored
                explored.append(node)

                # in case there's no path between the 2 nodes
        return None

    @memoize
    def dfs_paths_itr(self, start, goal):
        graph = self.graph_dict
        stack = [(start, [start])]
        while stack:
            (vertex, path) = stack.pop()
            for next_node in graph[vertex] - set(path):
                if next_node == goal:
                    yield path + [next_node]
                else:
                    stack.append((next_node, path + [next_node]))

    @memoize
    def dfs_itr(self, start):
        graph = self.graph_dict
        visited, stack = set(), [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(graph[vertex] - visited)
        return visited


@memoize
def breadth_first_search(graph, root):
    visited, queue = set(), collections.deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)


@memoize
def bfs_paths(graph, start, goal):
    q = [(start, [start])]
    while q:
        (vertex, path) = q.pop(0)
        for next_node in graph[vertex] - set(path):
            if next_node == goal:
                yield path + [next_node]
            else:
                q.append((next_node, path + [next_node]))


@memoize
def bfs(graph, start):
    visited, queue = set(), [start]
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited:
            visited.add(vertex)
            queue.extend(graph[vertex] - visited)
    return visited


@memoize
def dfs_paths_itr(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        for next_node in graph[vertex] - set(path):
            if next_node == goal:
                yield path + [next_node]
            else:
                stack.append((next_node, path + [next_node]))


@memoize
def dfs_paths(graph, start, goal, path=None):
    if path is None:
        path = [start]
    if start == goal:
        yield path
    for next_node in graph[start] - set(path):
        yield from dfs_paths(graph, next_node, goal, path + [next_node])


@memoize
def dfs_itr(graph, start):
    visited, stack = set(), [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited


@memoize
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for next_node in graph[start] - visited:
        dfs(graph, next_node, visited)
    return visited


@memoize
def shortest_path(graph, start, goal):
    try:
        return next(bfs_paths(graph, start, goal))
    except StopIteration:
        return None


def shortest_paths(graph):
    paths = {}
    a = list(graph.keys())
    for i in range(len(a)):
        paths[a[i]] = []
        k = [j for j in mod_gen(len(a), (len(a) - 1), 2)][i]
        for j in k:
            paths[a[i]].append(shortest_path(graph, a[i], a[j]))
    return paths


def get_depth(paths):
    depth = None
    for i in range(len(paths)):
        if depth is None or (len(paths[i]) - 1) > depth:
            depth = (len(paths[i]) - 1)
    return depth


def min_depth(paths_dict):
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     for i in paths_dict:
    #         node_depth.append(get_depth(paths_dict.get(i)))

    executor = concurrent.futures.ProcessPoolExecutor(22)
    futures = [executor.submit(get_depth, paths_dict.get(item)) for item in paths_dict]
    concurrent.futures.wait(futures)
    node_depth = [futures[i].result() for i in range(len(futures))]
    min_d = min(node_depth)
    return min_d

if __name__ == '__main__':
    g = Graph(links=[[0, 1], [1, 2], [2, 3], [2, 4]], bidirectional=True)
    p = shortest_paths(g.graph_dict)
    steps = min_depth(p)
    print(steps)
