import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.patches as mpatches

class DeadlockDetection:
    def __init__(self, processes, resources, allocation, max_need, available):
        self.processes = processes
        self.resources = resources
        self.allocation = np.array(allocation, dtype=int)
        self.max_need = np.array(max_need, dtype=int)
        self.available = np.array(available, dtype=int)
        self.need = self.max_need - self.allocation

    def is_safe_state(self):
        work = self.available.copy()
        finish = [False] * len(self.processes)
        safe_sequence = []
        steps_info = "\n🔍 **Safe State Calculation Steps:**\n\n"

        while len(safe_sequence) < len(self.processes):
            allocated = False
            for i in range(len(self.processes)):
                if not finish[i] and all(self.need[i] <= work):
                    steps_info += f"✅ Process P{i} can execute (Need ≤ Available)\n"
                    work += self.allocation[i]
                    finish[i] = True
                    safe_sequence.append(f"P{i}")
                    allocated = True
                    break
            if not allocated:
                steps_info += "❌ No process can proceed further, leading to DEADLOCK!\n"
                return False, [], steps_info

        steps_info += "\n✅ **Safe Sequence:** " + " ➡ ".join(safe_sequence)
        return True, safe_sequence, steps_info

    def detect_deadlock(self):
        is_safe, safe_sequence, steps_info = self.is_safe_state()
        return not is_safe, safe_sequence, steps_info

    def visualize_graph(self):
        G = nx.DiGraph()

        # Add Nodes
        for i, p in enumerate(self.processes):
            G.add_node(f"P{p}", color='skyblue', shape='o')  # Process: Circle
        for j, r in enumerate(self.resources):
            G.add_node(f"R{r}", color='lightcoral', shape='s')  # Resource: Square

        # Add Edges
        edge_colors = []
        edge_styles = []
        labels = {}

        for i, p in enumerate(self.processes):
            for j, r in enumerate(self.resources):
                if self.allocation[i][j] > 0:
                    G.add_edge(f"P{p}", f"R{r}")
                    edge_colors.append('green')
                    edge_styles.append('solid')
                    labels[(f"P{p}", f"R{r}")] = "Allocated"
                if self.need[i][j] > 0:
                    G.add_edge(f"R{r}", f"P{p}")
                    edge_colors.append('red')
                    edge_styles.append('dashed')
                    labels[(f"R{r}", f"P{p}")] = "Request"

        # Define Positioning
        pos = nx.spring_layout(G, seed=42)  # Better node spacing
        colors = [G.nodes[n]['color'] for n in G.nodes]

        # Draw Graph with Custom Styling
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color=colors, edge_color=edge_colors,
                node_size=2500, font_size=12, font_weight="bold", edgecolors="black", linewidths=1.5)

        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='black', font_size=10)

        # Draw Different Node Shapes
        node_shapes = {'o': [], 's': []}
        for node, data in G.nodes(data=True):
            node_shapes[data['shape']].append(node)

        for shape, nodes in node_shapes.items():
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_shape=shape, node_color=[G.nodes[n]['color'] for n in nodes])

        # Add Legend
        legend_p = mpatches.Patch(color='skyblue', label="Process (P)")
        legend_r = mpatches.Patch(color='lightcoral', label="Resource (R)")
        plt.legend(handles=[legend_p, legend_r], loc="upper right")

        plt.title("🔍 Deadlock Detection Graph", fontsize=14, fontweight="bold")
        plt.show()

# GUI Implementation
class DeadlockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Deadlock Detection System")
        self.root.geometry("650x550")
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10)
        style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")

        # Header
        ttk.Label(root, text="🔍 Deadlock Detection System", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(root, text="Enter system details below:", font=("Arial", 12)).pack(pady=5)

        # Input Fields
        self.processes_entry = self.create_labeled_entry("Processes (e.g., 0 1 2 3)")
        self.resources_entry = self.create_labeled_entry("Resources (e.g., 0 1)")
        self.allocation_entry = self.create_labeled_entry("Allocation Matrix (comma-separated rows, space-separated values)")
        self.max_need_entry = self.create_labeled_entry("Max Need Matrix (comma-separated rows, space-separated values)")
        self.available_entry = self.create_labeled_entry("Available Resources (space-separated)")

        # Check Deadlock Button
        ttk.Button(root, text="Check Deadlock", command=self.check_deadlock, style="TButton").pack(pady=20)

    def create_labeled_entry(self, label_text):
        frame = ttk.Frame(self.root)
        frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(frame, text=label_text, font=("Arial", 11)).pack(anchor="w")
        entry = ttk.Entry(frame, font=("Arial", 12))
        entry.pack(fill="x", padx=5, pady=3)
        return entry

    def check_deadlock(self):
        try:
            # Get Inputs
            processes = list(map(int, self.processes_entry.get().strip().split()))
            resources = list(map(int, self.resources_entry.get().strip().split()))
            allocation = self.parse_matrix(self.allocation_entry.get(), len(processes), len(resources))
            max_need = self.parse_matrix(self.max_need_entry.get(), len(processes), len(resources))
            available = list(map(int, self.available_entry.get().strip().split()))

            if len(available) != len(resources):
                messagebox.showerror("Input Error", "Available resources count must match resource count.")
                return

            # Run Deadlock Detection
            detector = DeadlockDetection(processes, resources, allocation, max_need, available)
            is_deadlock, safe_sequence, steps_info = detector.detect_deadlock()

            if is_deadlock:
                messagebox.showerror("❌ Deadlock Detected", f"⚠ The system is in a DEADLOCK state!\n\n{steps_info}")
            else:
                messagebox.showinfo("✅ Safe State", f"🎉 The system is in a SAFE state!\n\n{steps_info}")

            detector.visualize_graph()

        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input format! Please check your entries.\nError: {str(e)}")

    def parse_matrix(self, matrix_str, rows, cols):
        try:
            matrix = [list(map(int, row.strip().split())) for row in matrix_str.strip().split(",")]
            if len(matrix) != rows or any(len(row) != cols for row in matrix):
                raise ValueError("Matrix dimensions do not match input count.")
            return matrix
        except:
            raise ValueError("Matrix input is not formatted correctly. Use 'row1, row2, row3' format.")

# Run GUI
root = tk.Tk()
app = DeadlockGUI(root)
root.mainloop()
