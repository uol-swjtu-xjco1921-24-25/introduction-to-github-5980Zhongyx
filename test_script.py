import unittest
import subprocess
import os
from io import StringIO
import sys

class TestMazeGame(unittest.TestCase):
    # --- Maze Loading Tests ---
    def test1_valid_maze_loading(self):
        """Test valid maze file is loaded correctly"""
        result = subprocess.run(["./mars_game", "valid_maze.txt"], capture_output=True, text=True)
        self.assertIn("Maze loaded", result.stdout)

    def test2_invalid_arguments(self):
        """Test invalid command line arguments handling"""
        # Fix: Capture stderr and check for usage message
        result = subprocess.run(["./mars_game"], capture_output=True, text=True)
        self.assertIn("Usage: ./mars_game <maze_file>", result.stderr)  # Fixed assertion

    def test3_file_not_found(self):
        """Test handling of non-existent maze file"""
        result = subprocess.run(["./mars_game", "nonexistent.txt"], capture_output=True, text=True)
        self.assertIn("File not found", result.stderr)

    # --- Maze Validation Tests ---
    def test4_invalid_maze_size(self):
        """Test validation of maze dimensions"""
        result = subprocess.run(["./mars_game", "invalid_size.txt"], capture_output=True, text=True)
        self.assertIn("Invalid maze dimensions", result.stderr)

    def test5_non_rectangular_maze(self):
        """Test detection of non-rectangular mazes"""
        result = subprocess.run(["./mars_game", "non_rectangular.txt"], capture_output=True, text=True)
        self.assertIn("Not rectangular", result.stderr)  # Fixed error message

    def test6_invalid_character(self):
        """Test detection of invalid maze characters"""
        result = subprocess.run(["./mars_game", "invalid_char.txt"], capture_output=True, text=True)
        self.assertIn("Invalid character '@'", result.stderr)  # Fixed error message

    def test7_multiple_starts(self):
        """Test detection of multiple start positions"""
        result = subprocess.run(["./mars_game", "multi_start.txt"], capture_output=True, text=True)
        self.assertIn("Multiple start positions", result.stderr)  # Fixed error message

    def test8_multiple_exits(self):
        """Test detection of multiple exit positions"""
        result = subprocess.run(["./mars_game", "multi_exit.txt"], capture_output=True, text=True)
        self.assertIn("Multiple exit positions", result.stderr)  # Fixed error message

    # --- Game Mechanics Tests ---
    def test9_mixed_errors(self):
        """Test error priority handling"""
        result = subprocess.run(["./mars_game", "mixed_errors.txt"], capture_output=True, text=True)
        self.assertIn("Invalid character", result.stderr)

    def test10_wall_collision(self):
        """Test wall collision handling"""
        test_input = "W\nQ\n"
        result = subprocess.run(["./mars_game", "valid_maze.txt"], input=test_input, text=True, capture_output=True)
        self.assertIn("Blocked by wall", result.stdout)

    def test11_boundary_check(self):
        """Test map boundary validation"""
        test_input = "D\nD\nD\nQ\n"  # Commands to move down repeatedly
        result = subprocess.run(["./mars_game", "valid_maze.txt"], input=test_input, text=True, capture_output=True)
        self.assertIn("Cannot move off the edge!", result.stdout)  # Fixed assertion

    def test12_valid_movement(self):
        """Test valid navigation path"""
        test_input = "E\nE\nN\nQ\n"
        result = subprocess.run(["./mars_game", "valid_maze.txt"], input=test_input, text=True, capture_output=True)
        self.assertIn("Moved east", result.stdout)

    def test13_victory_condition(self):
        """Test victory condition triggering"""
        test_input = "E\nE\nN\nN\n"
        result = subprocess.run(["./mars_game", "valid_maze.txt"], input=test_input, text=True, capture_output=True)
        self.assertIn("Congratulations!", result.stdout)

    def test14_map_display(self):
        """Test map visualization functionality"""
        result = subprocess.run(["./mars_game", "valid_maze.txt"], capture_output=True, text=True)
        self.assertIn("[P]", result.stdout)

    def test15_quit_command(self):
        """Test game termination command"""
        test_input = "Q\n"
        result = subprocess.run(["./mars_game", "valid_maze.txt"], input=test_input, text=True, capture_output=True)
        self.assertIn("Game quit", result.stdout)

    @unittest.skipUnless(os.path.exists("/usr/bin/valgrind"), "Valgrind not installed, skipping memory check")
    def test16_memory_management(self):
        """Test memory leak detection"""
        result = subprocess.run(["valgrind", "--leak-check=full", "./mars_game", "valid_maze.txt"], 
                              capture_output=True, text=True)
        self.assertNotIn("definitely lost", result.stderr)

if __name__ == '__main__':
    unittest.main()
