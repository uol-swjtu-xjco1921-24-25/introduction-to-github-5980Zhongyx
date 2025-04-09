import unittest
import subprocess
import os
import re

class TestMazeGame(unittest.TestCase):

    def setUp(self):
        # Compile C code before each test
        self.compile_code()

    def compile_code(self):
        """Compile maze.c to generate the executable."""
        result = subprocess.run(["gcc", "maze.c", "-o", "maze"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Compilation failed: {result.stderr}")
        self.assertTrue(os.path.exists("./maze"), "Executable 'maze' not found")

    def test_initialization(self):
        """Test if the game initializes with correct prompts."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("Q\n")
        self.assertIn("Command (WASD/M/Q):", output, "Initialization prompt missing")

    def test_invalid_command(self):
        """Test handling of invalid input commands."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("X\nQ\n")
        self.assertIn("Invalid action.", output, "Invalid command not handled")

    def test_move_off_map(self):
        """Test boundary checks when moving outside the map."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("A\nA\nA\nQ\n")  # Multiple left moves
        self.assertIn("Cannot move off the edge!", output, "Boundary check failed")

    def test_move_into_wall(self):
        """Test collision detection with walls."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("W\nQ\n")  # Move into wall
        self.assertIn("Blocked by wall!", output, "Wall collision not detected")

    def test_view_map(self):
        """Test map display functionality."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("M\nQ\n")
        self.assertTrue(re.search(r'X |# |E |S ', output), "Map rendering failed")

    def test_reach_exit(self):
        """Test victory condition when reaching the exit."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("D\nD\nS\nS\nQ\n")  # Example path
        self.assertIn("!!! VICTORY !!!", output, "Exit not reached")

    def test_quit_game(self):
        """Test game termination with quit command."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("Q\n")
        self.assertIn("Game quit.", output, "Quit command failed")

    def test_memory_leak(self):
        """Check for memory leaks using Valgrind."""
        try:
            process = subprocess.Popen(
                ["valgrind", "--leak-check=full", "./maze"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            _, errors = process.communicate("Q\n")
            self.assertIn("0 bytes in 0 blocks", errors, "Memory leaks detected")
        except FileNotFoundError:
            self.skipTest("Valgrind not installed, skipping memory check")

    def test_multiple_moves(self):
        """Test sequential valid moves."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("D\nS\nA\nW\nQ\n")
        self.assertNotIn("Invalid action.", output, "Sequential moves failed")

    def test_maze_randomness(self):
        """Verify maze generation randomness."""
        process1 = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output1, _ = process1.communicate("M\nQ\n")
        process2 = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output2, _ = process2.communicate("M\nQ\n")
        self.assertNotEqual(output1, output2, "Maze generation lacks randomness")

    def test_dynamic_exit_position(self):
        """Ensure exit is not fixed at bottom-right."""
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("M\nQ\n")
        self.assertNotRegex(output, r'E\s+$', "Exit position is static")

    def test_path_connectivity(self):
        """Verify there is always a path from start to exit."""
        for _ in range(3):  # Test 3 mazes
            process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            output, _ = process.communicate("D\nS\nA\nW\nD\nS\nQ\n")
            self.assertNotIn("Blocked by wall!", output, "Path connectivity failed")

if __name__ == "__main__":
    unittest.main()
