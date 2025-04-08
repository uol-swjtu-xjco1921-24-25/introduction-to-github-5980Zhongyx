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

Maze generate_maze(int min_size, int max_size);
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

    // Random size
    maze.height = min_size + rand() % (max_size - min_size + 1);
    maze.width = min_size + rand() % (max_size - min_size + 1);

    // Allocate storage
    maze.grid = (char **)malloc(maze.height * sizeof(char *));
    for (int i = 0; i < maze.height; i++) {
        maze.grid[i] = (char *)malloc(maze.width * sizeof(char));
    }

    // Initialize the maze with walls
    for (int i = 0; i < maze.height; i++) {
        for (int j = 0; j < maze.width; j++) {
            maze.grid[i][j] = '#'; // wall
        }
    }

    // Set the player's starting position
    maze.player_x = 1;
    maze.player_y = 1;
    maze.grid[maze.player_y][maze.player_x] = 'S';

    // Set the exit position
    maze.exit_x = maze.width - 2;
    maze.exit_y = maze.height - 2;
    maze.grid[maze.exit_y][maze.exit_x] = 'E';

    // Directions: up, right, down, left
    int dx[] = {0, 1, 0, -1};
    int dy[] = {-1, 0, 1, 0};

    // Use DFS to generate a path from start to exit
    int **visited = (int **)malloc(maze.height * sizeof(int *));
    for (int i = 0; i < maze.height; i++) {
        visited[i] = (int *)malloc(maze.width * sizeof(int));
        for (int j = 0; j < maze.width; j++) {
            visited[i][j] = 0;
        }
    }

    // Stack for DFS
    int *stack = (int *)malloc(maze.height * maze.width * 2 * sizeof(int));
    int top = -1;
    stack[++top] = maze.player_y;
    stack[++top] = maze.player_x;
    visited[maze.player_y][maze.player_x] = 1;

    while (top >= 0) {
        int current_y = stack[top--];
        int current_x = stack[top--];

        // Shuffle directions to increase randomness
        for (int i = 0; i < 4; i++) {
            int j = rand() % 4;
            int temp = dx[i];
            dx[i] = dx[j];
            dx[j] = temp;
            temp = dy[i];
            dy[i] = dy[j];
            dy[j] = temp;
        }

        // Check all four directions
        for (int i = 0; i < 4; i++) {
            int new_y = current_y + 2 * dy[i];
            int new_x = current_x + 2 * dx[i];

            if (new_y >= 0 && new_y < maze.height && new_x >= 0 && new_x < maze.width && !visited[new_y][new_x]) {
                // Carve a path
                int mid_y = current_y + dy[i];
                int mid_x = current_x + dx[i];
                maze.grid[mid_y][mid_x] = ' ';
                maze.grid[new_y][new_x] = ' ';
                visited[new_y][new_x] = 1;
                stack[++top] = new_y;
                stack[++top] = new_x;

                // Check if we reached the exit
                if (new_y == maze.exit_y && new_x == maze.exit_x) {
                    break;
                }
            }
        }
    }

    // Ensure there is a path from start to exit
    int current_y = maze.player_y;
    int current_x = maze.player_x;
    while (current_y != maze.exit_y || current_x != maze.exit_x) {
        for (int i = 0; i < 4; i++) {
            int new_y = current_y + dy[i];
            int new_x = current_x + dx[i];
            if (new_y >= 0 && new_y < maze.height && new_x >= 0 && new_x < maze.width) {
                if (maze.grid[new_y][new_x] == '#') {
                    maze.grid[new_y][new_x] = ' ';
                }
                current_y = new_y;
                current_x = new_x;
                break;
            }
        }
    }

    // Free dynamically allocated memory
    for (int i = 0; i < maze.height; i++) {
        free(visited[i]);
    }
    free(visited);
    free(stack);

    return maze;
}

// Print the maze
void print_maze(const Maze *maze) {
    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            // Print 'X' for current position
            if (i == maze->player_y && j == maze->player_x) {
                printf("X ");
            } else {
                printf("%c ", maze->grid[i][j]);
            }
        }
        printf("\n");
    }
}

// Move player
int move_player(Maze *maze, char direction) {
    int new_x = maze->player_x;
    int new_y = maze->player_y;

    // Update position:
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
            return -1; // Default invalid input
    }

    // Boundary check
    if (new_x < 0 || new_x >= maze->width || new_y < 0 || new_y >= maze->height) {
        printf("Cannot move off the edge of the map!\n");
        return -1;
    }

    // Wall check
    if (maze->grid[new_y][new_x] == '#') {
        printf("Cannot move through walls!\n");
        return -1;
    }
    maze->player_x = new_x;
    maze->player_y = new_y;

    // Check if player reached the exit
    if (maze->grid[new_y][new_x] == 'E') {
        return 1; // End - success
    }

    return 0; 
}

// Main circulation
void game_loop(Maze maze) {
    char input;
    while (1) {
        printf("Enter a command (W/A/S/D to move, M to show map, Q to quit): ");
        if (scanf(" %c", &input) != 1) {
            printf("Error reading input.\n");
            break;
        }

        printf("Received input: %c\n", input); // Debug information

        if (input == 'Q' || input == 'q') {
            printf("Game ended by user.\n");
            break;
        } else if (input == 'M' || input == 'm') {
            print_maze(&maze);
        } else {
            int result = move_player(&maze, input);
            if (result == -1) {
                printf("Invalid move.\n"); // Debug information
            } else if (result == 1) {
                printf("Congratulations! You've reached the exit!\n");
                break;
            }
        }
    }
}
