#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_SIZE 100
#define MIN_SIZE 5

typedef struct {
    int height;
    int width;
    char **grid;
    int player_x;
    int player_y;
    int exit_x;
    int exit_y;
} Maze;

Maze generate_maze();
void print_maze(const Maze *maze);
int move_player(Maze *maze, char direction);
void game_loop(Maze maze);

int main() {
    srand(time(NULL));
    Maze maze = generate_maze();

    if (maze.grid == NULL) {
        printf("Failed to generate maze.\n");
        return 1;
    }

    game_loop(maze);

    // Free allocated memory
    for (int i = 0; i < maze.height; i++) {
        free(maze.grid[i]);
    }
    free(maze.grid);

    return 0;
}

// Generate maze using DFS algorithm
Maze generate_maze() {
    Maze maze = {0};
    int dx[] = {0, 1, 0, -1};
    int dy[] = {-1, 0, 1, 0};

    // Randomize maze dimensions
    maze.height = MIN_SIZE + rand() % (MAX_SIZE - MIN_SIZE + 1);
    maze.width = MIN_SIZE + rand() % (MAX_SIZE - MIN_SIZE + 1);

    // Allocate memory for grid
    maze.grid = (char **)malloc(maze.height * sizeof(char *));
    for (int i = 0; i < maze.height; i++) {
        maze.grid[i] = (char *)malloc(maze.width * sizeof(char));
        memset(maze.grid[i], '#', maze.width); // Initialize with walls
    }

    // Set starting position
    maze.player_x = 1;
    maze.player_y = 1;
    maze.grid[maze.player_y][maze.player_x] = 'S';

    // Initialize DFS components
    int **visited = (int **)malloc(maze.height * sizeof(int *));
    for (int i = 0; i < maze.height; i++) {
        visited[i] = (int *)malloc(maze.width * sizeof(int));
        memset(visited[i], 0, maze.width * sizeof(int));
    }

    // DFS stack operations
    int *stack = (int *)malloc(maze.height * maze.width * 2 * sizeof(int));
    int top = -1;
    stack[++top] = maze.player_y;
    stack[++top] = maze.player_x;
    visited[maze.player_y][maze.player_x] = 1;

    // Generate paths using DFS
    while (top >= 0) {
        int current_y = stack[top--];
        int current_x = stack[top--];

        // Randomize direction order
        for (int i = 0; i < 4; i++) {
            int j = rand() % 4;
            int temp = dx[i];
            dx[i] = dx[j];
            dx[j] = temp;
            temp = dy[i];
            dy[i] = dy[j];
            dy[j] = temp;
        }

        // Explore directions
        for (int i = 0; i < 4; i++) {
            int new_y = current_y + 2 * dy[i];
            int new_x = current_x + 2 * dx[i];

            if (new_y >= 0 && new_y < maze.height && 
                new_x >= 0 && new_x < maze.width && 
                !visited[new_y][new_x]) {
                
                // Create path
                int mid_y = current_y + dy[i];
                int mid_x = current_x + dx[i];
                maze.grid[mid_y][mid_x] = ' ';
                maze.grid[new_y][new_x] = ' ';
                visited[new_y][new_x] = 1;

                // Push to stack
                stack[++top] = new_y;
                stack[++top] = new_x;
            }
        }
    }

    // Dynamically set exit position
    int exit_found = 0;
    for (int attempt = 0; attempt < 100; attempt++) {
        int y = rand() % maze.height;
        int x = rand() % maze.width;
        if (visited[y][x] && (y != maze.player_y || x != maze.player_x)) {
            maze.exit_y = y;
            maze.exit_x = x;
            exit_found = 1;
            break;
        }
    }
    if (!exit_found) {  // Fallback position
        maze.exit_y = maze.height - 2;
        maze.exit_x = maze.width - 2;
    }
    maze.grid[maze.exit_y][maze.exit_x] = 'E';

    // Force connection between start and exit
    int cy = maze.player_y, cx = maze.player_x;
    while (cy != maze.exit_y || cx != maze.exit_x) {
        int dir = rand() % 4;
        int ny = cy + dy[dir];
        int nx = cx + dx[dir];
        if (ny >= 0 && ny < maze.height && nx >= 0 && nx < maze.width) {
            maze.grid[ny][nx] = ' ';
            cy = ny;
            cx = nx;
        }
    }

    // Ensure start/exit markers are preserved
    maze.grid[maze.player_y][maze.player_x] = 'S';
    maze.grid[maze.exit_y][maze.exit_x] = 'E';

    // Cleanup memory
    for (int i = 0; i < maze.height; i++) free(visited[i]);
    free(visited);
    free(stack);

    return maze;
}

// Print maze with player position marked as 'X'
void print_maze(const Maze *maze) {
    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            printf("%c ", (i == maze->player_y && j == maze->player_x) ? 'X' : maze->grid[i][j]);
        }
        printf("\n");
    }
}

// Handle player movement
int move_player(Maze *maze, char dir) {
    int dx = 0, dy = 0;
    switch (dir) {
        case 'W': case 'w': dy = -1; break;
        case 'S': case 's': dy = 1; break;
        case 'A': case 'a': dx = -1; break;
        case 'D': case 'd': dx = 1; break;
        default: return -1; // Invalid input
    }

    int new_x = maze->player_x + dx;
    int new_y = maze->player_y + dy;

    // Boundary check
    if (new_x < 0 || new_x >= maze->width || new_y < 0 || new_y >= maze->height) {
        printf("Cannot move off the edge!\n");
        return -1;
    }

    // Wall collision check
    if (maze->grid[new_y][new_x] == '#') {
        printf("Blocked by wall!\n");
        return -1;
    }

    // Update position
    maze->player_x = new_x;
    maze->player_y = new_y;

    // Check exit condition
    if (new_x == maze->exit_x && new_y == maze->exit_y) return 1;
    return 0;
}

// Main game loop
void game_loop(Maze maze) {
    char cmd;
    while (1) {
        printf("Command (WASD/M/Q): ");
        if (scanf(" %c", &cmd) != 1) {
            printf("Input error!\n");
            while (getchar() != '\n'); // Clear input buffer
            continue;
        }

        if (cmd == 'Q' || cmd == 'q') {
            printf("Game quit.\n");
            break;
        } else if (cmd == 'M' || cmd == 'm') {
            print_maze(&maze);
        } else {
            int res = move_player(&maze, cmd);
            if (res == 1) {
                printf("\n!!! VICTORY !!! You found the exit!\n");
                break;
            } else if (res == -1) {
                printf("Invalid action.\n");
            }
        }
    }
}
