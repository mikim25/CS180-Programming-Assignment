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
    memo = [[None for x in range(n)] for y in range(n)] # initialize memo
    return helper(n, H, tile_types, tile_values, 0, 0, 0, 0, memo) # 0, 0, 0, 0 -> i, j, ptoken, mtoken


def helper(n, H, tile_types, tile_values, i, j, ptoken, mtoken, memo):
    # NOTE: Dynamic programming algorithm checks if it's possible to reach bottom-right
    # corner without running out of HP. Returns True if possible, False otherwise.

    # BASE CASE: out of bounds
    if (i == n) or (j == n):
        return False
    
    # BASE CASE: memo[i][j] exists
    if memo[i][j] is not None:
        return memo[i][j]
    
    # BASE CASE: neg health, no ptoken available
    if (tile_types[i][j] == 0) and (H - tile_values[i][j] < 0) and (ptoken == 0):
        memo[i][j] = False
        return memo[i][j]
    
    # BASE CASE: reached last square with 0 or pos health
    if (i == n-1) and (j == n-1):
        memo[i][j] = True
        return memo[i][j]

    # initialize moves
    down = None
    right = None

    # BASE CASE: last row XOR last column
    if i == n-1: # last row
        down = False
    if j == n-1: # last column
        right = False

    # current tile logic
    match tile_types[i][j]:
        case 0: # DMG -> lose HP ——————————————————————————————————————————————————————————————
            takeD = H - tile_values[i][j]
            downPT = down
            rightPT = right

            # ptoken available
            if ptoken == 1:
                # any health, use ptoken
                if downPT is None:
                    downPT = helper(n, H, tile_types, tile_values, i+1, j, ptoken-1, mtoken, memo)
                if rightPT is None:
                    rightPT = helper(n, H, tile_types, tile_values, i, j+1, ptoken-1, mtoken, memo)
                
                # neg health, must use ptoken
                if takeD < 0:
                    if True in {downPT, rightPT}:
                        memo[i][j] = True
                    else:
                        memo[i][j] = False
                    return memo[i][j]
                
            # 0 or pos health, ptoken not available or not used
            if down is None:
                down = helper(n, takeD, tile_types, tile_values, i+1, j, ptoken, mtoken, memo)
            if right is None:
                right = helper(n, takeD, tile_types, tile_values, i, j+1, ptoken, mtoken, memo)

            # 0 or pos health
            if True in {down, right, downPT, rightPT}:
                memo[i][j] = True
            else:
                memo[i][j] = False

        case 1: # HEAL -> gain HP —————————————————————————————————————————————————————————————

            takeH = H + tile_values[i][j]
            doubleH = H + 2 * tile_values[i][j]
            
            # no mtoken available or don't use mtoken
            downMT = down
            rightMT = right
            if down is None:
                down = helper(n, takeH, tile_types, tile_values, i+1, j, ptoken, mtoken, memo)
            if right is None:
                right = helper(n, takeH, tile_types, tile_values, i, j+1, ptoken, mtoken, memo)

            # mtoken available
            if mtoken == 1:
                if downMT is None:
                    downMT = helper(n, doubleH, tile_types, tile_values, i+1, j, ptoken, mtoken-1, memo)
                if rightMT is None:
                    rightMT = helper(n, doubleH, tile_types, tile_values, i, j+1, ptoken, mtoken-1, memo)
                
            if True in {down, right, downMT, rightMT}:
                memo[i][j] = True
            else:
                memo[i][j] = False

        case 2: # PTOKEN -> can nullify an instance of DMG ————————————————————————————————————————————
            if ptoken == 0:
                ptoken = 1
            
            if down is None:
                down = helper(n, H, tile_types, tile_values, i+1, j, ptoken, mtoken, memo)
            if right is None:
                right = helper(n, H, tile_types, tile_values, i, j+1, ptoken, mtoken, memo)

            if True in {down, right}:
                memo[i][j] = True
            else:
                memo[i][j] = False

        case 3: # MTOKEN -> can double an instance of HEAL ————————————————————————————————————————————
            if mtoken == 0:
                mtoken = 1
            
            if down is None:
                down = helper(n, H, tile_types, tile_values, i+1, j, ptoken, mtoken, memo)
            if right is None:
                right = helper(n, H, tile_types, tile_values, i, j+1, ptoken, mtoken, memo)

            if True in {down, right}:
                memo[i][j] = True
            else:
                memo[i][j] = False

        case _:
            return False
        
    return memo[i][j]


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
