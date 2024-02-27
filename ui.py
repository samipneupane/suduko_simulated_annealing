import tkinter as tk



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



def new_puzzle(root, canvas_box, canvas_score, canvas_time, canvas_temp, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time):
    canvas_box.delete("all")
    puzzle = tmp_sudoku[0]
    draw_numbers(canvas_box, puzzle, fixed_sudoku[0])
    draw_grid(canvas_box)
    
    score = current_score[0]
    draw_score(canvas_score, score)

    sigma_v = sigma[0]
    draw_value_bar(canvas_temp, sigma_v)

    if solution_found[0]:
        draw_time(canvas_time, start_time, end_time)

    if not solution_found[0]:
        root.after(10, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time)



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

    root.after(10, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time)
    root.mainloop()
