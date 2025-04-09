#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 100
#define MIN_SIZE 5

typedef struct {
    size_t height;
    size_t width;
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

    char buffer[MAX_SIZE + 2];
    size_t line_count = 0;
    int start_found = 0, exit_found = 0;
    
    // First pass: validate dimensions and structure
    while (fgets(buffer, sizeof(buffer), file)) {
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len-1] == '\n') len--;
        
        if (line_count == 0) {
            maze.width = len;
        } else if (len != maze.width) {
            printf("Invalid maze: Not rectangular\n");
            fclose(file);
            return maze;
        }
        line_count++;
    }

    // Validate dimensions with explicit type casting
    const size_t min_size = (size_t)MIN_SIZE;
    const size_t max_size = (size_t)MAX_SIZE;
    if (line_count < min_size || line_count > max_size || 
        maze.width < min_size || maze.width > max_size) {
        printf("Invalid maze dimensions\n");
        fclose(file);
        return maze;
    }
    maze.height = line_count;

    // Allocate memory
    maze.grid = malloc(maze.height * sizeof(char *));
    for (size_t i = 0; i < maze.height; i++) {
        maze.grid[i] = malloc(maze.width * sizeof(char));
    }

    // Second pass: load content
    rewind(file);
    for (size_t y = 0; y < maze.height; y++) {
        if (fgets(buffer, sizeof(buffer), file) == NULL) break;
        for (size_t x = 0; x < maze.width; x++) {
            char c = buffer[x];
            
            // Validate characters
            if (!(c == '#' || c == ' ' || c == 'S' || c == 'E')) {
                printf("Invalid character '%c' at (%zu,%zu)\n", c, y, x);
                free_maze(&maze);
                fclose(file);
                return (Maze){0};
            }

            maze.grid[y][x] = c;

            if (c == 'S') {
                if (start_found++) {
                    printf("Multiple start positions\n");
                    free_maze(&maze);
                    fclose(file);
                    return (Maze){0};
                }
                maze.player_x = (int)x;
                maze.player_y = (int)y;
            } else if (c == 'E') {
                if (exit_found++) {
                    printf("Multiple exit positions\n");
                    free_maze(&maze);
                    fclose(file);
                    return (Maze){0};
                }
                maze.exit_x = (int)x;
                maze.exit_y = (int)y;
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
    if (maze->grid) {
        for (size_t i = 0; i < maze->height; i++) {
            free(maze->grid[i]);
        }
        free(maze->grid);
        maze->grid = NULL;
    }
}

void print_maze(const Maze *maze) {
    for (size_t i = 0; i < maze->height; i++) {
        for (size_t j = 0; j < maze->width; j++) {
            printf("%c ", (i == (size_t)maze->player_y && j == (size_t)maze->player_x) ? 'X' : maze->grid[i][j]);
        }
        printf("\n");
    }
}

int move_player(Maze *maze, char dir) {
    int dx = 0, dy = 0;
    switch (dir) {
        case 'W': case 'w': dy = -1; break;
        case 'S': case 's': dy = 1; break;
        case 'A': case 'a': dx = -1; break;
        case 'D': case 'd': dx = 1; break;
        default: return -1;
    }

    int new_x = maze->player_x + dx;
    int new_y = maze->player_y + dy;

    if (new_x < 0 || (size_t)new_x >= maze->width || 
        new_y < 0 || (size_t)new_y >= maze->height) {
        printf("Cannot move off the edge!\n");
        return -1;
    }

    if (maze->grid[new_y][new_x] == '#') {
        printf("Blocked by wall!\n");
        return -1;
    }

    maze->player_x = new_x;
    maze->player_y = new_y;

    if (new_x == maze->exit_x && new_y == maze->exit_y) return 1;
    return 0;
}

void game_loop(Maze maze) {
    char cmd;
    char buffer[100];

    while (1) {
        printf("Command (WASD/M/Q): ");
        if (scanf(" %c", &cmd) != 1) {
            printf("Input error!\n");
            while (getchar() != '\n');
            continue;
        }

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
