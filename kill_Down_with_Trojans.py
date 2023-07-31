import numpy as np
import scipy

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


def DP(n, H, tile_types, tile_values):
    memo = np.full((n, 4*n), None) # initialize memo
    maxH = helper(n, H, tile_types, tile_values, 0, 0, 0, 0, memo) # 0, 0, 0, 0 -> i, j, ptoken, mtoken
    return maxH >= 0


def helper(n, H, tile_types, tile_values, i, j, ptoken, mtoken, memo):
    # NOTE: Dynamic programming algorithm to check if it's possible to reach bottom-right
    # corner without running out of HP; returns True if possible, False otherwise.

    # base cases ——————————————————————————————————————————————————————————————————————————————————————

    if (ptoken == 0) and (mtoken == 0):
        quad = 0*n + j
    if (ptoken == 0) and (mtoken == 1):
        quad = 1*n + j
    if (ptoken == 1) and (mtoken == 0):
        quad = 2*n + j
    if (ptoken == 1) and (mtoken == 1):
        quad = 3*n + j

    # out of bounds
    if (i == n) or (j == n):
        return False
    
    # game over (neg health, no ptoken)
    if (tile_types[i][j] == 0) and (H - tile_values[i][j] < 0) and (ptoken == 0):
        return False
    
    # reached last square with 0 or pos health
    if (i == n-1) and (j == n-1):
        memo[i][quad] = True
        return memo[i][quad]

    # memo[i][j] otherwise exists
    if memo[i][j] is not None:
        return memo[i][j]
    
    downPT = False
    rightPT = False
    downMT = False
    rightMT = False

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
                memo[i][quad] = downPT or rightPT
                return memo[i][quad]
                
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

    memo[i][quad] = down or right or downPT or rightPT or downMT or rightMT
    return memo[i][quad]

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
        