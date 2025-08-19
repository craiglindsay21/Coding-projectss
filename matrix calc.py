import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import re

# --- Style Configuration ---
BG_COLOR = "#1c1c1c"
FG_COLOR = "#ffffff"
INPUT_BG_COLOR = "#2b2b2b"
BTN_BG = "#333333"
BTN_HOVER_BG = "#555555"
BTN_TEXT_COLOR = "#000000" # Black for button text
FONT_FAMILY = "Helvetica"

class App(tk.Tk):
    """
    Main application window that hosts the start menu and switches between different frames.
    """
    def __init__(self):
        super().__init__()
        self.title("Matrix Tools")
        
        # Make the window fullscreen/maximized (cross-platform)
        self.state('zoomed')
        self.configure(bg=BG_COLOR)

        # Container frame to hold the different pages
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.active_frame = None # To track the currently visible frame for optimization
        self._create_start_menu()
        self.show_start_menu() # Start by showing the menu

    def _create_start_menu(self):
        """Creates the initial start menu."""
        self.start_menu_frame = tk.Frame(self.container, bg=BG_COLOR)

        menu_content_frame = tk.Frame(self.start_menu_frame, bg=BG_COLOR)
        menu_content_frame.pack(expand=True)

        tk.Label(menu_content_frame, text="Matrix Tools", font=(FONT_FAMILY, 48, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 50))

        # --- Button Styling ---
        self._create_fancy_button(menu_content_frame, "Eigenvalue Calculator", lambda: self.show_frame(EigenCalculator))
        self._create_fancy_button(menu_content_frame, "Matrix Generator", lambda: self.show_frame(MatrixGenerator))

    def _create_fancy_button(self, parent, text, command):
        """Helper to create styled buttons with hover effects."""
        button = tk.Button(parent, text=text,
                           font=(FONT_FAMILY, 18, "bold"),
                           bg=BTN_BG,
                           fg=BTN_TEXT_COLOR,
                           command=command,
                           relief=tk.RAISED,
                           borderwidth=2,
                           width=25,
                           pady=15,
                           activebackground=BTN_HOVER_BG,
                           activeforeground=BTN_TEXT_COLOR)
        button.pack(pady=15)
        
        # Hover effects
        button.bind("<Enter>", lambda e: e.widget.config(bg=BTN_HOVER_BG))
        button.bind("<Leave>", lambda e: e.widget.config(bg=BTN_BG))

    def show_frame(self, FrameClass):
        """Hides the current frame and shows the selected one."""
        if self.active_frame:
            self.active_frame.grid_forget()

        if FrameClass not in self.frames:
            self.frames[FrameClass] = FrameClass(self.container, self)
        
        frame = self.frames[FrameClass]
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
        self.active_frame = frame

    def show_start_menu(self):
        """Hides the current tool frame and shows the start menu."""
        if self.active_frame:
            self.active_frame.grid_forget()
        
        self.start_menu_frame.grid(row=0, column=0, sticky="nsew")
        self.active_frame = self.start_menu_frame


