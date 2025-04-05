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
        print ("1st commit")

    def is_safe_state(self):
        work = self.available.copy()
        finish = [False] * len(self.processes)
        safe_sequence = []
        steps_info = "\n🔍 **Safe State Calculation Steps:**\n\n"

        while len(safe_sequence) < len(self.processes):
            allocated = False
            for i in range(len(self.processes)):
                if not finish[i] and np.all(self.need[i] <= work):
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

        # Add Nodes with Labels
        for i in self.processes:
            G.add_node(f"P{i}", color='#4D9DE0')  # Process Node (Blue)
        for j in self.resources:
            G.add_node(f"R{j}", color='#E15554')  # Resource Node (Red)

        edge_colors = {}
        labels = {}

        # Add Edges (Process -> Resource Allocation & Resource -> Process Request)
        for i, p in enumerate(self.processes):
            for j, r in enumerate(self.resources):
                if self.allocation[i][j] > 0:
                    G.add_edge(f"P{p}", f"R{r}", color='green', width=2.5)
                    labels[(f"P{p}", f"R{r}")] = "Allocated"
                if self.need[i][j] > 0:
                    G.add_edge(f"R{r}", f"P{p}", color='red', width=2.5)
                    labels[(f"R{r}", f"P{p}")] = "Request"

        # Graph Layout (Circular for better readability)
        pos = nx.circular_layout(G)
        node_colors = [G.nodes[n]['color'] for n in G.nodes]

        # Set Figure Size & Background
        plt.figure(figsize=(9, 7), facecolor="#F7F7F7")

        # Draw Graph with Improved Styles
        edges = G.edges(data=True)
        edge_colors = [d['color'] for _, _, d in edges]
        edge_widths = [d['width'] for _, _, d in edges]

        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2800,
                font_size=14, font_weight="bold", edgecolors="black", linewidths=1.8)

        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color=edge_colors, width=edge_widths)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='black', font_size=11)

        # Add an Enhanced Legend
        legend_p = mpatches.Patch(color='#4D9DE0', label="Process (P)")
        legend_r = mpatches.Patch(color='#E15554', label="Resource (R)")
        legend_alloc = mpatches.Patch(color='green', label="Allocated")
        legend_request = mpatches.Patch(color='red', label="Request")
        
        plt.legend(handles=[legend_p, legend_r, legend_alloc, legend_request], loc="upper right", fontsize=11)
        
        plt.title("🔍 Deadlock Detection Graph", fontsize=16, fontweight="bold", color="#333")
        plt.show()

# GUI Implementation
class DeadlockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Deadlock Detection System")
        self.root.geometry("700x600")
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
        matrix = [list(map(int, row.strip().split())) for row in matrix_str.strip().split(",")]
        if len(matrix) != rows or any(len(row) != cols for row in matrix):
            raise ValueError("Matrix dimensions do not match input count.")
        return matrix

# Run GUI
root = tk.Tk()
app = DeadlockGUI(root)
root.mainloop()
