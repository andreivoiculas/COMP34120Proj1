import os
import sys
import copy
import numpy as np
import math

sys.setrecursionlimit(200000)

bot_name = sys.argv[1]
# max_depth = int(sys.argv[2])
log = open("log_{:s}.txt".format(bot_name),"w")
# this is what the program outputted last game
output_log = ""
# this was the engine input from last game
input_log = ""
# any value that might be useful to printout goes here
debbuging_log = ""

reachEnd = 0
no_of_moves = 1.0

empty_row = np.zeros(7,dtype = int)



class MKAgent(object):
  """docstring for MKAgent"""
  def __init__(self):
    global debbuging_log

    super(MKAgent, self).__init__()
    self.player = -1
    self.board = np.array([7,7,7,7,7,7,7,0,7,7,7,7,7,7,7,0])
    self.game_over = False
    self.my_turn = False
    self.first_turn = True
    

  def minimax(self,board,player,
              my_player,depth = 0,
             alpha = -99,beta = 99):
    global debbuging_log
    global reachEnd
    global no_of_moves

    if depth == -1 or depth > math.floor(abs(10 - 12/(pow(no_of_moves, 0.5) - 0.3))):
    # if depth == -1 or depth > math.floor(1/65 * pow(no_of_moves - 18, 2) + 3):
      reward = self.reward(board,my_player)
    #   debbuging_log += "reward " + str(reward) + "\n"
      return reward
    else:
      action_range = None
      new_board = None
      new_depth = None
      if not player:
        action_range = range(0,7)
      else:
        action_range = range(8,15)
      action = -1
      if player == my_player:      
        max_val = -100
        for i in action_range:
          new_board,new_player,terminal = self.apply_action(board,i,player)
          if terminal:
            reachEnd += 1
            new_depth = -1
          else:
            new_depth = depth + 1
          curr_val = self.minimax(new_board,new_player,my_player,
                                  new_depth,alpha,beta)
          max_val = max(max_val,curr_val)
          alpha = max(alpha,curr_val)
          if beta <= alpha:
            break
        # debbuging_log += "{:s} {:d}\n".format(str(actions),max_val)
        return max_val
      else:
        min_val = 99
        for i in action_range:
          new_board,new_player,terminal = self.apply_action(board,i,player)
          if terminal:
            reachEnd += 1
            new_depth = -1
          else:
            new_depth = depth + 1
          curr_val = self.minimax(new_board,new_player,my_player,
                                  new_depth,alpha,beta)
          beta = min(beta,curr_val)
          min_val = min(min_val,curr_val)
          if beta <= alpha:
            break
        # debbuging_log += "{:s} {:d}\n".format(str(actions),min_val)
        return min_val

    
  def reward(self,board,player):
    if player:
      return (board[15] - self.board[15])   - (board[7] - self.board[7]) 
    else:
      return (board[7] - self.board[7]) - (board[15] - self.board[15])

  def reflect(hole):
    if hole < 7:
      return hole + 8
    else:
      return hole - 8

  def point_well(player):
    if player:
      return 15
    else:
      return 7

  def owned(hole,player):
    if ((hole < 7 and not player) or
       (hole > 7 and player)):
      return True
    else:
      return False

  def apply_action(self,board,action,player,first_turn = False):
    new_board = board.copy()
    seeds = new_board[action]
    if not seeds:

      new_board.fill(0)
      if player:
        new_board[7] = 98
      else:
        new_board[15] = 98
      return (new_board,not player,True)

    new_board[action] = 0
    hole = action
    while seeds:
      hole +=1
      if hole == 7 and player:
        hole = 8
      elif hole == 15 and not player:
        hole = 0

      hole %=16
      new_board[hole] +=1
      seeds -= 1

    if hole != MKAgent.point_well(player) or first_turn:
        player = not player

    if np.array_equal(new_board[0:7],empty_row):
      new_board[15] = sum(new_board[8:15])
      new_board[8:15].fill(0)
      return (new_board,not player,True)

    elif np.array_equal(new_board[8:15],empty_row) :
      new_board[7] = sum(new_board[0:7])
      new_board[0:7].fill(0)
      return (new_board,not player,True)

    return (new_board,player,False)

  def read_msg(self):
    global input_log

    msg = sys.stdin.readline()
    input_log += msg
    msg = msg.replace("\n","")
    if msg == "":
      return False 
    if msg == "END":
      self.game_over = True
      return True

    cmd,args = msg.split(";",1)
    if cmd == "START":
      if args == "North":
        self.player = 0

      elif args == "South":
        self.player = 1
        self.my_turn = True

    if cmd == "CHANGE":
      move,board,turn = args.split(";")
      if turn == "YOU":
        self.my_turn = True
      elif turn == "OPP":
        self.my_turn = False  
      else:
        self.my_turn = False

      if move == "SWAP":
        self.player = not self.player
      else:
        move = int(move);
      if self.my_turn:
        board = board.split(",")
        board = list(map(lambda x: int(x),board))
        self.board = np.array(board)    
          
    if(self.my_turn):
      return True
    else:  
      return False

  def send_swap(self):
    global output_log
    sys.stdout.write("SWAP\n")
    sys.stdout.flush()
    output_log += "SWAP\n"

  def send_move(self,hole):
    global output_log
    global no_of_moves
    no_of_moves += 1
    sys.stdout.write("MOVE;{:d}\n".format(hole))
    sys.stdout.flush()
    output_log += "MOVE;{:d}\n".format(hole)

  def best_action(self):
    global debbuging_log
    global reachEnd
    action = -1
    action_range = None
    if not self.player:
      action_range = range(0,7)
    else:
      action_range = range(8,15)
    max_val = -99
    depth = 0
    # debbuging_log += "turn\n"
    for i in action_range:
      board,player,terminal = self.apply_action(self.board,i,self.player,
                                                self.first_turn)
      if terminal:
        reachEnd += 1
        depth = -1
      else:
        depth = 0
      # debbuging_log += "minimax {:d}\n".format(i)
      curr_val = self.minimax(board,player,self.player,depth)
      debbuging_log += "action value: {:d}".format(curr_val) + "\n"
      if curr_val > max_val:
        max_val = curr_val
        action = i
        
    if action > 7:
      action -= 8
    action +=1

    self.first_turn = False

    return action

      

  def do_action(self): 
    action = self.best_action()
    if(action == -1):
      log.write("No action was chosen\n")
    elif(action == 0):
      self.send_swap()
    elif(action <= 7):
      self.send_move(action)

try:
  agent = MKAgent()
  while True:
    if(agent.read_msg()):
      if(agent.game_over):
        break
      agent.do_action()
except Exception as e:
  raise e
finally:
  log.write(str(reachEnd) + "\n")
  log.write("=========OUTPUT=============\n")
  log.write(output_log)
  log.write("=========INPUT=============\n")
  log.write(input_log)
  log.write("=========DEBUG=============\n")
  log.write(debbuging_log)
  log.close()
# data_file.close()