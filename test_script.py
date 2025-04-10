import unittest
import subprocess
import os

class TestMazeGame(unittest.TestCase):
    TEST_MAZE_DIR = "test_mazes"
    
    def setUp(self):
        self.compile_code()
        os.makedirs(self.TEST_MAZE_DIR, exist_ok=True)
        self.create_test_files()
        
    def compile_code(self):
        """Compile C source code to generate executable"""
        result = subprocess.run(
            ["gcc", "maze.c", "-o", "maze", "-Wall", "-Wextra"], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            self.fail(f"Compilation failed:\n{result.stderr}")

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
        # Check stdout (C代码错误输出到stdout)
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
        """Test maze dimension validation"""
        # 使用一个尺寸不足的迷宫文件（例如4x4）
        rc, out = self.run_maze("sample9.txt")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid maze dimensions", out)

    def test5_non_rectangular_maze(self):
        """Test non-rectangular maze detection"""
        # 使用一个非矩形的合法尺寸迷宫（例如5x5但某行少一个字符）
        rc, out = self.run_maze("sample6.txt")
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
        """Test map boundary validation"""
        # 确保初始位置在边缘（例如sample1中S在(1,1)，输入"A"会越界
        _, out = self.run_maze("sample1.txt", "A")
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
        self.assertIn("X", out)  # Player position
        self.assertIn("S", out)  # Start marker
        self.assertIn("E", out)  # Exit marker

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