class EigenCalculator(tk.Frame):
    """
    GUI frame for calculating eigenvalues and eigenvectors.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)
        
        self.matrix_entries = []
        self.matrix_size = tk.IntVar(value=2)

        main_frame = tk.Frame(self, padx=20, pady=20, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(main_frame, text="← Back to Menu", command=self.controller.show_start_menu, bg=BTN_BG, fg=BTN_TEXT_COLOR, relief=tk.RAISED, borderwidth=1, activebackground=BTN_HOVER_BG, activeforeground=BTN_TEXT_COLOR, font=(FONT_FAMILY, 10, "bold")).pack(anchor='nw')
        tk.Label(main_frame, text="Eigenvalue Calculator", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(20, 30))

        top_frame = tk.Frame(main_frame, bg=BG_COLOR)
        top_frame.pack(fill=tk.X, pady=10)
        tk.Label(top_frame, text="Matrix Size (N x N):", bg=BG_COLOR, fg=FG_COLOR, font=(FONT_FAMILY, 12)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Spinbox(top_frame, from_=1, to=10, textvariable=self.matrix_size, width=5, command=self.create_matrix_grid).pack(side=tk.LEFT)

        self.matrix_frame = tk.Frame(main_frame, padx=10, pady=10, bg=INPUT_BG_COLOR)
        self.matrix_frame.pack(pady=10)

        calculate_button = tk.Button(main_frame, text="Calculate", command=self.calculate_eigen, bg=BTN_BG, fg=BTN_TEXT_COLOR, font=(FONT_FAMILY, 14, "bold"), relief=tk.RAISED, borderwidth=2, padx=20, pady=10, activebackground=BTN_HOVER_BG, activeforeground=BTN_TEXT_COLOR)
        calculate_button.pack(pady=20)
        calculate_button.bind("<Enter>", lambda e: e.widget.config(bg=BTN_HOVER_BG))
        calculate_button.bind("<Leave>", lambda e: e.widget.config(bg=BTN_BG))

        results_frame = tk.Frame(main_frame, bg=BG_COLOR)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Label(results_frame, text="Results:", font=(FONT_FAMILY, 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w')
        self.results_text = tk.Text(results_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED, bg=INPUT_BG_COLOR, fg=FG_COLOR, font=(FONT_FAMILY, 12))
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.create_matrix_grid()

    def create_matrix_grid(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        self.matrix_entries = []
        size = self.matrix_size.get()
        for i in range(size):
            row_entries = []
            for j in range(size):
                entry = tk.Entry(self.matrix_frame, width=5, justify='center', font=(FONT_FAMILY, 12), 
                                 bg=INPUT_BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
                entry.grid(row=i, column=j, padx=5, pady=5)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    def get_matrix_from_input(self):
        size = self.matrix_size.get()
        matrix_data = []
        try:
            for i in range(size):
                row_data = []
                for j in range(size):
                    value = float(self.matrix_entries[i][j].get())
                    row_data.append(value)
                matrix_data.append(row_data)
            return np.array(matrix_data)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers in all matrix cells.")
            return None

    def calculate_eigen(self):
        matrix = self.get_matrix_from_input()
        if matrix is not None:
            try:
                eigenvalues, eigenvectors = np.linalg.eig(matrix)
                self.display_results(eigenvalues, eigenvectors)
            except np.linalg.LinAlgError:
                messagebox.showerror("Calculation Error", "Could not compute eigenvalues for this matrix.")

    def display_results(self, eigenvalues, eigenvectors):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, "Eigenvalues:\n")
        self.results_text.insert(tk.END, np.array2string(eigenvalues, precision=4) + "\n\n")
        self.results_text.insert(tk.END, "Eigenvectors (as columns):\n")
        self.results_text.insert(tk.END, np.array2string(eigenvectors, precision=4))
        self.results_text.config(state=tk.DISABLED)


class MatrixGenerator(tk.Frame):
    """
    GUI frame for generating a matrix from eigenvalues and eigenvectors.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=BG_COLOR)

        main_frame = tk.Frame(self, padx=20, pady=20, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True)

        tk.Button(main_frame, text="← Back to Menu", command=self.controller.show_start_menu, bg=BTN_BG, fg=BTN_TEXT_COLOR, relief=tk.RAISED, borderwidth=1, activebackground=BTN_HOVER_BG, activeforeground=BTN_TEXT_COLOR, font=(FONT_FAMILY, 10, "bold")).pack(anchor='nw')
        tk.Label(main_frame, text="Matrix Generator", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(20, 30))

        # --- Input Frame ---
        input_frame = tk.Frame(main_frame, bg=BG_COLOR)
        input_frame.pack(pady=10, fill='x')

        tk.Label(input_frame, text="Eigenvalues (comma-separated):", bg=BG_COLOR, fg=FG_COLOR, font=(FONT_FAMILY, 12)).pack(anchor='w')
        self.eigen_entry = tk.Entry(input_frame, width=60, font=(FONT_FAMILY, 12),
                                    bg=INPUT_BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        self.eigen_entry.pack(fill='x', pady=(5, 20), ipady=4) # ipady for internal padding

        tk.Label(input_frame, text="Eigenvectors (enter as columns, separated by spaces/newlines):", bg=BG_COLOR, fg=FG_COLOR, font=(FONT_FAMILY, 12)).pack(anchor='w')
        self.evec_text = tk.Text(input_frame, height=8, width=60, font=(FONT_FAMILY, 12), bg=INPUT_BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, relief=tk.FLAT)
        self.evec_text.pack(fill='x', pady=5)
        self.evec_text.insert('1.0', "Example for a 2x2 matrix:\n1 0.5\n0.5 1")

        # --- Button Frame ---
        generate_button = tk.Button(main_frame, text="Generate Matrix", command=self.generate_matrix, bg=BTN_BG, fg=BTN_TEXT_COLOR, font=(FONT_FAMILY, 14, "bold"), relief=tk.RAISED, borderwidth=2, padx=20, pady=10, activebackground=BTN_HOVER_BG, activeforeground=BTN_TEXT_COLOR)
        generate_button.pack(pady=20)
        generate_button.bind("<Enter>", lambda e: e.widget.config(bg=BTN_HOVER_BG))
        generate_button.bind("<Leave>", lambda e: e.widget.config(bg=BTN_BG))

        # --- Results Frame ---
        results_frame = tk.Frame(main_frame, bg=BG_COLOR)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Label(results_frame, text="Generated Matrix (A = PDP⁻¹):", font=(FONT_FAMILY, 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w')
        self.results_text = tk.Text(results_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED, font=("Courier", 14), bg=INPUT_BG_COLOR, fg=FG_COLOR)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def generate_matrix(self):
        # 1. Parse Eigenvalues
        try:
            input_str = self.eigen_entry.get()
            values = re.findall(r'-?\d+\.?\d*', input_str)
            eigenvalues = [float(v) for v in values]
            if not eigenvalues: raise ValueError("No eigenvalues entered.")
        except (ValueError, TypeError):
            messagebox.showerror("Input Error", "Please enter valid, comma or space-separated numbers for eigenvalues.")
            return

        # 2. Parse Eigenvectors
        try:
            evec_str = self.evec_text.get("1.0", tk.END)
            lines = evec_str.strip().split('\n')
            # Ignore example text
            lines = [line for line in lines if "Example" not in line]
            
            parsed_evecs = []
            for line in lines:
                if line.strip(): # Skip empty lines
                    row = [float(num) for num in line.strip().split()]
                    parsed_evecs.append(row)
            
            if not parsed_evecs: raise ValueError("No eigenvectors entered.")
            
            # The input is row-based, but we need column-based eigenvectors, so transpose.
            eigenvector_matrix_P = np.array(parsed_evecs).T

        except (ValueError, TypeError):
            messagebox.showerror("Input Error", "Eigenvectors must be valid numbers separated by spaces and newlines.")
            return

        # 3. Validate Inputs
        n = len(eigenvalues)
        if eigenvector_matrix_P.shape != (n, n):
            messagebox.showerror("Dimension Mismatch", f"You entered {n} eigenvalues, but the eigenvector matrix is not {n}x{n}. Please check your input.")
            return

        # 4. Perform Calculation: A = P * D * P^-1
        try:
            D = np.diag(eigenvalues)
            P_inv = np.linalg.inv(eigenvector_matrix_P)
            
            # Use @ for matrix multiplication
            generated_matrix = eigenvector_matrix_P @ D @ P_inv
            
            self.display_matrix(generated_matrix)

        except np.linalg.LinAlgError:
            messagebox.showerror("Calculation Error", "The eigenvector matrix is singular and cannot be inverted. Please provide a set of linearly independent eigenvectors.")

    def display_matrix(self, matrix):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        matrix_str = np.array2string(matrix, precision=4, separator='  ', suppress_small=True)
        self.results_text.insert(tk.END, matrix_str)
        self.results_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = App()
    app.mainloop()
