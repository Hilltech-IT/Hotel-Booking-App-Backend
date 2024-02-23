import numpy as np

class Othello:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = -1
        self.current_player = 1
        self.valid_moves = self.get_valid_moves()

    def display_board(self):
        print("   0 1 2 3 4 5 6 7")
        for i in range(8):
            print(i, end="  ")
            for j in range(8):
                if self.board[i][j] == 1:
                    print('○', end=" ")
                elif self.board[i][j] == -1:
                    print('●', end=" ")
                else:
                    print('_', end=" ")
            print()

    def get_valid_moves(self):
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 0 and self.is_valid_move(i, j):
                    valid_moves.append((i, j))
        return valid_moves

    def is_valid_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        if self.board[row][col] != 0:
            return False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] == 0:
                        break
                    if self.board[r][c] == self.current_player:
                        return True
                    r, c = r + dr, c + dc
        return False

    def make_move(self, row, col):
        if (row, col) in self.valid_moves:
            self.board[row][col] = self.current_player
            self.flip_tiles(row, col)
            self.current_player *= -1
            self.valid_moves = self.get_valid_moves()
        else:
            print("Invalid move! Try again.")

    def flip_tiles(self, row, col):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                to_flip = []
                while 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] == 0:
                        break
                    if self.board[r][c] == self.current_player:
                        for flip_row, flip_col in to_flip:
                            self.board[flip_row][flip_col] = self.current_player
                        break
                    else:
                        to_flip.append((r, c))
                    r, c = r + dr, c + dc

    def check_winner(self):
        if len(self.valid_moves) == 0:
            score = np.sum(self.board)
            if score > 0:
                return "○ wins!"
            elif score < 0:
                return "● wins!"
            else:
                return "It's a tie!"
        return None

    def play_game(self):
        while True:
            self.display_board()
            print(f"Current player: {'○' if self.current_player == 1 else '●'}")
            print("Valid moves:", self.valid_moves)
            if len(self.valid_moves) == 0:
                print("No valid moves for current player.")
                winner = self.check_winner()
                if winner:
                    print(winner)
                    break
                self.current_player *= -1
                self.valid_moves = self.get_valid_moves()
                continue
            row = int(input("Enter row: "))
            col = int(input("Enter column: "))
            self.make_move(row, col)

if __name__ == "__main__":
    game = Othello()
    game.play_game()
