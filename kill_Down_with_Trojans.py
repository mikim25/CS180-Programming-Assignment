# python PA_checker.py
# python kill_Down_with_Trojans.py
import numpy as np
import math

def load_input_file(file_name):
    with open(file_name, 'r') as file:
        n, H = map(int, file.readline().split())
        tile_types = np.zeros((n, n), dtype=int)
        tile_values = np.zeros((n, n), dtype=int)

        for i in range(n * n):
            if i == 0:
                continue  # the initial tile is zero type with zero value
            x, y, t, v = map(int, file.readline().split())
            tile_types[x][y] = t
            tile_values[x][y] = v

    return n, H, tile_types, tile_values


def print_tile_data(tile_types, tile_values):
    print("Tile Types:")
    print(tile_types)
    print("\nTile Values:")
    print(tile_values)


# current solution
def DP(n, H, tile_types, tile_values):
    memo = np.full((n, n, 4), None) # initialize memo
    minH = helper(n, H, tile_types, tile_values, 0, 0, 0, 0, memo) # 0, 0, 0, 0 -> i, j, ptoken, mtoken
    return minH <= H


def helper(n, H, tile_types, tile_values, i, j, ptoken, mtoken, memo):
    # NOTE: Dynamic programming algorithm to check if it's possible to reach bottom-right
    # corner without running out of HP; returns True if possible, False otherwise.

    # base cases ——————————————————————————————————————————————————————————————————————————————————————

    if (ptoken == 0) and (mtoken == 0):
        quad = 0
    if (ptoken == 0) and (mtoken == 1):
        quad = 1
    if (ptoken == 1) and (mtoken == 0):
        quad = 2
    if (ptoken == 1) and (mtoken == 1):
        quad = 3

    # out of bounds
    if (i >= n) or (j >= n):
        return math.inf
    
    # reached last square
    if (i == n-1) and (j == n-1):
        if (tile_types[i][j] == 0) and (ptoken == 0):
            end = tile_values[i][j]
        else:
            end = 0

        if memo[i][j][quad] is not None:
            memo[i][j][quad] = min(memo[i][j][quad], end)
        else:
            memo[i][j][quad] = end

    # memo otherwise exists
    if memo[i][j][quad] is not None:
        return memo[i][j][quad]
    
    down = math.inf
    right = math.inf
    downPT = math.inf
    rightPT = math.inf
    downMT = math.inf
    rightMT = math.inf

    # current tile logic
    match tile_types[i][j]:
        case 0: # DMG -> lose HP ——————————————————————————————————————————————————————————————————————

            # use ptoken, don't take DMG
            if ptoken == 1:
                downPT  = helper(n, H, tile_types, tile_values, i+1, j, 0, mtoken, memo)
                rightPT = helper(n, H, tile_types, tile_values, i, j+1, 0, mtoken, memo)

            # don't use ptoken, take DMG
            down  = helper(n, H, tile_types, tile_values, i+1, j, ptoken, mtoken, memo) + tile_values[i][j]
            right = helper(n, H, tile_types, tile_values, i, j+1, ptoken, mtoken, memo) + tile_values[i][j]

        case 1: # HEAL -> gain HP —————————————————————————————————————————————————————————————————————

            # take double heal
            if mtoken == 1:
                downMT  = max(0, helper(n, H, tile_types, tile_values, i+1, j, ptoken, 0, memo) - 2*tile_values[i][j])
                rightMT = max(0, helper(n, H, tile_types, tile_values, i, j+1, ptoken, 0, memo) - 2*tile_values[i][j])
            
            # take regular heal
            down  = max(0, helper(n, H, tile_types, tile_values, i+1, j, ptoken, mtoken, memo) - tile_values[i][j])
            right = max(0, helper(n, H, tile_types, tile_values, i, j+1, ptoken, mtoken, memo) - tile_values[i][j])

        case 2: # PTOKEN -> can nullify an instance of DMG ————————————————————————————————————————————
            down  = helper(n, H, tile_types, tile_values, i+1, j, 1, mtoken, memo)
            right = helper(n, H, tile_types, tile_values, i, j+1, 1, mtoken, memo)

        case 3: # MTOKEN -> can double an instance of HEAL ————————————————————————————————————————————
            down  = helper(n, H, tile_types, tile_values, i+1, j, ptoken, 1, memo)
            right = helper(n, H, tile_types, tile_values, i, j+1, ptoken, 1, memo)

        case _:
            print("Invalid tile type!")

    memo[i][j][quad] = min(down, right, downPT, rightPT, downMT, rightMT)
    return memo[i][j][quad]


