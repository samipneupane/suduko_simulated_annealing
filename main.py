import numpy as np
import threading
import copy

from logic import start_algorithm
from ui import start_ui



if __name__ == "__main__":

    startingSudoku = """
                        024007000
                        600000000
                        003680415
                        431005000
                        500000032
                        790000060
                        209710800
                        040093000
                        310004750
                    """
    
    fixed_sudoku = [np.zeros((9, 9))]
    tmp_sudoku = [np.zeros((9, 9))]
    
    current_score = [999]
    sigma = [5.00]
    solution_found = [False]
    start_time = [None]
    end_time = [None]
    
    sudoku = [np.array([[int(i) for i in line] for line in startingSudoku.split()])]
    tmp_sudoku = [copy.deepcopy(sudoku)]
  
    #thread
    solve_sudoku_thread = threading.Thread(target=start_algorithm, args=(sudoku, tmp_sudoku, fixed_sudoku, current_score, sigma, start_time, end_time, solution_found))
    solve_sudoku_thread.start()
    start_ui(tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found, start_time, end_time)
    solve_sudoku_thread.join()