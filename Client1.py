import random
import socket
import time

import chess
import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()
MainScreen = pygame.display.set_mode((560, 600))

#Fonts
HeadingFont = pygame.font.SysFont('freesanbold.ttf', 50)
BodyFont = pygame.font.SysFont('freesanbold.ttf', 20)

#Colours
ColourA = (168, 174, 218)  #Light lavender
ColourB = (0, 0, 0)  #Black
ColourC = (255, 255, 255)  #White


# function to handle the creation of menu objects and draw them on the screen 
class MenuButton:

  # initialises the object
  def __init__(self, StartArea, RectangleArea, BorderBool, Text, Font,
               SendLocation):
    self.StartArea = StartArea
    self.RectangleArea = pygame.Rect(RectangleArea)
    self.BorderBool = BorderBool
    self.Text = Text

    self.Font = Font
    self.SendLocation = SendLocation

  # draws the object on the screen
  def Draw(self):
    if self.BorderBool:
      pygame.draw.rect(MainScreen, ColourA, self.RectangleArea, 2)
    self.DrawnText = (self.Font).render(self.Text, True, ColourA)
    self.Container = self.DrawnText.get_rect()
    self.Container.center = (self.StartArea)
    pygame.draw.rect(MainScreen, [0,0,0], pygame.Rect(self.RectangleArea))
    MainScreen.blit(self.DrawnText, self.Container)

  # if a click is detected, it will run this
  def Click_Handler(self):
    exec(self.SendLocation)

  # detects if there is a click within the objects area
  def Check_Click(self, mousepos):
    Rect = self.RectangleArea
    if (Rect).collidepoint(mousepos):
      return True
    else:
      return False


#global variables
square_size = 70
global BotDifficulty

#Back button
back_button = MenuButton(StartArea=(40, 30),
                         RectangleArea=(20, 20, 40, 20),
                         BorderBool=True,
                         Text="Back",
                         Font=BodyFont,
                         SendLocation="MainMenuWindow()")

back_button_playing = MenuButton(StartArea=(280, 580),
                         RectangleArea=(0, 560, 560, 40),
                         BorderBool=True,
                         Text="Back to main menu",
                         Font=BodyFont,
                         SendLocation="MainMenuWindow()")


#Draw the board
def DrawBoard(board):
  light_colour = (238, 238, 210)
  dark_colour = (119, 148, 85)

  #create the coloured  squares
  for row in range(8):
    for col in range(8):
      x = col * square_size
      y = row * square_size
      square_colour = light_colour if (row + col) % 2 == 0 else dark_colour

      pygame.draw.rect(MainScreen, square_colour,
                       (x, y, square_size, square_size))

  #Add the pieces from the pychess board
  for row in range(8):
    for col in range(8):
      x = col * square_size
      y = (7 - row) * square_size

      piece = board.piece_at(chess.square(col, row))
      if piece is not None:
        if piece.color == chess.WHITE:
          piece_symbol = piece.symbol().lower()
          piece_image = pygame.image.load(f"images/w_{piece_symbol}.png")
          piece_image = pygame.transform.scale(piece_image, (70, 70))
        else:
          piece_symbol = piece.symbol()
          piece_image = pygame.image.load(f"images/b_{piece_symbol}.png")
          piece_image = pygame.transform.scale(piece_image, (70, 70))
        MainScreen.blit(piece_image, (x, y))

  back_button_playing.Draw()