# previous solution
'''
# 3D MEMO
def DP(n, H, tile_types, tile_values):
    memo = np.full((n, n, 4), None) # initialize memo
    # if holding ? ptoken and ? mtoken on this square, what's the max HP I can have when I get to the end?
    maxH = helper(n, H, tile_types, tile_values, 0, 0, 0, 0, memo) # 0, 0, 0, 0 -> i, j, ptoken, mtoken
    return maxH >= 0


def helper(n, H, tile_types, tile_values, i, j, ptoken, mtoken, memo):
    # NOTE: Dynamic programming algorithm to check if it's possible to reach bottom-right
    # corner without running out of HP; returns True if possible, False otherwise.

    # base cases ——————————————————————————————————————————————————————————————————————————————————————

    if (ptoken == 0) and (mtoken == 0):
        quad = 0
    if (ptoken == 0) and (mtoken == 1):
        quad = 1
    if (ptoken == 1) and (mtoken == 0):
        quad = 2
    if (ptoken == 1) and (mtoken == 1):
        quad = 3

    # out of bounds
    if (i >= n) or (j >= n):
        return -1
    
    # game over (neg health, no ptoken)
    if (tile_types[i][j] == 0) and (H - tile_values[i][j] < 0) and (ptoken == 0):
        return -1
    
    # reached last square with 0 or pos health
    if (i == n-1) and (j == n-1):

        if tile_types[i][j] == 0:
            if ptoken == 0:
                memo[i][j][quad] = H - tile_values[i][j]
            else: # ptoken == 1
                memo[i][j][quad] = H
            return memo[i][j][quad]
        elif tile_types[i][j] == 1:
            if mtoken == 0:
                memo[i][j][quad] = H + tile_values[i][j]
            else: # mtoken == 1
                memo[i][j][quad] = H + 2 * tile_values[i][j]
        else: # token tile
            memo[i][j][quad] = H
    
        return memo[i][j][quad]

    # memo otherwise exists
    if memo[i][j][quad] is not None:
        return memo[i][j][quad]
    
    downPT = -1
    rightPT = -1
    downMT = -1
    rightMT = -1

    # current tile logic
    match tile_types[i][j]:
        case 0: # DMG -> lose HP ——————————————————————————————————————————————————————————————————————
            takeD = H - tile_values[i][j]
            
            # use ptoken
            if ptoken == 1:
                downPT = helper(n, H, tile_types, tile_values, i+1, j, ptoken-1, mtoken, memo)
                rightPT = helper(n, H, tile_types, tile_values, i, j+1, ptoken-1, mtoken, memo)

            # neg health, must use ptoken
            if takeD < 0:
                memo[i][j][quad] = downPT or rightPT
                return memo[i][j][quad]
                
            # don't use ptoken
            H = takeD

        case 1: # HEAL -> gain HP —————————————————————————————————————————————————————————————————————
            takeH = H + tile_values[i][j]
            doubleH = H + 2 * tile_values[i][j]

            # take double heal
            if mtoken == 1:
                downMT = helper(n, doubleH, tile_types, tile_values, i+1, j, ptoken, mtoken-1, memo)
                rightMT = helper(n, doubleH, tile_types, tile_values, i, j+1, ptoken, mtoken-1, memo)
            
            # take regular heal
            H = takeH

        case 2: # PTOKEN -> can nullify an instance of DMG ————————————————————————————————————————————
            ptoken = 1

        case 3: # MTOKEN -> can double an instance of HEAL ————————————————————————————————————————————
            mtoken = 1

        case _:
            print("Invalid tile type!")

    down = helper(n, H, tile_types, tile_values, i+1, j, ptoken, mtoken, memo)
    right = helper(n, H, tile_types, tile_values, i, j+1, ptoken, mtoken, memo)

    memo[i][j][quad] = max(down, right, downPT, rightPT, downMT, rightMT)
    return memo[i][j][quad]
'''

def write_output_file(output_file_name, result):
    with open(output_file_name, 'w') as file:
        file.write(str(int(result)))


def main(input_file_name):
    n, H, tile_types, tile_values = load_input_file(input_file_name)
    print_tile_data(tile_types, tile_values)
    result = DP(n, H, tile_types, tile_values)
    print("Result: " + str(result))
    output_file_name = input_file_name.replace(".txt", "_out.txt")
    write_output_file(output_file_name, result)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python kill_Down_with_Trojans.py a_file_name.txt")
    else:
        main(sys.argv[1])
