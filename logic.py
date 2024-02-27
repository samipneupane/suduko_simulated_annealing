import random
import numpy as np
import math 
from random import choice
import statistics 
import time
import copy



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