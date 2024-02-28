import tkinter as tk
import matplotlib.pyplot as plt
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


x_plot = []
y_plot = []


def draw_grid(canvas):
    # Draw horizontal lines
    for i in range(10):
        width = 2 if i % 3 == 0 else 1
        canvas.create_line(50, 50 + i * 50, 500, 50 + i * 50, width=width)

    # Draw vertical lines
    for i in range(10):
        width = 2 if i % 3 == 0 else 1
        canvas.create_line(50 + i * 50, 50, 50 + i * 50, 500, width=width)



def draw_numbers(canvas, puzzle, fixed_sudoku):
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] != 0:
                if fixed_sudoku[i][j] == 1:
                    canvas.create_text(75 + j * 50, 75 + i * 50, text=str(puzzle[i][j]), font=("Arial", 18, "bold"), fill="red")
                else:
                    canvas.create_text(75 + j * 50, 75 + i * 50, text=str(puzzle[i][j]), font=("Arial", 16))
            else:
                canvas.create_text(75 + j * 50, 75 + i * 50, text=str(0), font=("Arial", 16))



def draw_score(canvas, score):
    canvas.delete("all")
    canvas.create_text(100, 30, text="Error Score: " + str(score), font=("Arial", 16))



def draw_time(canvas, start_time, end_time):
    canvas.delete("all")
    multiline_text = f"Start Time: {start_time[0]}\nEnd Time: {end_time[0]}"
    canvas.create_text(200, 50, text=multiline_text, font=("Arial", 12))



def draw_value_bar(canvas, value):
    canvas.delete("all")
    canvas_width = 40
    canvas_height = 550
    bar_height = value * canvas_height / 5.0
    canvas.create_rectangle(0, canvas_height - bar_height, canvas_width, canvas_height, fill="blue")
    canvas.create_text(canvas_width + 15, 10, text="5.00", anchor="nw", font=("Arial", 10, "bold"))
    canvas.create_text(canvas_width + 15, 540, text=f"0.00", anchor="nw", font=("Arial", 10, "bold"))
    canvas.create_text(canvas_width - 35, 565, text="Tempr", anchor="nw", font=("Arial", 12, "bold"))
    canvas.create_text(canvas_width + 15, 250, text=f"{value:.2f}", anchor="nw", font=("Arial", 15, "bold"))



def new_puzzle(root, canvas_box, canvas_score, canvas_time, canvas_temp, canvas_graph, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time, canvas_plot, fig):
    canvas_box.delete("all")
    puzzle = tmp_sudoku[0]
    draw_numbers(canvas_box, puzzle, fixed_sudoku[0])
    draw_grid(canvas_box)
    
    score = current_score[0]
    draw_score(canvas_score, score)

    sigma_v = sigma[0]
    draw_value_bar(canvas_temp, sigma_v)

    global x_plot
    global y_plot
    y_plot.append(score)
    if len(x_plot) == 0:
        x_plot.append(1)
    else:
        x_plot.append(x_plot[-1]+1)
    plot_graph(canvas_plot, fig, x_plot, y_plot)

    if solution_found[0] and score == 0:
        draw_time(canvas_time, start_time, end_time)

    if not (solution_found[0] and score == 0):
        root.after(1, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp, canvas_graph, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time, canvas_plot, fig)



def initialize_graph(canvas_graph):
    fig, _ = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=canvas_graph)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return canvas, fig



def plot_graph(canvas, fig, x_values, y_values):
    ax = fig.gca()
    ax.clear()
    ax.plot(x_values, y_values)
    ax.set_xlabel('Progress Iterations')
    ax.set_ylabel('Error Score')
    ax.set_title('Annealing Process')
    ax.grid(True)
    canvas.draw()



def start_ui(tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time):
    root = tk.Tk()
    root.title("Sudoku Solver - Simulated Annealing")
    root.geometry("1280x720")

    canvas_box = tk.Canvas(root, width=500, height=500)
    canvas_box.pack()
    canvas_box.place(x=750, y=0)

    canvas_score = tk.Canvas(root, width=200, height=60, bg="lightgray")
    canvas_score.pack()
    canvas_score.place(x=950, y=520)

    canvas_time = tk.Canvas(root, width=400, height=100, bg="lightblue")
    canvas_time.pack()
    canvas_time.place(x=850, y=600)

    canvas_temp = tk.Canvas(root, width=100, height=600, bg="lightgreen")
    canvas_temp.pack()
    canvas_temp.place(x=0, y=50)

    canvas_graph = tk.Canvas(root, width=50, height=50)
    canvas_graph.pack()
    canvas_graph.place(x=150, y=50)

    canvas_plot, fig = initialize_graph(canvas_graph)

    root.after(1, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp, canvas_graph, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time, canvas_plot, fig)

    def close_window(root):
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", lambda: close_window(root))

    root.mainloop()
