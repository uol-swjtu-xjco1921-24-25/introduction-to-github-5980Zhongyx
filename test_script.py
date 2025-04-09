import unittest
import subprocess
import os
import re

class TestMazeGame(unittest.TestCase):
    TEST_MAZE_DIR = "test_mazes"
    
    def setUp(self):
        self.compile_code()
        os.makedirs(self.TEST_MAZE_DIR, exist_ok=True)
        
    def compile_code(self):
        """Compile C code to generate executable"""
        result = subprocess.run(
            ["gcc", "maze.c", "-o", "maze"], 
            capture_output=True, 
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Compilation failed: {result.stderr}")
        self.assertTrue(os.path.exists("./maze"), "Executable 'maze' not found")

    def run_maze(self, maze_file, inputs):
        """Run maze program and return output"""
        cmd = ["./maze", os.path.join(self.TEST_MAZE_DIR, maze_file)]
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
        rc, out, err = self.run_maze("sample1.txt", "Q\n")
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
        rc, _, err = self.run_maze("nonexistent.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Error opening file", err)

    def test4_invalid_maze_size(self):
        """Test maze size validation"""
        rc, _, err = self.run_maze("sample9.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid maze dimensions", err)

    def test5_non_rectangular_maze(self):
        """Test non-rectangular maze detection"""
        rc, _, err = self.run_maze("sample6.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Not rectangular", err)

    def test6_invalid_character(self):
        """Test invalid character detection"""
        rc, _, err = self.run_maze("sample6.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid character '@'", err)

    def test7_multiple_starts(self):
        """Test multiple start positions detection"""
        rc, _, err = self.run_maze("sample7.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Multiple start positions", err)

    def test8_multiple_exits(self):
        """Test multiple exit positions detection"""
        rc, _, err = self.run_maze("sample8.txt", "")
        self.assertNotEqual(rc, 0)
        self.assertIn("Multiple exit positions", err)

    def test9_mixed_errors(self):
        """Test combined error detection priority"""
        rc, _, err = self.run_maze("sample9.txt", "")
        self.assertIn("Invalid maze dimensions", err)

    def test10_wall_collision(self):
        """Test wall collision handling"""
        rc, out, _ = self.run_maze("sample1.txt", "W\nQ\n")
        self.assertIn("Blocked by wall!", out)

    def test11_boundary_check(self):
        """Test map boundary validation"""
        rc, out, _ = self.run_maze("sample1.txt", "A\nA\nA\nQ\n")
        self.assertIn("Cannot move off the edge!", out)

    def test12_valid_movement(self):
        """Test valid movement path"""
        inputs = "D\n"*3 + "S\n"*2 + "Q\n"
        rc, out, _ = self.run_maze("sample2.txt", inputs)
        self.assertNotIn("Blocked", out)
        self.assertNotIn("Invalid", out)

    def test13_victory_condition(self):
        """Test victory condition triggering"""
        inputs = "D\n"*3 + "S\n"*2 + "D\n"
        rc, out, _ = self.run_maze("sample2.txt", inputs)
        self.assertIn("!!! VICTORY !!!", out)

    def test14_map_display(self):
        """Test map display functionality"""
        rc, out, _ = self.run_maze("sample1.txt", "M\nQ\n")
        self.assertIn("X", out)  # Player position
        self.assertIn("S", out)  # Start marker
        self.assertIn("E", out)  # Exit marker

    def test15_quit_command(self):
        """Test game termination with quit command"""
        rc, out, _ = self.run_maze("sample1.txt", "Q\n")
        self.assertIn("Game quit.", out)

    def test16_memory_management(self):
        """Test memory leak detection"""
        try:
            process = subprocess.Popen(
                ["valgrind", "--leak-check=full", "./maze", os.path.join(self.TEST_MAZE_DIR, "sample1.txt")],
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
