#include "Skeleton_code.h"

Maze load_maze(const char *filename) {
    //load_maze 
    // files are loaded and  to validate existence
    // to perform two-pass validation:
    // 1. check dimensions and rectangular structure
    // 2. validate characters and positions (S/E)
    // extra impportance attached:
    // allocate memory for grid ;
    // return initialized Maze structure
}

void free_maze(Maze *maze) {
    //free_maze: for memory allocated CHECK
    // release memory allocated for grid
    // handle nested pointer structure
}

void print_maze(const Maze *maze) {
    //print maze is used to print the maze information on the screen in time
    //  grid elements iterated
    // player position is displayed as 'X' in the map
     // print maze with formatted output
}

int move_player(Maze *maze, char dir) {
    //move player
    // Calculate movement direction
    // Validate boundary conditions
    // Error Check:if the player collides with the wall
    // update and record player position.. after each step
    // print out "victory", when player reach to E
}

void game_loop(Maze maze) {
    //game loop
    // read in and handle user input commands
    // execute the movements:WSAD or receive "M" "Q" function
    // to maintain game state until player reach to exit "E"
}

int main(int argc, char *argv[]) {
    // This is the main function circulation
  //Validate command line arguments
    // load maze file

    //Initialize the game loop
    // Clean-up
    return 0;
}