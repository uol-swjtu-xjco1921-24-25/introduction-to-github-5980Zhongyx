#ifndef __SKELETON_CODE_H__
#define __SKELETON_CODE_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 100  
// Max-allowed maze dimensions
#define MIN_SIZE 5   
 // Min-allowed maze dimensions

typedef struct {
    size_t height;     // Number of rows in the maze
    size_t width;      // Number of columns in the maze
    char **grid;       // 2D array storing maze layout ('#': wall, ' ': path)
    
    int player_x;      // X-coordinate of player's current position
    int player_y;      // Y-coordinate of player's current position
    
    int exit_x;        // X-coordinate of maze exit position
    int exit_y;        // Y-coordinate of maze exit position
} Maze;

// to load maze from file and  validate structure
Maze load_maze(const char *filename);

// free allocated memory for the maze
void free_maze(Maze *maze);

// display current maze state with player position
void print_maze(const Maze *maze);

// process player movement commands
int move_player(Maze *maze, char direction);

// main game interaction loop
void game_loop(Maze maze);

#endif