import unittest
import subprocess
import os
import re

class TestMazeGame(unittest.TestCase):
    TEST_MAZE_DIR = "test_mazes"
    
    def setUp(self):
        self.compile_code()
        self.base_cmd = ["./maze"]
        os.makedirs(self.TEST_MAZE_DIR, exist_ok=True)
        
        # Create test maze files
        self.create_test_files()

    def compile_code(self):
        """Compile C code to generate executable"""
        result = subprocess.run(
            ["gcc", "maze.c", "-o", "maze"], 
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self.fail(f"Compilation failed: {result.stderr}")

    def create_test_files(self):
        """Create all test maze files"""
        test_cases = {
            # Valid maze
            "valid.maze": [
                "#####",
                "#S E#",
                "#   #",
                "#   #",
                "#####"
            ],
            # Invalid size (4x5)
            "invalid_size.maze": [
                "####",
                "#S #",
                "# E#",
                "####"
            ],
            # Non-rectangular maze
            "non_rect.maze": [
                "#####",
                "#S  ",
                "#  E#",
                "#####"
            ],
            # Multiple starts
            "multi_s.maze": [
                "#####",
                "SS  #",
                "#  E#",
                "#   #",
                "#####"
            ],
            # Missing exit
            "no_exit.maze": [
                "#####",
                "#S  #",
                "#####",
                "#   #",
                "#####"
            ]
        }

        for filename, content in test_cases.items():
            with open(os.path.join(self.TEST_MAZE_DIR, filename), "w") as f:
                f.write("\n".join(content))

    def run_maze(self, maze_file, inputs):
        """Run maze program and return output"""
        cmd = self.base_cmd + [os.path.join(self.TEST_MAZE_DIR, maze_file)]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate(inputs)
        return process.returncode, output, error

    # ------------------- Core Test Cases -------------------

    def test1_valid_maze_loading(self):
        """Test valid maze file loading"""
        rc, out, err = self.run_maze("valid.maze", "Q\n")
        self.assertEqual(rc, 0)
        self.assertIn("Command (WASD/M/Q):", out)

    def test2_invalid_arguments(self):
        """Test command line argument handling"""
        # No arguments
        process = subprocess.Popen(
            ["./maze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        _, err = process.communicate()
        self.assertIn("Usage:", err)

        # Extra arguments
        process = subprocess.Popen(
            ["./maze", "a", "b"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        _, err = process.communicate()
        self.assertIn("Usage:", err)

    def test3_file_not_found(self):
        """Test non-existent file handling"""
        rc, _, err = self.run_maze("nonexistent.maze", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Error opening file", err)

    def test4_invalid_maze_size(self):
        """Test maze size validation"""
        rc, _, err = self.run_maze("invalid_size.maze", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid maze dimensions", err)

    def test5_non_rectangular_maze(self):
        """Test non-rectangular maze detection"""
        rc, _, err = self.run_maze("non_rect.maze", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Not rectangular", err)

    def test6_multiple_start_positions(self):
        """Test multiple start position detection"""
        rc, _, err = self.run_maze("multi_s.maze", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Multiple start positions", err)

    def test7_missing_exit(self):
        """Test missing exit detection"""
        rc, _, err = self.run_maze("no_exit.maze", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Missing start/exit position", err)

    def test8_wall_collision(self):
        """Test wall collision handling"""
        rc, out, _ = self.run_maze("valid.maze", "W\nQ\n")  # Move up into wall
        self.assertIn("Blocked by wall!", out)

    def test9_valid_movement(self):
        """Test valid movement path"""
        inputs = "D\n"*3 + "S\n"*2 + "Q\n"  # Right->Down
        rc, out, _ = self.run_maze("valid.maze", inputs)
        self.assertNotIn("Blocked", out)
        self.assertNotIn("Invalid", out)

    def test10_victory_condition(self):
        """Test victory condition triggering"""
        inputs = "D\n"*3 + "S\n"*2 + "D\n"  # Path to exit
        rc, out, _ = self.run_maze("valid.maze", inputs)
        self.assertIn("!!! VICTORY !!!", out)

    def test11_map_display(self):
        """Test map display functionality"""
        rc, out, _ = self.run_maze("valid.maze", "M\nQ\n")
        self.assertIn("X", out)  # Player position marker
        self.assertIn("E", out)  # Exit display

    def test12_invalid_input_handling(self):
        """Test invalid input handling"""
        rc, out, _ = self.run_maze("valid.maze", "X\nZ\n1\nQ\n")
        self.assertGreaterEqual(out.count("Invalid action."), 2)

    def test13_boundary_check(self):
        """Test map boundary validation"""
        inputs = "A\n"*10 + "Q\n"  # Multiple left moves
        rc, out, _ = self.run_maze("valid.maze", inputs)
        self.assertIn("Cannot move off the edge!", out)

    def test14_memory_management(self):
        """Test memory leak detection"""
        try:
            process = subprocess.Popen(
                ["valgrind", "--leak-check=full", "./maze", os.path.join(self.TEST_MAZE_DIR, "valid.maze")],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            _, err = process.communicate("Q\n")
            self.assertIn("0 errors from 0 contexts", err)
        except FileNotFoundError:
            self.skipTest("Valgrind not installed, skipping memory check")

if __name__ == "__main__":
    unittest.main(verbosity=2)
