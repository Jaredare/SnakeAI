import time
import sys
import random
from datetime import datetime

# X_BOUNDS and Y_BOUNDS may or may not be functional, I can't remember, and I don't care to test them.
X_BOUNDS = 10
Y_BOUNDS = 10
# This is an override for the screen and sleep_time in agent.py. These rules will happen on all runs, whereas the ones in agent.py only happen every 50th run.
SCREEN = False
SLEEP_TIME = 0


class Directions:
    LEFT = 0 
    UP = 1 
    RIGHT = 2 
    DOWN = 3 

class Play_Step_Combo_Contents:
    # This class if a reference for where each piece is in the variable known as combo or play_step_combo.
    SNAKE = 0
    FRUIT = 1
    SCORE = 2
    DEATH = 3
    REWARD = 4
    TURN = 5
    FRUIT_DISTANCE = 6
    PREVIOUS_NEAREST_DISTANCE = 7
    SCREEN = 8
    SLEEP_TIME = 9
    

def main():
    # Main was just for testing after I got agent.py going, and as such does nothing helpful at the moment.
    SG = SnakeGameAI()
    combo, direction = SG.reset()
    death = combo[3]
    while death == False:
        reward, death, score, combo, direction = SG.play_step(combo, direction)
        direction = SG.random_brain(direction)
    pass

