import unittest
import subprocess
import os

class TestMazeGame(unittest.TestCase):

    def setUp(self):
        # Compile the C code
        self.compile_code()

    def compile_code(self):
        # Compile maze.c to generate the executable 'maze'
        result = subprocess.run(["gcc", "maze.c", "-o", "maze"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Compilation failed")
        self.assertTrue(os.path.exists("./maze"), "Executable 'maze' not found")

    def test_initialization(self):
        # Test program initialization
        result = subprocess.run(["./maze"], capture_output=True, text=True)
        self.assertIn("Enter a command", result.stdout, "Initialization failed")

    def test_invalid_command(self):
        # Test invalid command
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("X\nQ\n")
        self.assertIn("Invalid move!", output, "Invalid command not handled")

    def test_move_off_map(self):
        # Test moving off the map
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("W\nQ\n")
        self.assertIn("Cannot move off the edge of the map!", output, "Boundary check failed")

    def test_move_into_wall(self):
        # Test moving into a wall
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("A\nQ\n")
        self.assertIn("Cannot move through walls!", output, "Wall check failed")

    def test_view_map(self):
        # Test viewing the map
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("M\nQ\n")
        self.assertIn("X ", output, "Map display failed")

    def test_reach_exit(self):
        # Test reaching the exit
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("D\nS\nQ\n")
        self.assertIn("Congratulations! You've reached the exit!", output, "Exit check failed")

    def test_quit_game(self):
        # Test quitting the game
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("Q\n")
        self.assertIn("Game ended by user", output, "Quit check failed")

    def test_memory_leak(self):
        # Test for memory leaks
        process = subprocess.Popen(["valgrind", "./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("Q\n")
        self.assertNotIn("definitely lost", output, "Memory leak detected")

    def test_multiple_moves(self):
        # Test multiple moves
        process = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate("W\nA\nS\nD\nQ\n")
        self.assertNotIn("Invalid move!", output, "Multiple moves failed")

    def test_random_seed(self):
        # Test random seed
        process1 = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output1, _ = process1.communicate("M\nQ\n")
        process2 = subprocess.Popen(["./maze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output2, _ = process2.communicate("M\nQ\n")
        self.assertNotEqual(output1, output2, "Random seed not working")

if __name__ == "__main__":
    unittest.main()