#Find mouse coordinates on board
def BoardCoords():
  mouse_x, mouse_y = pygame.mouse.get_pos()
  col = (mouse_x // square_size)
  row = (mouse_y // square_size)
  return col, row


#convert board square into chess notation
def GetSquare(col, row):
  XAxis = "a", "b", "c", "d", "e", "f", "g", "h"
  YAxis = "8", "7", "6", "5", "4", "3", "2", "1"
  letter = str(XAxis[col])
  number = str(YAxis[row])
  square = letter + number
  return square

# function to create the notation in the correct format
def CreateNotation(piece1, piece2, square1, square2, board):

  if piece1 == None:
      piece1 = ""

  if piece2 == None:
      piece2 = ""

  if square1 == None:
      square1 = ""

  if square2 == None:
      square2 = ""

  print(f"{piece1} = Piece1   {piece2} = Piece2")
  print(f"{square1} = Square1   {square2} = Square2")

  Notation = ""
  column = square1[0].lower()
  row = square1[1]
  symbol = str(piece1).upper()
  piece1 = str(piece1)

  if piece2 == "":
    pass
  else:
    piece2 = str(piece2)

  square1 = str(square1)
  square2 = str(square2)


  # moving a pawn and not taking a piece
  if symbol == "P" and piece2 == "":
    Notation = square2

  # moving a pawn and taking a piece
  elif symbol == "P" and piece2 != "":
    Notation = column + "x" + square2

  # moving any other piece
  else:
    Notation += symbol
    if piece2 != "":
      Notation += "x" + square2
    else:
      Notation += square2

  # handles pawn promotion to queen automatically
  if symbol == "P" and row == 7: 
    Notation += "=Q"

  # handles if the board is in check
  try:
    board.push_san(Notation)
    board.pop()
  except:
    Notation += "+"

  if "Kg1" in Notation:
    Notation = "0-0"

  if "Kc1" in Notation:
    Notation = "0-0-0 "
  print(Notation)
  return Notation


#Get the users move
def UserMove(board):

  global client_socket

  # set all squares and pieces to be empty
  square1 = None
  square2 = None
  piece1 = None
  piece2 = None

  movemade = False

  # while the user hasnt made a valid move:
  while not movemade:
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:

        mousepos = pygame.mouse.get_pos()
        # if currently playing multiplayer, close the connection when the user presses to go back to the main menu
        if back_button_playing.Check_Click(mousepos):
         try:
            client_socket.close()

         except:
             pass

         back_button_playing.Click_Handler()
         break
        # get the coordinates of a clicked square
        col, row = BoardCoords()
        square = GetSquare(col, row)

        # if square1 is empty, store the clicked square there, also save the piece on that square
        if square1 is None:
          square1 = square
          piece1 = (board.piece_at(chess.parse_square(square1.lower())))
          print(piece1)

        # if square1 isnt empty, repeat same process for square2 and piece2
        else:
          square2 = square
          piece2 = (board.piece_at(chess.parse_square(square2.lower())))

          print(board.legal_moves)

          # use the create notation function to get proper notation 
          move = CreateNotation(piece1, piece2, square1, square2, board)

          # reset all variables
          movemade = True
          square1 = None
          square2 = None
          piece1 = None
          piece2 = None

          print(f"Users move is {move}")

          # test if the move is valid
          try:
            board.push_san(move)
            board.pop()
            return move

          except:
            movemade = False
            print("MOVE INVALID - RETAKING INPUT")


def AIPlayer(board):
  global BotDifficulty

  if BotDifficulty == "Easy":
    move = FindBestMove(board, 1)
    board.push(move)

  elif BotDifficulty == "Medium":
    move = FindBestMove(board, 2)
    board.push(move)

  elif BotDifficulty == "Hard":
    move = FindBestMove(board, 3)
    board.push(move)

  else:
    print("No difficulty set")


# return a board evaluation score
def EvaluateBoard(board):
  # list pieces and their values

  PieceValues = [0, 100, 200, 200, 300, 1000, 5000]
  # NULL, pawn, knight, bishop, rook, queen, king

  # location tables to decide which square each piece wants to be on
  pawntable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    1,  1,  1,  2,  2,  1,  1,  1,
    -2, -2, -2, -2, -2, -2, -2, -2,
    -2, -2, -2, -2, -2, -2, -2, -2,
    1,  1,  1,  1,  1,  1,  1,  1,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    0,  0,  0,  0,  0,  0,  0,  0,
  ]

  knightstable = [
    -5,  -4,  -3,  -3,  -3,  -3,  -4,  -5,
    -4,  -2,  0,   0.5, 0.5,  0,   -2,  -4,
    -3,  0.5,  1,   1, 1,  1,   0.5, -3,
    -3,  0,   1,  1,   1,   1, 0,   -3,
    -3,  0.5,  1,  1,   1,   1, 0.5, -3,
    -3,  0,   1,   1, 1,  1,   0,   -3,
    -4,  -2,  0,   0.5, 0.5,  0,   -2,  -4,
    -5,  -4,  -3,  -3,  -3,  -3,  -4,  -5,
  ]

  bishopstable = [
    -2,  -1,  -1,  -1,  -1,  -1,  -1,  -2,
    -1,   0,   0,   0,   0,   0,   0,  -1,
    -1,   0.5,  0.5,  0.5,  0.5,  0.5,  0.5, -1,
    -1,   0,   0.5,  1,   1,   0.5,  0,  -1,
    -1,   0,   0.5,  1,   1,   0.5,  0,  -1,
    -1,   0,   0.5,  0.5,  0.5,  0.5,  0,  -1,
    -1,   0,   0,   0,   0,   0,   0,  -1,
    -2,  -1,  -1,  -1,  -1,  -1,  -1,  -2,
  ]

  rookstable = [
    0,   0,   0,   0,   0,   0,   0,   0,
    0.5, 1,   1,   1,   1,   1,   1,   0.5,
    -0.5, 0,   0,   0,   0,   0,   0,  -0.5,
    -0.5, 0,   0,   0,   0,   0,   0,  -0.5,
    -0.5, 0,   0,   0,   0,   0,   0,  -0.5,
    -0.5, 0,   0,   0,   0,   0,   0,  -0.5,
    -0.5, 0,   0,   0,   0,   0,   0,  -0.5,
    0,   0,   0,   0.5, 0.5,  0,   0,   0,
  ]

  queenstable = [
    -2,  -1,  -1,  -0.5, -0.5, -1,  -1,  -2,
    -1,   0,   0,   0,   0,   0,   0,  -1,
    -1,   0.5,  0.5,  0.5,  0.5,  0.5,  0.5, -1,
    -0.5, 0,   0.5,  0.5,  0.5,  0.5,  0,   -0.5,
    0,    0,   0.5,  0.5,  0.5,  0.5,  0,   0,
    -1,   0,   0.5,  0.5,  0.5,  0.5,  0,   -1,
    -1,   0,   0,   0,   0,   0,   0,   -1,
    -2,  -1,  -1,  -0.5, -0.5, -1,  -1,  -2,
  ]

  kingstable = [
    2,   3,   1,   0,   0,   1,   3,   2,
    2,   2,   0,   0,   0,   0,   2,   2,
    -1,  -2,  -2,  -2,  -2,  -2,  -2,  -1,
    -2,  -3,  -3,  -4,  -4,  -3,  -3,  -2,
    -3,  -4,  -4,  -5,  -5,  -4,  -4,  -3,
    -3,  -4,  -4,  -5,  -5,  -4,  -4,  -3,
    -3,  -4,  -4,  -5,  -5,  -4,  -4,  -3,
    -2,  -3,  -3,  -4,  -4,  -3,  -3,  -2,
  ]


  # add each piece value to a score variable
  score = 0
  for piece in board.piece_map().values():
    Value = PieceValues[piece.piece_type]
    if piece.color == chess.BLACK:
      score += Value
    else:
      score -= Value

  # add each pieces location value to score
  for i in range(64):
    piece = board.piece_at(i)
    if piece is not None:
      piece_type = piece.piece_type
      piece_color = piece.color
      if piece_color == chess.WHITE:
        if piece_type == chess.PAWN:
          score -= pawntable[i]
        elif piece_type == chess.KNIGHT:
          score -= knightstable[i]
        elif piece_type == chess.BISHOP:
          score -= bishopstable[i]
        elif piece_type == chess.ROOK:
          score -= rookstable[i]
        elif piece_type == chess.QUEEN:
          score -= queenstable[i]
        elif piece_type == chess.KING:
          score -= kingstable[i]
      else:
        if piece_type == chess.PAWN:
          score += pawntable[i]
        elif piece_type == chess.KNIGHT:
          score += knightstable[i]
        elif piece_type == chess.BISHOP:
          score += bishopstable[i]
        elif piece_type == chess.ROOK:
          score += rookstable[i]
        elif piece_type == chess.QUEEN:
          score += queenstable[i]
        elif piece_type == chess.KING:
          score += kingstable[i]

  return score


# the minimax algorithm to foresee future moves and make the best one for the maximiser
def MinimaxAlphaBeta(board, foresight, IsMaximiser, Alpha, Beta):

  # if foresight is 0, return the current board state either directly or down through the recursion
  if foresight == 0:
    return EvaluateBoard(board)

  # what to do if its not the AIs turn
  if not IsMaximiser:
    # set the max evaluation so it will always have a move to make
    MaxEvaluation = -10000
    # try each possible move it can make using recursion to branch down each tree until foresight is 0
    for move in board.legal_moves:
      board.push(move)
      Evaluation = MinimaxAlphaBeta(board, foresight-1, False, Alpha, Beta)
      board.pop()
      MaxEvaluation = max(MaxEvaluation, Evaluation)
      Beta = min(Beta, Evaluation)

      # stop running the current tree if it finds a bad move
      if Beta < Alpha:
        break
    return MaxEvaluation

  # what to do if it is the AIs turn (Mostly the same code as above)
  else:
    MinEvaluation = 10000
    for move in board.legal_moves:
      board.push(move)
      Evaluation = MinimaxAlphaBeta(board, foresight-1, True, Alpha, Beta)
      board.pop()
      MinEvaluation = min(MinEvaluation, Evaluation)
      Alpha = max(Alpha, Evaluation)
      if Beta < Alpha:
        break
    return MinEvaluation


def FindBestMove(board, foresight):

  # set the bestevaluation depending on the turn
  BestMove = ""
  if board.turn == chess.BLACK:
    BestEvaluation = -10000
  else:
    BestEvaluation = 10000

  # initialise alpha and beta as very small or very large numbers
  Beta = 10000
  Alpha = -10000

  # for each possible move, use minimax to evaluate each of its branches
  for move in list(board.legal_moves):
    board.push(move)
    BoardEvaluation = MinimaxAlphaBeta(board, foresight, True, Alpha, Beta)
    board.pop()

    # save the best moves
    if board.turn == chess.BLACK:
      if BoardEvaluation > BestEvaluation:
        BestEvaluation = BoardEvaluation
        BestMove = move
    else:
      if board.turn == chess.WHITE:
        if BoardEvaluation < BestEvaluation:
          BestEvaluation = BoardEvaluation
          BestMove = move

  print(f"Best move is {BestMove}")
  return BestMove




# use the notification window function to let the player know when they win/lose/draw
def BoardState(board, IsMultiplayer):
  WaitTime = 3
  if IsMultiplayer:
    if board.is_checkmate():
        if board.turn == chess.WHITE:
          time.sleep(WaitTime)
          print("Black wins!")
          NotificationWindow("Black wins!", "Seems like black has won this game!")
        else:
            time.sleep(WaitTime)
            print("White wins!")
            NotificationWindow("White wins!", "Seems like white has won this game!")
    elif board.is_stalemate():
        time.sleep(WaitTime)
        print("Its a draw!")
        NotificationWindow("Stalemate!", "Hmmm, seems like a draw this time...")
    else:
        pass

  else:
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            time.sleep(WaitTime)
            print("Black wins!")
            NotificationWindow("AI wins!", "Better luck next time :(")
        else:
            time.sleep(WaitTime)
            print("White wins!")
            NotificationWindow("You win!", "Good job! Betcha cant win twice in a row!")
    elif board.is_stalemate():
        time.sleep(WaitTime)
        print("Its a draw!")
        NotificationWindow("Stalemate!", "Hmmm, seems like a draw this time...")
    else:
        pass



def MainMenuWindow():

  game_title = MenuButton(StartArea=(280, 100),
                          RectangleArea=(0, 0, 0, 0),
                          BorderBool=False,
                          Text="Welcome to pychess!",
                          Font=HeadingFont,
                          SendLocation="NULL")

  single_button = MenuButton(StartArea=(280, 150),
                             RectangleArea=(220, 130, 120, 40),
                             BorderBool=True,
                             Text="Battle the bot!",
                             Font=BodyFont,
                             SendLocation="SingleMenu()")
  puzzle_button = MenuButton(StartArea=(280, 200),
                             RectangleArea=(220, 180, 120, 40),
                             BorderBool=True,
                             Text="Tricky puzzles!",
                             Font=BodyFont,
                             SendLocation="PuzzleMenu()")
  multiplayer_button = MenuButton(StartArea=(280, 250),
                                  RectangleArea=(220, 230, 120, 40),
                                  BorderBool=True,
                                  Text="Play a person!",
                                  Font=BodyFont,
                                  SendLocation="MultiMenu()")

  RunMenu = True

  while RunMenu:
    #background colour
    MainScreen.fill((0, 70, 0))
    #add text
    game_title.Draw()
    single_button.Draw()
    puzzle_button.Draw()
    multiplayer_button.Draw()

    mousepos = pygame.mouse.get_pos()
    for i in pygame.event.get():
      if i.type == pygame.MOUSEBUTTONDOWN:
        if game_title.Check_Click(mousepos):
          RunMenu = False
          game_title.Click_Handler()
        if single_button.Check_Click(mousepos):
          RunMenu = False
          single_button.Click_Handler()
        if puzzle_button.Check_Click(mousepos):
          RunMenu = False
          puzzle_button.Click_Handler()
        if multiplayer_button.Check_Click(mousepos):
          RunMenu = False
          multiplayer_button.Click_Handler()

    #update the display
    pygame.display.update()


def SingleMenu():

  # Initialise objects

  difficulty_title = MenuButton(StartArea=(280, 100),
                                RectangleArea=(0, 0, 0, 0),
                                BorderBool=False,
                                Text="Choose a difficulty!",
                                Font=HeadingFont,
                                SendLocation="NULL")

  easy_button = MenuButton(StartArea=(280, 150),
                           RectangleArea=(220, 130, 120, 40),
                           BorderBool=True,
                           Text="Easy",
                           Font=BodyFont,
                           SendLocation="PlayingAI()")

  medium_button = MenuButton(StartArea=(280, 200),
                             RectangleArea=(220, 180, 120, 40),
                             BorderBool=True,
                             Text="Medium",
                             Font=BodyFont,
                             SendLocation="PlayingAI()")

  hard_button = MenuButton(StartArea=(280, 250),
                           RectangleArea=(220, 230, 120, 40),
                           BorderBool=True,
                           Text="Hard",
                           Font=BodyFont,
                           SendLocation="PlayingAI()")

  RunMenu = True

  # loop the menu

  while RunMenu:
    # background colour
    MainScreen.fill((0, 70, 0))
    # draw text
    difficulty_title.Draw()
    back_button.Draw()
    easy_button.Draw()
    medium_button.Draw()
    hard_button.Draw()
    mousepos = pygame.mouse.get_pos()
    for i in pygame.event.get():
      if i.type == pygame.MOUSEBUTTONDOWN:
        global BotDifficulty

        if easy_button.Check_Click(mousepos):
          BotDifficulty = "Easy"
          easy_button.Click_Handler()

        if medium_button.Check_Click(mousepos):
          BotDifficulty = "Medium"
          medium_button.Click_Handler()

        if hard_button.Check_Click(mousepos):
          BotDifficulty = "Hard"
          hard_button.Click_Handler()

        if back_button.Check_Click(mousepos):
          back_button.Click_Handler()

    pygame.display.update()


def PuzzleMenu():

  global BotDifficulty

  # Initialise objects

  difficulty_title = MenuButton(StartArea=(280, 100),
                                RectangleArea=(0, 0, 0, 0),
                                BorderBool=False,
                                Text="Choose a difficulty!",
                                Font=HeadingFont,
                                SendLocation="NULL")

  easy_button = MenuButton(StartArea=(280, 150),
                           RectangleArea=(220, 130, 120, 40),
                           BorderBool=True,
                           Text="Easy",
                           Font=BodyFont,
                           SendLocation="PlayingPuzzle()")

  medium_button = MenuButton(StartArea=(280, 200),
                             RectangleArea=(220, 180, 120, 40),
                             BorderBool=True,
                             Text="Medium",
                             Font=BodyFont,
                             SendLocation="PlayingPuzzle()")

  hard_button = MenuButton(StartArea=(280, 250),
                           RectangleArea=(220, 230, 120, 40),
                           BorderBool=True,
                           Text="Hard",
                           Font=BodyFont,
                           SendLocation="PlayingPuzzle()")

  RunMenu = True

  # loop the menu

  while RunMenu:
    # background colour
    MainScreen.fill((0, 70, 0))
    # draw text
    difficulty_title.Draw()
    back_button.Draw()
    easy_button.Draw()
    medium_button.Draw()
    hard_button.Draw()

    mousepos = pygame.mouse.get_pos()
    for i in pygame.event.get():
      if i.type == pygame.MOUSEBUTTONDOWN:
        global BotDifficulty
        if easy_button.Check_Click(mousepos):
          BotDifficulty = "Easy"
          easy_button.Click_Handler()

        if medium_button.Check_Click(mousepos):
          BotDifficulty = "Medium"
          medium_button.Click_Handler()

        if hard_button.Check_Click(mousepos):
          BotDifficulty = "Hard"
          hard_button.Click_Handler()

        if back_button.Check_Click(mousepos):
          back_button.Click_Handler()

    pygame.display.update()

# multiplayer code
def MultiMenu():

  # set up the board, client socket and connect to the server
  board = chess.Board()
  host = '127.0.0.1'
  port = 5559
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    client_socket.connect((host, port))

  # error handling if the server isnt available
  except:
    NotificationWindow("Cant connect", "Sorry, the server seems to be unavailable at the moment. Please try again later!")

  # receive the colour of the clients pieces from the server
  # boolean variable, white is True and black is False
  Colour = bool(int(client_socket.recv(1024)))

  # function to handle the receiving and making of a move from the server
  def ReceiveMove():
    Move = client_socket.recv(1024).decode('utf-8')
    board.push_san(Move)
    DrawBoard(board)
    pygame.display.update()

  # function to send a move to the server
  def SendMove(Move):
    client_socket.send(Move.encode('utf-8'))


  Playing = True
  TurnCount = 0

  DrawBoard(board)
  pygame.display.update()


  while Playing:
    # if its the first turn and its white to move, send the move before waiting to receive
    if TurnCount == 0 and Colour == True:
        Move = UserMove(board)
        SendMove(Move)

    ReceiveMove()

    # analyse the current board state
    CurrentBoardState = BoardState(board, True)
    if CurrentBoardState == True:
        Playing = False

    # if the user is the same colour as the boards turn, let them make and send a move
    if board.turn == Colour:
        Move = UserMove(board)
        SendMove(Move)


    TurnCount += 1

# function to handle the displaying of notifications to the user
def NotificationWindow(Title, Text):

    MainScreen.fill((0, 0, 0))

    heading = MenuButton(StartArea=(280, 100),
                          RectangleArea=(0, 0, 0, 0),
                          BorderBool=False,
                          Text=f"{Title}",
                          Font=HeadingFont,
                          SendLocation="NULL")

    text = MenuButton(StartArea=(280, 200),
                          RectangleArea=(0, 0, 0, 0),
                          BorderBool=True,
                          Text=f"{Text}",
                          Font=BodyFont,
                          SendLocation="NULL")

    heading.Draw()
    text.Draw()
    back_button_playing.Draw()

    pygame.display.update()

    while True:
        for i in pygame.event.get():
            if i.type == pygame.MOUSEBUTTONDOWN:

                mousepos = pygame.mouse.get_pos()

                if back_button_playing.Check_Click(mousepos):
                    back_button_playing.Click_Handler()



# puzzle code
def PlayingPuzzle():

  # create a random board
  board = chess.Board()
  StartMoves = [6,10,14,18,22,26]
  for i in range(random.choice(StartMoves)):
    board.push(random.choice(list(board.legal_moves)))

  # set up the board
  DrawBoard(board)
  pygame.display.update()
  MoveFound = False

  # find the best move and make it, saving the state of the board

  BestMove = FindBestMove(board, 2)

  board.push(BestMove)
  boardPuzzleMove = board
  board.pop()

  print(f"Best puzzle move is: {str(BestMove)}")

  # collect the users move, if their move makes the board state match the state the AI made, they beat the puzzle
  while not MoveFound:
    UsersMove = UserMove(board)

    board.push(board.parse_san(UsersMove))
    boardUserMove = board
    board.pop()

    if boardUserMove == boardPuzzleMove:
      MoveFound = True

  board.push(board.parse_san(UsersMove))
  DrawBoard(board)
  pygame.display.update()
  time.sleep(1)
  print("BEST MOVE FOUND :D")
  NotificationWindow("Great job!", "Goob job! You managed to beat one of the puzzles!")



# code to handle playing th AI
def PlayingAI():

  # initialise necessary variables
  multi = False
  GameRunning = True
  board = chess.Board()


  while GameRunning:
    # draw and update the board
    DrawBoard(board)
    pygame.display.update()
    print(board)

    MoveMade = False
    while MoveMade is False:

      # make the users move

      UsersMove = UserMove(board)
      print("############")
      print(UsersMove)
      print(board.legal_moves)
      print("############")
      try:
        board.push_san(UsersMove)
        MoveMade = True
      except:
        print("Cant make move!")


    DrawBoard(board)
    pygame.display.update()
    
    # check the board state
    BoardState(board, False)

    DrawBoard(board)
    pygame.display.update()

    # make the AIs move
    AIPlayer(board)

    DrawBoard(board)
    pygame.display.update()
    print(board)

    BoardState(board, False)

    print("AI MOVE DONE")

# start the program
MainMenuWindow()

