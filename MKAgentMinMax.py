import os
import sys
import copy
import numpy as np

sys.setrecursionlimit(200000)

# bot_name = sys.argv[1]
# max_depth = int(sys.argv[2])
max_depth = 7
# log = open("log_{:s}.txt".format(bot_name),"w")
# this is what the program outputted last game
# output_log = ""
# this was the engine input from last game
# input_log = ""
# any value that might be useful to printout goes here
# debbuging_log = ""

empty_row = np.zeros(7,dtype = int)

weights = [0.244, 0.24, 0.525, 1, 1, 1]
heuristics = [0, 0, 0, 0, 0, 0]

class MKAgent(object):
  """docstring for MKAgent"""
  def __init__(self):
    # global debbuging_log

    super(MKAgent, self).__init__()
    self.player = -1
    self.board = np.array([7,7,7,7,7,7,7,0,7,7,7,7,7,7,7,0])
    self.game_over = False
    self.my_turn = False
    self.first_turn = True




  def minimax(self,board,player,
              my_player,depth = 0,
             alpha = -200,beta = 200,first_turn =  False):
    # global debbuging_log

    if depth == max_depth:
      reward = self.reward(board,my_player)
      # debbuging_log += str(actions) + " "+ str(reward) + "\n"
      # debbuging_log += "REWARD: {:d}".format(reward) + "\n"
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
        max_val = -200
        for i in action_range:
          new_board,new_player,terminal = self.apply_action(board,i,player)
          if terminal:
            new_depth = max_depth
          else:
            new_depth = depth + 1
          curr_val = self.minimax(new_board,new_player,my_player,
                                  new_depth,alpha,beta)
          max_val = max(max_val,curr_val)
          alpha = max(alpha,curr_val)
          if beta <= alpha:
            break
        # debbuging_log += "{:s} {:d}\n".format(str(actions),max_val)
        # debbuging_log += "MAX_VAL: {:d}".format(max_val) + "\n"
        return max_val
      else:
        min_val = 199
        for i in action_range:
          new_board,new_player,terminal = self.apply_action(board,i,player)
          if terminal:
            new_depth = max_depth
          else:
            new_depth = depth + 1
          curr_val = self.minimax(new_board,new_player,my_player,
                                  new_depth,alpha,beta)
          beta = min(beta,curr_val)
          min_val = min(min_val,curr_val)
          if beta <= alpha:
            break
      if(first_turn and not player):
        curr_val = self.minimax(board,not player,my_player,depth)
        # debbuging_log += "swap action value: {:d}\n".format(curr_val)
        min_val = min(min_val,curr_val)
      return min_val

  def getSeeds(self, board, player, hole):
    if player:
      return board[hole+8]
    else:
      return board[hole]

  def getSeedsOp(self, board, player, hole):
    if player:
      return board[6-hole]
    else:
      return board[14-hole]

  def isSeedable(self, board, player, hole):

    if player:
      hole += 8

    if (board[hole] == 15):
      return 1
    elif (board[hole] == 0):
      if player:
        for i in range(hole-1, 7, -1):
          if (hole-i) == self.getSeeds(board, player, i-8):
            return 1
        for i in range(14, hole, -1):
          if (board[i] > 8 and board[i] < 15):
            if (hole-i+15) == self.getSeeds(board, player, i-8):
              return 1
      else:
        for i in range(hole-1, -1, -1):
          if (hole-i) == self.getSeeds(board, player, i):
            return 1
        for i in range(6, hole, -1):
          if (board[i] > 8 and board[i] < 15):
            if(hole-i+15) == self.getSeeds(board,player,i):
              return 1

    # for i in range (hole-1, 0, -1):
    #   if ((hole - i) == self.getSeeds(board, player, i)):
    #     return 1
    #     break

    return 0

  def opposite(self, player):
    return (1 - player)


  # def reward(self,board,player):
  #   if player:
  #     return (board[15] - self.board[15])   - (board[7] - self.board[7])
  #   else:
  #     return (board[7] - self.board[7]) - (board[15] - self.board[15])

  # FINAL HEURISTIC
  def reward(self, board, player):
    eval = 0.0

    if player:
      myStore = board[15]
      opponentStore = board[7]
    else:
      myStore = board[7]
      opponentStore = board[15]

    # evaluate current position
    if ((myStore != 0.0 or opponentStore != 0.0) and myStore != opponentStore):
      if (myStore > opponentStore):
        positiveAdv = myStore
        negativeAdv = opponentStore
      else:
        positiveAdv = opponentStore
        negativeAdv = myStore

      eval = ((1.0 / positiveAdv * (positiveAdv - negativeAdv) + 1.0) * positiveAdv)
      if (opponentStore > myStore):
        eval *= -1.0

    # check how many holes I can seed
    for i in range(0, 7):
      # if (self.getSeeds(board, player, i) == 0 and (self.isSeedable(board, player, i) == 1)):
      if (self.isSeedable(board, player, i) == 1):
        eval += (self.getSeedsOp(board, player, i) / 2)

    # check how many holes will lead to extra move
    for i in range(0, 7):
      if ((7 - i) == self.getSeeds(board, player, i)):
        eval += 1.0;

    # count number of seeds on my side
    mySeeds = 0.0
    for i in range(0, 7):
      mySeeds += self.getSeeds(board, player, i)

    # count number of seeds on opponents side
    opponentSeeds = 0.0
    for i in range(0,7):
      opponentSeeds += self.getSeeds(board, self.opposite(player), i)

    # update eval with regard to seed count
    seedDiff = mySeeds - opponentSeeds
    eval += (seedDiff/2)

    # check how many holes can opponent seed
    for i in range(0, 7):
      # if (self.getSeeds(board, self.opposite(player), i) == 0 and self.isSeedable(board, self.opposite(player), i)):
      if (self.isSeedable(board, self.opposite(player), i) == 1):
        eval -= (self.getSeedsOp(board, self.opposite(player), i) / 2)

    return int(eval)

  # INITIAL HEURISTIC
  # def reward(self,board,player):
  #   if player:
  #     return (board[15] - self.board[15])   - (board[7] - self.board[7])
  #   else:
  #     return (board[7] - self.board[7]) - (board[15] - self.board[15])

  # HEURISTIC FROM PAPERS
  # def reward(self,board,player):
  #   eval_func = 0.0
  #   for i in range (0, 6):
  #     heuristics[i] = 0
  #
  #   if player:
  #     heuristics[0] = max(board[8], board[9], board[10], board[11], board[12], board[13], board[14])
  #     heuristics[1] = board[8] + board[9] + board[10] + board[11] + board[12] + board[13] + board[14]
  #     for i in range(8, 15):
  #       if (board[i] > 0):
  #         heuristics[2] += 1
  #     heuristics[3] = board[15] - self.board[15]
  #     if (board[14] > 0):
  #       heuristics[4] = 1
  #     else:
  #       heuristics[4] = 0
  #     heuristics[5] = board[7] - self.board[7]
  #
  #     for i in range(0, 5):
  #       eval_func += (weights[i] * heuristics[i])
  #     eval_func -= (weights[5] * heuristics[5])
  #
  #     return int(eval_func)
  #
  #   else:
  #     heuristics[0] = max(board[0], board[1], board[2], board[3], board[4], board[5], board[6])
  #     heuristics[1] = board[0] + board[1] + board[2] + board[3] + board[4] + board[5] + board[6]
  #     for i in range(0, 7):
  #       if (board[i] > 0):
  #         heuristics[2] += 1
  #     heuristics[3] = board[7] - self.board[7]
  #     if (board[6] > 0):
  #       heuristics[4] = 1
  #     else:
  #       heuristics[4] = 0
  #     heuristics[5] = board[15] - self.board[15]
  #
  #     for i in range(0, 5):
  #       eval_func += (weights[i] * heuristics[i])
  #     eval_func -= (weights[5] * heuristics[5])
  #
  #     return int(eval_func)

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

    if (hole < 7 and not player or
        hole < 14 and hole > 7 and player):
      if board[hole] == 1:
        well = MKAgent.point_well(player)
        if player:
          opposite = - (hole - 14)
        else:
          opposite = -(hole - 6) + 8
        board[well] += opposite
        board[opposite] = 0

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
    # global input_log

    msg = sys.stdin.readline()
    # input_log += msg
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
    # global output_log
    sys.stdout.write("SWAP\n")
    sys.stdout.flush()
    # output_log += "SWAP\n"
    self.player = not self.player

  def send_move(self,hole):
    # global output_log
    sys.stdout.write("MOVE;{:d}\n".format(hole))
    sys.stdout.flush()
    # output_log += "MOVE;{:d}\n".format(hole)

  def best_action(self):
    # global debbuging_log
    action = -1
    action_range = None
    if not self.player:
      action_range = range(0,7)
    else:
      action_range = range(8,15)
    max_val = -200
    depth = 0
    # debbuging_log += "turn\n"
    for i in action_range:
      board,player,terminal = self.apply_action(self.board,i,self.player,
                                                self.first_turn)
      if terminal:
        depth = max_depth
      else:
        depth = 0
      curr_val = self.minimax(board,player,self.player,depth, first_turn = self.first_turn)
      # debbuging_log += "action {:d} value: {:d}\n".format(i+1,curr_val)
      if curr_val > max_val:
        max_val = curr_val
        action = i

    if (self.board[action] == 0):
      for i in action_range:
        if (self.board[i] != 0):
          action = i
          break

    if action > 7:
      action -= 8
    action += 1

    if(self.first_turn and not self.player):
      curr_val = self.minimax(board,self.player,not self.player,depth)
      # debbuging_log += "swap action value: {:d}\n".format(curr_val)
      if curr_val > max_val:
        max_val = curr_val
        action = 0

    self.first_turn = False

    # debbuging_log += "FINAL action value: {:d}".format(max_val) + "\n"
    # debbuging_log += "FINAL ACTION: {:d}".format(action) + "\n"

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
# finally:
  # log.write("=========OUTPUT=============\n")
  # log.write(output_log)
  # log.write("=========INPUT=============\n")
  # log.write(input_log)
  # log.write("=========DEBUG=============\n")
  # log.write(debbuging_log)
  # log.close()
# data_file.close()
