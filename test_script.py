import unittest
import subprocess
import os

#main test class 
class TestMazeGame(unittest.TestCase):
    TEST_MAZE_DIR = "test_mazes"
    #maze files folder to store test maze files
    def setUp(self):
        # Run before every test
        self.compile_code()
        #to make sure code compiled
        os.makedirs(self.TEST_MAZE_DIR, exist_ok=True)

        self.create_test_files()
        
    def compile_code(self):
        """Compile C source code to generate executable"""
        #tey to compile the C program
        result = subprocess.run(
            ["gcc", "maze.c", "-o", "maze", "-Wall", "-Wextra"], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            self.fail(f"Compilation failed:\n{result.stderr}")
            #If compile fails: CRASH!
#helper to create maze test files

    def create_test_files(self):
        """Create standardized test maze files"""
        test_cases = {
            # Valid 5x5 maze
            "sample1.txt": [
                "#####",
                "#S E#",
                "#   #",
                "#   #",
                "#####"
            ],
            # Contains invalid character '@' (now 5x5)
            "sample6.txt": [
                "#####",
                "#S@ #",
                "#   #",
                "#  E#",
                "#####"
            ],
            # Multiple start positions (now 5x5)
            "sample7.txt": [
                "#####",
                "#SS #",
                "#   #",
                "#  E#",
                "#####"
            ],
            # Multiple exit positions (now 5x5)
            "sample8.txt": [
                "#####",
                "#S  #",
                "#   #",
                "# EE#",
                "#####"
            ],
            # Valid dimensions but invalid character '$'
            "sample9.txt": [
                "#####",
                "#S$ #",
                "#   #",
                "#  E#",
                "#####"
            ]
        }
#write each maze to a file
        for filename, content in test_cases.items():
            path = os.path.join(self.TEST_MAZE_DIR, filename)
            with open(path, "w") as f:
                f.write("\n".join(content))

    def run_maze(self, maze_file, inputs=""):
        """Execute maze program and capture outputs"""
        cmd = ["./maze", os.path.join(self.TEST_MAZE_DIR, maze_file)]
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge output streams
                text=True
            )
            full_input = inputs + "\nQ\n"  # Ensure clean exit
            output, _ = process.communicate(full_input, timeout=5)
            return process.returncode, output
        except Exception as e:
            return -1, str(e)

    # ==================== Test Cases ====================
    
    def test1_valid_maze_loading(self):
        """Test valid maze file loading"""
        rc, out = self.run_maze("sample1.txt")
        self.assertEqual(rc, 0)
        self.assertIn("Command (WASD/M/Q):", out)

    def test2_invalid_arguments(self):
        """Test command line argument validation"""
        # No arguments test
        result = subprocess.run(
            ["./maze"],
            capture_output=True,
            text=True
        )
        self.assertIn("Usage:", result.stdout)
        
        # Extra arguments test
        result = subprocess.run(
            ["./maze", "a", "b"],
            capture_output=True,
            text=True
        )
        self.assertIn("Usage:", result.stdout)

    def test3_file_not_found(self):
        """Test non-existent file handling"""
        rc, out = self.run_maze("invalid.txt")
        self.assertNotEqual(rc, 0)
        self.assertIn("Error opening file", out)

    def test4_invalid_maze_size(self):
        """test maze size"""
        rc, out = self.run_maze("sample4_invalid_size.txt")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid maze dimensions", out)

    def test5_non_rectangular_maze(self):
        """test non-rectangular maze"""
        rc, out = self.run_maze("sample5_non_rect.txt")
        self.assertIn("Invalid maze: Not rectangular", out)

    def test6_invalid_character(self):
        """Test invalid character detection"""
        rc, out = self.run_maze("sample6.txt")
        self.assertIn("Invalid character '@'", out)

    def test7_multiple_starts(self):
        """Test multiple start position detection"""
        rc, out = self.run_maze("sample7.txt")
        self.assertIn("Multiple start positions", out)

    def test8_multiple_exits(self):
        """Test multiple exit position detection"""
        rc, out = self.run_maze("sample8.txt")
        self.assertIn("Multiple exit positions", out)

    def test9_mixed_errors(self):
        """Test error priority handling"""
        rc, out = self.run_maze("sample9.txt")
        self.assertIn("Invalid character '$'", out)

    def test10_wall_collision(self):
        """Test wall collision handling"""
        _, out = self.run_maze("sample1.txt", "W")
        self.assertIn("Blocked by wall!", out)

    def test11_boundary_check(self):
        """test map boundary"""
        _, out = self.run_maze("sample1_edge.txt", "A")
        self.assertIn("Cannot move off the edge!", out)

    def test12_valid_movement(self):
        """Test valid navigation path"""
        _, out = self.run_maze("sample1.txt", "D\nD\nS\nS")
        self.assertNotIn("Blocked", out)
        self.assertNotIn("Invalid", out)

    def test13_victory_condition(self):
        """Test victory condition triggering"""
        _, out = self.run_maze("sample1.txt", "D\nD\nS\nS\nD")
        self.assertIn("!!! VICTORY !!!", out)

    def test14_map_display(self):
        """Test map visualization functionality"""
        _, out = self.run_maze("sample1.txt", "M")
        self.assertIn("X", out)  # player position show by "X"
        self.assertIn("S", out)  # "S": start marker
        self.assertIn("E", out)  # "E" : Exit marker "VICTORY！"

    def test15_quit_command(self):
        """Test game termination command"""
        _, out = self.run_maze("sample1.txt", "Q")
        self.assertIn("Game quit.", out)

    def test16_memory_management(self):
        """Test memory leak detection"""
        try:
            process = subprocess.Popen(
                ["valgrind", "--leak-check=full", 
                 "./maze", os.path.join(self.TEST_MAZE_DIR, "sample1.txt")],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            _, err = process.communicate("Q\n", timeout=10)
            self.assertIn("0 errors from 0 contexts", err)
        except FileNotFoundError:
            self.skipTest("Valgrind not installed, skipping memory check")

if __name__ == "__main__":
    unittest.main(verbosity=2)
