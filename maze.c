#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

Maze load_maze(const char *filename);
void print_maze(const Maze *maze);
int move_player(Maze *maze, char direction);
void game_loop(Maze maze);
void free_maze(Maze *maze);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <maze_file>\n", argv[0]);
        return 1;
    }

    Maze maze = load_maze(argv[1]);
    if (maze.grid == NULL) {
        printf("Failed to load maze.\n");
        return 1;
    }

    game_loop(maze);
    free_maze(&maze);
    return 0;
}

Maze load_maze(const char *filename) {
    Maze maze = {0};
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening file");
        return maze;
    }

    char buffer[MAX_SIZE + 2]; // +2 for newline and null terminator
    int line_count = 0;
    int start_found = 0, exit_found = 0;
    
    // First pass: validate dimensions and structure
    while (fgets(buffer, sizeof(buffer), file)) {
        size_t len = strlen(buffer);
        if (buffer[len-1] == '\n') len--; // Remove newline
        
        if (line_count == 0) {
            maze.width = len;
        } else if (len != maze.width) {
            printf("Invalid maze: Not rectangular\n");
            fclose(file);
            return maze;
        }
        line_count++;
    }

    // Validate dimensions
    if (line_count < MIN_SIZE || line_count > MAX_SIZE || 
        maze.width < MIN_SIZE || maze.width > MAX_SIZE) {
        printf("Invalid maze dimensions\n");
        fclose(file);
        return maze;
    }
    maze.height = line_count;

    // Allocate memory
    maze.grid = malloc(maze.height * sizeof(char *));
    for (int i = 0; i < maze.height; i++) {
        maze.grid[i] = malloc(maze.width * sizeof(char));
    }

    // Second pass: load content
    rewind(file);
    for (int y = 0; y < maze.height; y++) {
        fgets(buffer, sizeof(buffer), file);
        for (int x = 0; x < maze.width; x++) {
            char c = buffer[x];
            maze.grid[y][x] = c;

            if (c == 'S') {
                if (start_found++) {
                    printf("Multiple start positions\n");
                    free_maze(&maze);
                    fclose(file);
                    return (Maze){0};
                }
                maze.player_x = x;
                maze.player_y = y;
            } else if (c == 'E') {
                if (exit_found++) {
                    printf("Multiple exit positions\n");
                    free_maze(&maze);
                    fclose(file);
                    return (Maze){0};
                }
                maze.exit_x = x;
                maze.exit_y = y;
            }
        }
    }
    fclose(file);

    if (!start_found || !exit_found) {
        printf("Missing start/exit position\n");
        free_maze(&maze);
        return (Maze){0};
    }

    return maze;
}

void free_maze(Maze *maze) {
    for (int i = 0; i < maze->height; i++) {
        free(maze->grid[i]);
    }
    free(maze->grid);
    maze->grid = NULL;
}

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

// Main game loop with input buffer management
void game_loop(Maze maze) {
    char cmd;
    char buffer[100]; // Input buffer

    while (1) {
        printf("Command (WASD/M/Q): ");
        if (scanf(" %c", &cmd) != 1) {
            printf("Input error!\n");
            while (getchar() != '\n'); // Clear input buffer
            continue;
        }

        // Clear remaining characters in buffer
        fgets(buffer, sizeof(buffer), stdin);

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
