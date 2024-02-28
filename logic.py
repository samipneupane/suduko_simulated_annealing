import random
import numpy as np
import math 
from random import choice
import statistics 
import time
import copy



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
            if fixed_sudoku[0][i,j] != 0:
                fixed_sudoku[0][i,j] = 1
    return(fixed_sudoku[0])



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
            if sudoku[0][box[0],box[1]] == 0:
                currentBlock = sudoku[0][block[0][0]:(block[-1][0]+1),block[0][1]:(block[-1][1]+1)]
                sudoku[0][box[0],box[1]] = choice([i for i in range(1,10) if i not in currentBlock])
    return sudoku[0]



#total no of errors  
def CalculateNumberOfErrors(sudoku):
    numberOfErrors = 0 
    for i in range (0,9):
        numberOfErrors += CalculateNumberOfErrorsRowColumn(i ,i , sudoku)
    return numberOfErrors



#no of errors for for row and column (i, i)
def CalculateNumberOfErrorsRowColumn(row, column, sudoku):
    numberOfErrors = (9 - len(np.unique(sudoku[0][:,column]))) + (9 - len(np.unique(sudoku[0][row,:])))
    return(numberOfErrors)



#sun of 3*3 block
def SumOfOneBlock (sudoku, oneBlock):
    finalSum = 0
    for box in oneBlock:
        finalSum += sudoku[0][box[0], box[1]]
    return(finalSum)



#chooses two random boxes of a randomly choosen block
def TwoRandomBoxesWithinBlock(fixedSudoku, block):
    while (1):
        firstBox = random.choice(block)
        secondBox = choice([box for box in block if box is not firstBox ])
        if fixedSudoku[0][firstBox[0], firstBox[1]] != 1 and fixedSudoku[0][secondBox[0], secondBox[1]] != 1:
            return([firstBox, secondBox])



#flip two randomly choosen boxes
def FlipBoxes(sudoku, boxesToFlip):
    proposedSudoku = np.copy(sudoku)
    placeHolder = proposedSudoku[0][boxesToFlip[0][0], boxesToFlip[0][1]]
    proposedSudoku[0][boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[0][boxesToFlip[1][0], boxesToFlip[1][1]]
    proposedSudoku[0][boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
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
            if fixed_sudoku[0][i,j] != 0:
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
def solveSudoku(sudoku, tmpSudoku, fixed_sudoku, current_score, sigma, solution_found):
    
    PrintSudoku(sudoku[0])
    
    fixed_sudoku[0] = copy.deepcopy(sudoku[0])
    FixSudokuValues(fixed_sudoku)
    listOfBlocks = CreateList3x3Blocks()
    tmpSudoku[0] = RandomlyFill3x3Blocks(sudoku, listOfBlocks)
    sigma[0] = CalculateInitialSigma(sudoku, fixed_sudoku, listOfBlocks)
    current_score[0] = CalculateNumberOfErrors(tmpSudoku)
    iterations = ChooseNumberOfItterations(fixed_sudoku)
    solved_sudoku = annealing_sudoku(sigma, current_score, iterations, tmpSudoku, fixed_sudoku, listOfBlocks, solution_found)

    return(solved_sudoku)
    


#the main simulated annealing process
def annealing_sudoku(sigma, score, iterations, tmpSudoku, fixedSudoku, listOfBlocks, solution_found):
    decreaseFactor = 0.99
    stuckCount = 0

    if score[0] == 0:
        solution_found = True

    while not solution_found[0]:
        previousScore = score[0]
        for i in range (0, iterations):
            newState = ChooseNewState(tmpSudoku, fixedSudoku, listOfBlocks, sigma)
            tmpSudoku[0] = newState[0][0] #updating sudoku
            scoreDiff = newState[1] 
            score[0] += scoreDiff  #updating score
            #time.sleep(0.001)
            if score[0] == 0:
                break
        
        if score[0] == 0:
            if(CalculateNumberOfErrors(tmpSudoku)==0):
                solution_found[0] = True
                break

        if score[0] >= previousScore:
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



#thread for algorithm starts here
def start_algorithm(sudoku, tmp_sudoku, fixed_sudoku, current_score, sigma, start_time, end_time, solution_found):
    start_time[0] = get_current_time()
    solution = solveSudoku(sudoku, tmp_sudoku, fixed_sudoku, current_score, sigma, solution_found)
    end_time[0] = get_current_time()

    PrintSudoku(solution[0])
    print("\nError: ", CalculateNumberOfErrors(solution))
    print(f"Start time: {start_time[0]}\nEnd Time: {end_time[0]}")
