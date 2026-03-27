import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import GRAPH_OUTPUT

class NetworkGraph:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.G = nx.Graph()
        self.device_ip = '10.0.1.5'
        
        self.G.add_node(self.device_ip, label='CPS Device', type='device', status='normal')
        
        for i in range(1, num_nodes + 1):
            node_id = f"Node{i}"
            self.G.add_node(node_id, label=node_id, type='edge', status='normal')
            self.G.add_edge(self.device_ip, node_id)
            
        self.pos = nx.spring_layout(self.G, seed=42)
        
    def update_graph(self, is_attack, attacker_ip=None, threat_level=0):
        # Update CPS Device node state
        self.G.nodes[self.device_ip]['status'] = 'attack' if is_attack else 'normal'
        
        if is_attack and attacker_ip:
            if attacker_ip not in self.G:
                self.G.add_node(attacker_ip, label='Attacker', type='attacker', status='attack')
                self.pos = nx.spring_layout(self.G, seed=42)  # Refit visual layout
            if not self.G.has_edge(attacker_ip, self.device_ip):
                self.G.add_edge(attacker_ip, self.device_ip, color='red')
        elif not is_attack and attacker_ip and attacker_ip in self.G:
            self.G.remove_node(attacker_ip)
            
        self._plot_graph(threat_level)

    def _plot_graph(self, threat_level):
        plt.figure(figsize=(9, 7))
        
        colors = []
        sizes = []
        edge_colors = []
        
        for node, data in self.G.nodes(data=True):
            if data['type'] == 'device':
                colors.append('orange' if data['status'] == 'attack' else '#2ecc71')
                sizes.append(2000 + (threat_level * 2000 if data['status'] == 'attack' else 0))
            elif data['type'] == 'edge':
                colors.append('#3498db')
                sizes.append(1200)
            elif data['type'] == 'attacker':
                colors.append('#e74c3c')
                sizes.append(1500)

        for u, v in self.G.edges():
            if 'Attacker' in (self.G.nodes[u].get('label'), self.G.nodes[v].get('label')):
                edge_colors.append('red')
            else:
                edge_colors.append('gray')
                
        labels = {node: data['label'] for node, data in self.G.nodes(data=True)}
        
        nx.draw(self.G, self.pos, with_labels=True, labels=labels,
                node_color=colors, node_size=sizes, edge_color=edge_colors,
                font_size=10, font_weight='bold')
        
        plt.title(f"SWED-A Network State (Threat Level: {threat_level:.2f})", pad=20)
        plt.savefig(GRAPH_OUTPUT, bbox_inches='tight')
        plt.close()
