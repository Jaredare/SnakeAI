from snake import SnakeGameAI

SG = SnakeGameAI()

SCREEN = True

combo, direction = SG.reset()
SG.play_step(combo, direction)