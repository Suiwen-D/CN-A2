import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


def main():
    # Read metadata
    metadata_file = r"D:\CNA2\A3_primary_school_network\A3_primary_school_network\metadata_primary_school.txt"
    metadata = pd.read_csv(metadata_file, sep="\s+", header=0)
    metadata.set_index("node", inplace=True)

    # Read networks: unweighted network & weighted network
    net_u_file = r"D:\CNA2\A3_primary_school_network\A3_primary_school_network\primaryschool_u.net"
    net_w_file = r"D:\CNA2\A3_primary_school_network\A3_primary_school_network\primaryschool_w.net"
    G_u = nx.read_pajek(net_u_file)
    G_w = nx.read_pajek(net_w_file)

    # If an undirected simple graph is needed, force conversion
    G_u = nx.Graph(G_u)
    G_w = nx.Graph(G_w)

    # Perform community detection on unweighted and weighted networks respectively
    if hasattr(nx.algorithms.community, "louvain_communities"):
        from networkx.algorithms.community import louvain_communities
        communities_u = louvain_communities(G_u, weight=None, resolution=1)
        communities_w = louvain_communities(G_w, weight='weight', resolution=1)
    else:
        raise ImportError("The current version of NetworkX does not support louvain_communities. ")

    #Calculate and compare their modularity
    from networkx.algorithms.community import quality
    # Calculate the modularity of the unweighted network
    mod_u = quality.modularity(G_u, communities_u)
    # Calculate the modularity of the weighted network
    mod_w = quality.modularity(G_w, communities_w)
    print("Modularity of community detection in unweighted network: ", mod_u)
    print("Modularity of community detection in weighted network: ", mod_w)

    # Analyze the distribution of school groups within each community
    def analyze_communities(G, communities, metadata):
        
    
        # metadata:    DataFrame containing information such as school_group and immigrant for each node
        
        results = []
        for c_idx, community in enumerate(communities):
            # community is a set containing all nodes in the community (string or integer type)
            community_list = list(community)
            try:
                community_list = [int(n) for n in community_list]
            except:
                pass
            sub_df = metadata.loc[community_list]
            # Count the distribution of school_group
            group_counts = sub_df['school_group'].value_counts().to_dict()
            if 'immigrant' in sub_df.columns:
                immigrant_counts = sub_df['immigrant'].value_counts().to_dict()
            else:
                immigrant_counts = {}
            results.append({
                'community_id': c_idx,
                'size': len(community),
                'group_distribution': group_counts,
                'immigrant_distribution': immigrant_counts
            })
        return results

    results_u = analyze_communities(G_u, communities_u, metadata)
    results_w = analyze_communities(G_w, communities_w, metadata)

    print("\n===== Analysis of community distribution in unweighted network =====")
    for r in results_u:
        print(f"Community {r['community_id']}: Size = {r['size']}")
        print("  School group distribution:", r['group_distribution'])
        if r['immigrant_distribution']:
            print("  Immigrant background distribution:", r['immigrant_distribution'])

    print("\n===== Analysis of community distribution in weighted network =====")
    for r in results_w:
        print(f"Community {r['community_id']}: Size = {r['size']}")
        print("  School group distribution:", r['group_distribution'])
        if r['immigrant_distribution']:
            print("  Immigrant background distribution:", r['immigrant_distribution'])

    # Visualization
    def draw_communities(G, communities, metadata, title="Graph Communities"):
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G, seed=42)  # Other layouts can be used
        # Assign colors
        color_map = {}
        for c_idx, c_set in enumerate(communities):
            color = plt.cm.Set3(c_idx % 12)
            for node in c_set:
                color_map[node] = color

        # Separate nodes into teachers and students according to metadata
        teacher_nodes = []
        student_nodes = []
        for node in G.nodes():
            try:
                node_id = int(node)
            except:
                node_id = node
            if node_id in metadata.index:
                group = metadata.loc[node_id, "school_group"]
                if group == "Teachers":
                    teacher_nodes.append(node)
                else:
                    student_nodes.append(node)
            else:
                student_nodes.append(node)

        # Student nodes: colors of their respective communities, circular shape
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=student_nodes,
            node_size=50,
            node_color=[color_map[n] for n in student_nodes],
            node_shape='o',
            label="Students"
        )
        # Teacher nodes: red color, square shape
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=teacher_nodes,
            node_size=100,
            node_color='red',
            node_shape='s',
            label="Teachers"
        )
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        plt.title(title)
        plt.legend()
        plt.axis('off')
        plt.show()

    # Visualize communities in the unweighted network
    draw_communities(G_u, communities_u, metadata, title="Communities in Unweighted Network")
    # Visualize communities in the weighted network
    draw_communities(G_w, communities_w, metadata, title="Communities in Weighted Network")

    # Add statistical chart (stacked bar chart to show the distribution of the number of people in different school groups in each community)
    def plot_stacked_bar(results, network_type):
        all_groups = set()
        for r in results:
            all_groups.update(r['group_distribution'].keys())

        community_ids = [r['community_id'] for r in results]
        data = []
        for r in results:
            group_counts = r['group_distribution']
            row = [group_counts.get(group, 0) for group in all_groups]
            data.append(row)

        df = pd.DataFrame(data, columns=list(all_groups), index=community_ids)
        df.plot(kind='bar', stacked=True, figsize=(10, 6))
        plt.title(f"School Group Distribution in {network_type} Communities")
        plt.xlabel("Community ID")
        plt.ylabel("Number of Individuals")
        plt.legend(title="School Group")
        plt.show()

    plot_stacked_bar(results_u, "Unweighted Network")
    plot_stacked_bar(results_w, "Weighted Network")


if __name__ == "__main__":
    main()