class SnakeGameAI:

    def __init__(self):
        pass
    

    def reset(self):
        snake = []
        fruit = []
        direction = 2
        score = 0
        death = False
        reward = 0
        turn = 0
        fruit_distance = 0
        previous_nearest_distance = 10000000
        screen = False
        sleep_time = 0

        self.fruit_place(snake, fruit)
        self.snake_start(snake)
        if screen == True or SCREEN == True:
            self.clear_screen()
            self.screen(snake, fruit)

        return (snake, fruit, score, death, reward, turn, fruit_distance, previous_nearest_distance, screen, sleep_time), direction



    def play_step(self, combo, direction):
        """Take the snake through one frame of the game, moving it forward, eating any possible fruit, testing for collision, and rewarding it according to it's actions"""
        snake, fruit, score, death, reward, turn, fruit_distance, previous_nearest_distance, screen, sleep_time = combo
        
        if SLEEP_TIME != 0:
            time.sleep(SLEEP_TIME)
        else: 
            time.sleep(sleep_time)

        # Move the snake one block in the direction specified
        self.snake_move(snake, direction)

        # If the snake is eating a fruit, eat and respawn it. The if is in fruit_eat.
        score, reward, previous_nearest_distance = self.fruit_eat(snake, fruit, score, reward, previous_nearest_distance)
        self.fruit_place(snake, fruit)


        # Refresh the screen
        if screen == True or SCREEN == True:
            self.clear_screen()
            self.screen(snake, fruit)
        

        # Check to see if the snake is biting it's tail or moving out of bounds
        tail_bite = self.bite_tail(snake)
        oob = self.out_of_bounds(snake)
        
        # Negative reward to prevent stalling out
        # reward -= 0.01
        turn += 1

        # Calculate distance from head to fruit, and award it if it's the closest it's been to this particular fruit.
        fruit_distance = self.find_fruit_distance(snake, fruit)
        if fruit_distance < previous_nearest_distance :
            if previous_nearest_distance != 10000000:
                # reward += 0.03
                pass
            previous_nearest_distance = fruit_distance


        #TEMPORARY TEST BIT 
        # if direction == 3:
        #     reward += 1 

        if turn > (80 * (score + 1)):
            death = "T-O"
            reward -= 1

        # If the snake should die, it dies.
        if oob: 
            death = "OOB"
            reward -= 1
        if tail_bite:
            reward -= 1
            death = "TB"

        screen = False

            
        return reward, death, score, (snake, fruit, score, death, reward, turn, fruit_distance, previous_nearest_distance, screen, sleep_time), direction



    def random_brain(self, direction):

        """The current brain takes the current direction, and will randomly go straight or turn left or right."""
        find_new_direction = True
        while find_new_direction:
            new_direction = random.randint(0, 3)
            if new_direction != direction - 2 and new_direction != direction + 2:
                find_new_direction = False

        return int(new_direction)



    def snake_start(self, snake):
        """Generates a random location generally in the center for the 
        snake to start. Gives the snake 2 sections."""
        # X and Y are set in a random area within the middle 1/3 of the map. This is done by randinting between the value of the end of the first third and the value of the end of the second third.
        x = random.randint(int(round(X_BOUNDS / 3)), int(round((X_BOUNDS / 3) * 2)))
        y = random.randint(int(round(Y_BOUNDS / 3)), int(round((Y_BOUNDS / 3) * 2)))
        new_snake = [x, y] 
        snake.insert(0, new_snake)
        new_snake = [x, y - 1]
        snake.append(new_snake)

        return snake



    def snake_move(self, snake, direction):
        """Moves the snake 1 block based on which direction it's moving"""
        # If the snake is moving left:
        if direction == Directions.LEFT:
            old_x_y = snake[0]
            x = old_x_y[0] 
            y = old_x_y[1] - 1
            snake.insert(0, [x, y])
            snake = snake.pop()

        # If the snake is moving up:
        if direction == Directions.UP:
            old_x_y = snake[0]
            x = old_x_y[0] - 1
            y = old_x_y[1]
            snake.insert(0, [x, y])
            snake = snake.pop()

        # If the snake is moving right:
        if direction == Directions.RIGHT:
            old_x_y = snake[0]
            x = old_x_y[0] 
            y = old_x_y[1] + 1
            snake.insert(0, [x, y])
            snake = snake.pop()

        # If the snake is moving down:
        if direction == Directions.DOWN:
            old_x_y = snake[0]
            x = old_x_y[0] + 1
            y = old_x_y[1] 
            snake.insert(0, [x, y])
            snake = snake.pop()

        return snake



    def snake_grow(self, snake):
        """Grows the snake by duplicating the last entry.
        This poses a problem if the snake starts off with 1 length
        because tail_bite will incorrectly recognize it as a tail bite
        if the snake grows."""
        snake.append(snake[-1])
        return snake



    def fruit_eat(self, snake, fruit, score, reward, previous_nearest_distance):
        """Checks to see if the the snake's head is overlapping with a 
        fruit. If it is, it increases the score and grows the snake."""
        if snake[0] == fruit[0]:
            fruit.pop()
            score += 1
            reward += 1
            self.snake_grow(snake)
            previous_nearest_distance = 10000000
        return score, reward, previous_nearest_distance



    def fruit_place(self, snake, fruit):
        """If there is not fruit, generates a fruit in a random spot."""
        while fruit == []:

            # Generate the x and y coordinates for the new fruit
            x = random.randint(0, X_BOUNDS - 1)
            y = random.randint(0, Y_BOUNDS - 1)
            new_fruit = [x, y]

            # If the new fruit doesn't overlap with the snake, place it.
            if new_fruit not in snake:
                fruit.append(new_fruit)
                


    def snake_eyes(self, snake, fruit, direction):
        """Creates the state that the neural network receives as input. It's called snake eyes because it's how the AI sees."""
        head = snake[0]
        fruit = fruit[0]
        head_x = head[0]
        head_y = head[1]
        fruit_x = fruit[0]
        fruit_y = fruit[1]

        fruit_up = 0
        fruit_right = 0
        fruit_down = 0
        fruit_left = 0
        danger_up = 0
        danger_right = 0
        danger_down = 0
        danger_left = 0
        direction_left = 0
        direction_up = 0
        direction_right = 0
        direction_down = 0

        # Where is the fruit in comparison to the snake?
        if head_y > fruit_y:
            fruit_left = 1
        if head_x > fruit_x:
            fruit_up = 1
        if head_y < fruit_y:
            fruit_right = 1
        if head_x < fruit_x:
            fruit_down = 1



        # Is there a boundary or piece of the snake left, right, up or down?
        if [head_x, head_y - 1] in snake or head_y == 0:
            danger_left = 1 
        if [head_x - 1, head_y] in snake or head_x == 0:
            danger_up = 1 
        if [head_x, head_y + 1] in snake or head_y == Y_BOUNDS:
            danger_right = 1 
        if [head_x + 1, head_y] in snake or head_x == X_BOUNDS:
            danger_down = 1 
        
        # Which direction is the snake headed?
        if direction == 0:
            direction_left = 1
        if direction == 1:
            direction_up = 1
        if direction == 2:
            direction_right = 1
        if direction == 3:
            direction_right = 1

        # 8: return [int(fruit_left), int(fruit_up), int(fruit_right), int(fruit_down), int(danger_left), int(danger_up), int(danger_right), int(danger_down)]
        # return [int(fruit_left), int(fruit_up), int(fruit_right), int(fruit_down), int(danger_left), int(danger_up), int(danger_right), int(danger_down), int(direction)]
        return [int(fruit_left), int(fruit_up), int(fruit_right), int(fruit_down), int(danger_left), int(danger_up), int(danger_right), int(danger_down), int(direction_left), int(direction_up), int(direction_right), int(direction_down)]
        
        

    def find_fruit_distance(self, snake, fruit):
        """Finds the minimum amount of moves it would take to eat the fruit, not taking into account the direction the snake is facing."""
        head = snake[0]
        head_x = head[0]
        head_y = head[1]
        fruit = fruit[0]
        fruit_x = fruit[0]
        fruit_y = fruit[1]

        if head_x <= fruit_x and head_y <= fruit_y:
            x_distance = fruit_x - head_x
            y_distance = fruit_y - head_y

        elif head_x <= fruit_x and head_y >= fruit_y:
            x_distance = fruit_x - head_x
            y_distance = head_y - fruit_y

        elif head_x >= fruit_x and head_y <= fruit_y:
            x_distance = head_x - fruit_x
            y_distance = fruit_y - head_y

        elif head_x >= fruit_x and head_y >= fruit_y:
            x_distance = head_x - fruit_x
            y_distance = head_y - fruit_y

        
        else:
            print("No distance found in find_fruit_distance")
            print(f"head_x = {head_x}, fruit_x = {fruit_x}\nhead_y = {head_y}, fruit_y = {fruit_y}")
            time.sleep(10)
        
        total_distance = int(x_distance + y_distance)
        return total_distance



    def screen(self, snake, fruit):
        """Prints a screen based on the X and Y bounds at the top of 
        the program showing the snake, fruit, and outline. """

        # Print the top side of the outline
        print(" -------------------- ")
        for x in range(X_BOUNDS):
            # Print the left side of the outline
            print("| ", end="")
            for y in range(Y_BOUNDS):
                coordinates = [x, y]

                # Test if the snake inhabits this coordinate, and if so print the coordinate as a green O
                if coordinates in snake:

                    # Test if the snake's head is here
                    if snake[0] == coordinates:
                        # Print the head
                        sys.stdout.write("\033[1;34m")
                        sys.stdout.write("H ")
                        sys.stdout.write("\033[1;0m")
                    else:
                        # Print the body
                        sys.stdout.write("\033[1;32m")
                        sys.stdout.write("O ")
                        sys.stdout.write("\033[1;0m")

                # Test if the fruit is here
                elif coordinates in fruit:
                    # Print a fruit
                    sys.stdout.write("\033[1;31m")
                    sys.stdout.write("a ")
                    sys.stdout.write("\033[1;0m")

                else:
                    # Print an empty cell
                    sys.stdout.write("O ")
            # Print the right side of the outline
            print("|")
        # Print the bottom side of the outline
        print(" ---------------------")



    def clear_screen(self):
        """Clears the screen based on how tall it is as set at the top of the file."""

        height = Y_BOUNDS + 5
        
        for _ in range(height):
            # Deletes the last Y_BOUNDS lines

            # Cursor up 1 line
            sys.stdout.write(f'\x1b[1A')
            # Delete last line
            sys.stdout.write(f'\x1b[2K')



    def bite_tail(self, snake):
        """Checks to see if the snake is biting it's tail"""

        tail_bite = snake.count(snake[0])
        if tail_bite > 1:
            return True
        


    def out_of_bounds(self, snake):
        """Checks to see if the snake's head is out of bounds"""

        head = snake[0]
        x = head[0]
        y = head[1]
        if x >= X_BOUNDS or x < 0 or y >= Y_BOUNDS or y < 0:
            return True

if __name__ == "__main__":
    main()