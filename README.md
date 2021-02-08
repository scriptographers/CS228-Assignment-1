# Problems

## Mastermind
Mastermind is a two player game. There are `n` colors. Let `k < n` be a positive number.
  1. Player one chooses a hidden sequence of `k` colors (colors may repeat)
  2. The game proceeds iteratively as follows until player two has guessed the sequence correctly.  
      - Player two makes a guess of sequence of `k` colors
      - Player one gives feedback to player two by giving  
        - (red response) the number of correct colors in the correct positions, and
        - (white response) the number of correct colors in the wrong positions.

Play the game [here](http://www.webgamesonline.com/mastermind/)  
Create player two using a SAT solver that is tolerant to unreliable player one, i.e., sometimes player one gives wrong answer.

## Disconnect

Consider an undirected connected graph `G = (V, E)` and nodes `s,t ∈ V`   
Give a SAT encoding of removing the minimal set of edges such that `s` and `t` are not connected.
