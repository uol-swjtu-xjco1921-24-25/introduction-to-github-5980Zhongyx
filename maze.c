#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// primary Struct of maze
typedef struct {
    int height;
    int width;
    char **grid;
    int player_x;
    int player_y;
    int exit_x;
    int exit_y;
} Maze;


Maze generate_maze(int min_size, int max_size);//randomly generate maze
void print_maze(const Maze *maze);
int move_player(Maze *maze, char direction);
void game_loop(Maze maze);

int main() {

    srand(time(NULL));
    Maze maze = generate_maze(5, 100);

    if (maze.grid == NULL) {
        printf("Failed to generate maze.\n");
        return 1;
    }

    game_loop(maze);

    // release storage
    for (int i = 0; i < maze.height; i++) {
        free(maze.grid[i]);
    }
    free(maze.grid);

    return 0;
}

Maze generate_maze(int min_size, int max_size) {
    Maze maze = {0};

    // random size
    maze.height = min_size + rand() % (max_size - min_size + 1);
    maze.width = min_size + rand() % (max_size - min_size + 1);

    // allocate storage
    maze.grid = (char **)malloc(maze.height * sizeof(char *));
    for (int i = 0; i < maze.height; i++) {
        maze.grid[i] = (char *)malloc(maze.width * sizeof(char));
    }

    for (int i = 0; i < maze.height; i++) {
        for (int j = 0; j < maze.width; j++) {
            // wall or path
            if (rand() % 3 == 0) {
                maze.grid[i][j] = '#'; // wall
            } else {
                maze.grid[i][j] = ' '; // path
            }
        }
    }

// E and S set
    maze.player_x = 1;
    maze.player_y = 1;
    maze.exit_x = maze.height - 2;
    maze.exit_y = maze.width - 2;

    // make sure no wall in E and S 
    maze.grid[maze.player_y][maze.player_x] = 'S';
    maze.grid[maze.exit_y][maze.exit_x] = 'E';

    return maze;
}

// print the maze
void print_maze(const Maze *maze) {
    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            // print'X' current position
            if (i == maze->player_y && j == maze->player_x) {
                printf("X ");
            } else {
                printf("%c ", maze->grid[i][j]);
            }
        }
        printf("\n");
    }
}

// motivation
int move_player(Maze *maze, char direction) {
    int new_x = maze->player_x;
    int new_y = maze->player_y;

    // update : 
    switch (direction) {
        case 'W':
        case 'w':
            new_y--;
            break;
        case 'A':
        case 'a':
            new_x--;
            break;
        case 'S':
        case 's':
            new_y++;
            break;
        case 'D':
        case 'd':
            new_x++;
            break;
        default:
            return -1; // default useless input
    }

    // boundary check
    if (new_x < 0 || new_x >= maze->width || new_y < 0 || new_y >= maze->height) {
        printf("Cannot move off the edge of the map!\n");
        return -1;
    }

    // wall check
    if (maze->grid[new_y][new_x] == '#') {
        printf("Cannot move through walls!\n");
        return -1;
    }
    maze->player_x = new_x;
    maze->player_y = new_y;

    // when player reach the E 
    if (maze->grid[new_y][new_x] == 'E') {
        return 1; // end - success
    }

    return 0; 
}

// Main circulation
void game_loop(Maze maze) {
    char input;
    while (1) {
        printf("Enter a command (W/A/S/D to move, M to show map, Q to quit): ");
        scanf(" %c", &input);

        if (input == 'Q' || input == 'q') {
            printf("Game ended by user.\n");
            break;
        } else if (input == 'M' || input == 'm') {
            print_maze(&maze);
        } else {
            int result = move_player(&maze, input);
            if (result == -1) {

            } else if (result == 1) {
                printf("Congratulations! You've reached the exit!\n");
                break;
            }
        }
    }
}