import random
import numpy as np
import math 
from random import choice
import statistics 
import time
import copy
import threading
import tkinter as tk



tmp_sudoku = np.zeros((9, 9))
fixed_sudoku = np.zeros((9, 9))
current_score = [999]
solution_found = False
end_time = None
start_time = None
sigma = [10.00]



#print the (3*3)*(3*3) suduko
def PrintSudoku(sudoku):
    print("\n")
    for i in range(len(sudoku)):
        line = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                line += "| "
            line += str(sudoku[i,j])+" "
        print(line)


#print Fixed suduko: 0 for fixed value, 1 for not fixed
def FixSudokuValues(fixed_sudoku):
    for i in range (0,9):
        for j in range (0,9):
            if fixed_sudoku[i,j] != 0:
                fixed_sudoku[i,j] = 1
    return(fixed_sudoku)


#make list of 9 different blocks, within block 9 different boxes
def CreateList3x3Blocks ():
    finalListOfBlocks = []
    for r in range (0,9):
        tmpList = []
        block1 = [i + 3*((r)%3) for i in range(0,3)]
        block2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
        for x in block1:
            for y in block2:
                tmpList.append([x,y])
        finalListOfBlocks.append(tmpList)
    return(finalListOfBlocks)


#fill the zeros with unique random (1-9) without repetition in a given block
def RandomlyFill3x3Blocks(sudoku, listOfBlocks):
    for block in listOfBlocks:
        for box in block:
            if sudoku[box[0],box[1]] == 0:
                currentBlock = sudoku[block[0][0]:(block[-1][0]+1),block[0][1]:(block[-1][1]+1)]
                sudoku[box[0],box[1]] = choice([i for i in range(1,10) if i not in currentBlock])
    return sudoku


#total no of errors  
def CalculateNumberOfErrors(sudoku):
    numberOfErrors = 0 
    for i in range (0,9):
        numberOfErrors += CalculateNumberOfErrorsRowColumn(i ,i ,sudoku)
    return(numberOfErrors)


#no of errors for for row and column (i, i)
def CalculateNumberOfErrorsRowColumn(row, column, sudoku):
    numberOfErrors = (9 - len(np.unique(sudoku[:,column]))) + (9 - len(np.unique(sudoku[row,:])))
    return(numberOfErrors)


#sun of 3*3 block
def SumOfOneBlock (sudoku, oneBlock):
    finalSum = 0
    for box in oneBlock:
        finalSum += sudoku[box[0], box[1]]
    return(finalSum)

#chooses two random boxes of a randomly choosen block
def TwoRandomBoxesWithinBlock(fixedSudoku, block):
    while (1):
        firstBox = random.choice(block)
        secondBox = choice([box for box in block if box is not firstBox ])

        if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
            return([firstBox, secondBox])


#flip two randomly choosen boxes
def FlipBoxes(sudoku, boxesToFlip):
    proposedSudoku = np.copy(sudoku)
    placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
    proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
    proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
    return (proposedSudoku)


#Creating new state by flipping two boxes within one choosen block
def ProposedState (sudoku, fixedSudoku, listOfBlocks):
    proposedSudoku = None
    boxesToFlip = None
    choosed = False

    while(not choosed):
        randomBlock = random.choice(listOfBlocks)
        if SumOfOneBlock(fixedSudoku, randomBlock) > 7:
            pass
        boxesToFlip = TwoRandomBoxesWithinBlock(fixedSudoku, randomBlock)
        proposedSudoku = FlipBoxes(sudoku,  boxesToFlip)
        choosed = True
        break
    return([proposedSudoku, boxesToFlip])


#Not compulsory but choosing the iterations same as the no of unknown boxes value
def ChooseNumberOfItterations(fixed_sudoku):
    numberOfItterations = 0
    for i in range (0,9):
        for j in range (0,9):
            if fixed_sudoku[i,j] != 0:
                numberOfItterations += 1
    return numberOfItterations


#calculating initial temperature by taking standard deviation of erros for 100 random proposed states ...
#... from initial state
def CalculateInitialSigma (sudoku, fixedSudoku, listOfBlocks):
    listOfDifferences = []
    tmpSudoku = sudoku
    for i in range(1,100):
        tmpSudoku = ProposedState(tmpSudoku, fixedSudoku, listOfBlocks)[0]
        listOfDifferences.append(CalculateNumberOfErrors(tmpSudoku))
    return (statistics.pstdev(listOfDifferences))


#New state creating and updating the state according to the acceptance probability
def ChooseNewState (currentSudoku, fixedSudoku, listOfBlocks, sigma):
    proposal = ProposedState(currentSudoku, fixedSudoku, listOfBlocks)
    newSudoku = proposal[0]
    boxesToCheck = proposal[1]
    currentCost = CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], currentSudoku) \
                    + CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], currentSudoku)
    newCost = CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], newSudoku) \
                    + CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], newSudoku)
    costDifference = newCost - currentCost

    #calculating acceptance probability
    rho = math.exp(-costDifference/sigma[0])
    #choosing the new state
    if(np.random.uniform(1,0,1) < rho):
        return([newSudoku, costDifference])
    return([currentSudoku, 0])


