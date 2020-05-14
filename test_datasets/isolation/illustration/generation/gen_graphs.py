from random import choice
class GraphGenerator:

    @staticmethod
    def gen_tree(n_nodes):
        all_nodes = [0]
        edges = []
        for i in range(1, n_nodes):
            edges.append( (choice(all_nodes), i) )
            all_nodes.append(i)
        return sorted(edges)

    """ You don't really want to be using it because it could spit out anything """
    @staticmethod
    def gen_graph(n_nodes, n_edges):
        assert(n_edges >= n_nodes)
        all_nodes = [ i for i in range(n_nodes)]
        # first we form a tree
        edges = gen_tree(n_nodes)
        n_edges -= n_nodes - 1
        
        for i in range(1, n_nodes):
            edges.append( (choice(all_nodes), choice(all_nodes)) )
        return edges


    @staticmethod
    def gen_dag(n_nodes, n_edges):
        from random import sample
        non_ancestors = { 0 : set(i for i in range(1, n_nodes)) }
        # first construct a tree
        edges = set()

        all_nodes = [0]
        for i in range(1, n_nodes):
            p = choice(all_nodes)
            edges.add( (p , i) )
            non_ancestors[i] = non_ancestors[p] - set([i])
            all_nodes.append(i)

        remaining_n_edges = n_edges - (n_nodes - 1)
        safety = n_edges*2
        while remaining_n_edges > 0 and safety > 0:
            safety-=1 
            i = choice(all_nodes)
            if len(non_ancestors[i]) > 0:
                jj = sample(non_ancestors[i], 1)
                j = jj[0] if len(jj) > 0 else -1
                if j>0 and (i,j) not in edges:
                    remaining_n_edges -= 1
                    non_ancestors[j] = non_ancestors[j].intersection(non_ancestors[i])
                    edges.add((i,j))

        if safety == 0:
            raise Exception("Yeah sorry, Couldn't construct. You can try again if you think I was unlucky.")
        return sorted(list(edges))

    @staticmethod
    def gen_single_cycled(n_nodes, n_edges):
        edges = GraphGenerator.gen_dag(n_nodes, n_edges-1)
        # Add the cyclic edge
        edge_dict = { u : [v[1] for v in edges if v[0]==u] for u in range(n_nodes) }
        at = 0
        path = [0]
        while len(edge_dict[at])>0:
            at = choice(edge_dict[at])
            path.append(at)
        from random import sample
        pq = sorted(sample(range(len(path)), 2))

        edges.append( (path[pq[1]], path[pq[0]]) )
        return edges

    @staticmethod
    def gen_chain(n_nodes):
        from random import shuffle
        nodes = [i for i in range(n_nodes)]
        shuffle(nodes)
        return [ (nodes[i-1],nodes[i]) for i in range(1,n_nodes) ]



def test():
    print("\n\nChain:\n", GraphGenerator.gen_chain(6))
    print("\n\nTree:\n", GraphGenerator.gen_tree(6))
    print("\n\nDag:\n", GraphGenerator.gen_dag(6, 8))
    print("\n\nCyclic:\n", GraphGenerator.gen_single_cycled(6, 8))

def main():
    from sys import argv, stdout, stderr

    if len(argv) < 3:
        print("Usage: python3 %s <graph_type> <n_graphs> <n_nodes> [<n_edges>]"%argv[0], file=stderr)
        print("\t- graph_type \{chain, tree, dag, looped\}", file=stderr)
        return
    graph_type = argv[1]
    n_graphs = int(argv[2])
    n_nodes = int(argv[3])

    if graph_type == 'chain':
        graphs = [ GraphGenerator.gen_chain(n_nodes)  for _ in range(n_graphs)]
    elif graph_type == 'tree':
        graphs = [ GraphGenerator.gen_tree(n_nodes)  for _ in range(n_graphs)]
    elif graph_type == 'dag':
        if len(argv) < 5 : print("Expected 4th argument for n_edges", file=stderr); quit()
        n_edges = int(argv[4])
        graphs = [ GraphGenerator.gen_dag(n_nodes, n_edges)  for _ in range(n_graphs)]
    elif graph_type == 'looped':
        if len(argv) < 5 : print("Expected 4th argument for n_edges", file=stderr); quit()
        n_edges = int(argv[4])
        graphs = [ GraphGenerator.gen_single_cycled(n_nodes, n_edges) for _ in range(n_graphs)]
    else:
        print("Unrecognized graph type %s"%graph_type, file=stderr)

    
    outf = stdout
    for i, g in enumerate(graphs):
        gkey = '%c_%d'%(graph_type[0], i)
        print("graph(%s, %s)."%(gkey, 'dummyclass'), file=outf)
        for e in g:
            print("edge(%s, %d, %d)."%(gkey, e[0], e[1]))
        print()

if __name__=='__main__': main()