#initializing the suduko parameters and annealing process
def solveSudoku(sudoku, tmpSudoku, score):
    
    PrintSudoku(sudoku)

    global fixed_sudoku
    fixed_sudoku = copy.deepcopy(sudoku)
    FixSudokuValues(fixed_sudoku)

    listOfBlocks = CreateList3x3Blocks()
    tmpSudoku = RandomlyFill3x3Blocks(sudoku, listOfBlocks)
    global sigma
    sigma = [CalculateInitialSigma(sudoku, fixed_sudoku, listOfBlocks)]
    score = CalculateNumberOfErrors(tmpSudoku)
    iterations = ChooseNumberOfItterations(fixed_sudoku)
    solved_sudoku = annealing_sudoku(sigma, score, iterations, tmpSudoku, fixed_sudoku, listOfBlocks)

    return(solved_sudoku)
    

#the main simulated annealing process
def annealing_sudoku(sigma, score, iterations, tmpSudoku, fixedSudoku, listOfBlocks):
    decreaseFactor = 0.99
    stuckCount = 0

    global solution_found
    if score == 0:
        solution_found = True

    while not solution_found:
        previousScore = score
        for i in range (0, iterations):
            newState = ChooseNewState(tmpSudoku, fixedSudoku, listOfBlocks, sigma)
            tmpSudoku = newState[0]
            global tmp_sudoku
            tmp_sudoku = tmpSudoku #updating sudoku
            scoreDiff = newState[1] 
            score += scoreDiff
            global current_score
            current_score[0] = score #updating score
            #time.sleep(0.002)
            if score == 0:
                break
        
        if score == 0:
            if(CalculateNumberOfErrors(tmpSudoku)==0):
                solution_found = True
                break

        if score >= previousScore:
            stuckCount += 1
        else:
            stuckCount = 0

        sigma[0] *= decreaseFactor
        
        if (stuckCount > 100):
            stuckCount = 0
            sigma[0] = 5

    return(tmpSudoku)


#current local time in hr min sec msec
def get_current_time():
    return f"{time.localtime().tm_hour} hrs, {time.localtime().tm_min} min, {time.localtime().tm_sec} sec, {int(1000*(time.time() - int(time.time())))} millisec"


#thread for algorithm
def start_algorithm(sudoku, tmp_sudoku, progress_score):
    global start_time
    start_time = get_current_time()
    solution = solveSudoku(sudoku, tmp_sudoku, progress_score[0])
    global end_time
    end_time = get_current_time()

    PrintSudoku(solution)
    print("\nError: ", CalculateNumberOfErrors(solution))
    print(f"Start time: {start_time}\nEnd Time: {end_time}")



def get_current_sudoku():
    global tmp_sudoku
    return tmp_sudoku



def get_current_score():
    global current_score
    return current_score[0]



def get_current_tempr():
    global sigma
    return sigma[0]



def is_solution_found():
    global solution_found
    return solution_found



def get_startend_time():
    global start_time
    global end_time
    return start_time, end_time



def draw_grid(canvas):
    # Draw horizontal lines
    for i in range(10):
        width = 2 if i % 3 == 0 else 1
        canvas.create_line(50, 50 + i * 50, 500, 50 + i * 50, width=width)

    # Draw vertical lines
    for i in range(10):
        width = 2 if i % 3 == 0 else 1
        canvas.create_line(50 + i * 50, 50, 50 + i * 50, 500, width=width)



def draw_numbers(canvas, puzzle):
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] != 0:
                global fixed_sudoku
                if fixed_sudoku[i][j] == 1:
                    canvas.create_text(75 + j * 50, 75 + i * 50, text=str(puzzle[i][j]), font=("Arial", 18, "bold"), fill="red")
                else:
                    canvas.create_text(75 + j * 50, 75 + i * 50, text=str(puzzle[i][j]), font=("Arial", 16))
            else:
                canvas.create_text(75 + j * 50, 75 + i * 50, text=str(0), font=("Arial", 16))



def draw_score(canvas, score):
    canvas.delete("all")
    canvas.create_text(100, 30, text="Error Score: " + str(score), font=("Arial", 16))



def draw_time(canvas, time):
    canvas.delete("all")
    start_time, end_time = time
    multiline_text = f"Start Time: {start_time}\nEnd Time: {end_time}"
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



def new_puzzle(root, canvas_box, canvas_score, canvas_time, canvas_temp):
    canvas_box.delete("all")
    puzzle = get_current_sudoku()
    draw_numbers(canvas_box, puzzle)
    draw_grid(canvas_box)
    
    score = get_current_score()
    draw_score(canvas_score, score)

    sigma = get_current_tempr()
    draw_value_bar(canvas_temp, sigma)

    if(is_solution_found()):
        time = get_startend_time()
        draw_time(canvas_time, time)

    root.after(10, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp)



def start_ui():
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

    root.after(10, new_puzzle, root, canvas_box, canvas_score, canvas_time, canvas_temp)
    root.mainloop()




if __name__ == "__main__":
    # initial unsolved sudoku
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

    sudoku = np.array([[int(i) for i in line] for line in startingSudoku.split()])
    tmp_sudoku = copy.deepcopy(sudoku)
    progress_score = [999]

    #thread
    solve_sudoku_thread = threading.Thread(target=start_algorithm, args=(sudoku, tmp_sudoku, progress_score))
    solve_sudoku_thread.start()
    start_ui()
    solve_sudoku_thread.join()