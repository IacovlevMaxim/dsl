import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
import eyed3

# Import your classes (adjust imports based on your project structure)
from src.interpreter.interpreter import (
    ForLoop, VariableDeclaration, Assignment, FunctionCall, IfStatement,
    BreakStatement, ContinueStatement, Literal, Identifier, Program,
    BinaryOperation, variables, Variable, VariableType
)
from src.interpreter.exceptions.break_exception import BreakException
from src.interpreter.exceptions.continue_exception import ContinueException


class TestForLoop(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear variables before each test
        variables.clear()

        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create test files
        self.test_files = {
            'test1.mp3': 'mp3 content',
            'test2.mp3': 'mp3 content',
            'image1.jpg': 'jpg content',
            'image2.png': 'png content',
            'document.txt': 'txt content',
            'unknown.xyz': 'unknown content'
        }

        for filename, content in self.test_files.items():
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)

        # Create empty directory
        self.empty_dir = tempfile.mkdtemp()

        # Create directory with only subdirectories
        self.folders_only_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.folders_only_dir, 'subfolder1'))
        os.makedirs(os.path.join(self.folders_only_dir, 'subfolder2'))

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directories
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.empty_dir)
        shutil.rmtree(self.folders_only_dir)
        variables.clear()

    def test_variable_name_conflict(self):
        """Test that ForLoop throws error when variable name already exists."""
        # Define a variable first
        variables['existing_var'] = Variable('existing_var', VariableType.NUMBER, 42)

        # Try to create ForLoop with same variable name
        directory_expr = Literal(self.temp_dir)
        body = Program([])

        for_loop = ForLoop(VariableType.UNKNOWN, 'existing_var', directory_expr, body)

        with self.assertRaises(NameError) as context:
            for_loop.eval()

        self.assertIn("Variable 'existing_var' already defined", str(context.exception))

    def test_invalid_directory(self):
        """Test that ForLoop throws error for invalid directory."""
        invalid_path = "/this/path/does/not/exist"
        directory_expr = Literal(invalid_path)
        body = Program([])

        for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)

        with self.assertRaises(ValueError) as context:
            for_loop.eval()

        self.assertIn(f"Directory '{invalid_path}' does not exist", str(context.exception))

    def test_empty_directory(self):
        """Test that ForLoop doesn't iterate when directory is empty."""
        directory_expr = Literal(self.empty_dir)
        executed = []

        # Create a mock body that tracks execution
        mock_stmt = MagicMock()
        mock_stmt.eval = lambda: executed.append('executed')
        body = Program([mock_stmt])

        for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
        result = for_loop.eval()

        # Should return None and not execute body
        self.assertIsNone(result)
        self.assertEqual(len(executed), 0)

    def test_folders_only_directory(self):
        """Test that ForLoop doesn't iterate when directory contains only folders."""
        directory_expr = Literal(self.folders_only_dir)
        executed = []

        mock_stmt = MagicMock()
        mock_stmt.eval = lambda: executed.append('executed')
        body = Program([mock_stmt])

        for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
        result = for_loop.eval()

        self.assertIsNone(result)
        self.assertEqual(len(executed), 0)

    @patch('eyed3.load')
    def test_variable_types_audio_file(self, mock_eyed3_load):
        """Test that audio files are correctly typed as AUDIO_FILE."""
        mock_audio = MagicMock()
        mock_eyed3_load.return_value = mock_audio

        # Create directory with only MP3 files
        mp3_dir = tempfile.mkdtemp()
        mp3_file = os.path.join(mp3_dir, 'test.mp3')
        with open(mp3_file, 'w') as f:
            f.write('mp3 content')

        try:
            directory_expr = Literal(mp3_dir)
            captured_vars = []

            def capture_variable():
                if 'test_var' in variables:
                    captured_vars.append({
                        'type': variables['test_var'].type,
                        'value': variables['test_var'].value
                    })

            mock_stmt = MagicMock()
            mock_stmt.eval = capture_variable
            body = Program([mock_stmt])

            for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
            for_loop.eval()

            self.assertEqual(len(captured_vars), 1)
            self.assertEqual(captured_vars[0]['type'], VariableType.AUDIO_FILE)
            self.assertEqual(captured_vars[0]['value'], mock_audio)

        finally:
            shutil.rmtree(mp3_dir)

    @patch('exiftool.ExifToolHelper')
    def test_variable_types_image_file(self, mock_exiftool_helper):
        """Test that image files are correctly typed as IMAGE_FILE."""
        mock_metadata = {'test': 'metadata'}
        mock_et = MagicMock()
        mock_et.get_metadata.return_value = [mock_metadata]
        mock_exiftool_helper.return_value.__enter__.return_value = mock_et

        # Create directory with only image files
        img_dir = tempfile.mkdtemp()
        img_file = os.path.join(img_dir, 'test.jpg')
        with open(img_file, 'w') as f:
            f.write('jpg content')

        try:
            directory_expr = Literal(img_dir)
            captured_vars = []

            def capture_variable():
                if 'test_var' in variables:
                    captured_vars.append({
                        'type': variables['test_var'].type,
                        'value': variables['test_var'].value
                    })

            mock_stmt = MagicMock()
            mock_stmt.eval = capture_variable
            body = Program([mock_stmt])

            for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
            for_loop.eval()

            self.assertEqual(len(captured_vars), 1)
            self.assertEqual(captured_vars[0]['type'], VariableType.IMAGE_FILE)
            self.assertEqual(captured_vars[0]['value'], mock_metadata)

        finally:
            shutil.rmtree(img_dir)

    def test_variable_types_unknown(self):
        """Test that unknown file extensions are typed as UNKNOWN."""
        # Create directory with unknown file type
        unknown_dir = tempfile.mkdtemp()
        unknown_file = os.path.join(unknown_dir, 'test.xyz')
        with open(unknown_file, 'w') as f:
            f.write('unknown content')

        try:
            directory_expr = Literal(unknown_dir)
            captured_vars = []

            def capture_variable():
                if 'test_var' in variables:
                    captured_vars.append({
                        'type': variables['test_var'].type,
                        'value': variables['test_var'].value
                    })

            mock_stmt = MagicMock()
            mock_stmt.eval = capture_variable
            body = Program([mock_stmt])

            for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
            for_loop.eval()

            self.assertEqual(len(captured_vars), 1)
            self.assertEqual(captured_vars[0]['type'], VariableType.UNKNOWN)
            self.assertEqual(captured_vars[0]['value'], unknown_file)

        finally:
            shutil.rmtree(unknown_dir)

    def test_continue_on_last_file(self):
        """Test that continue on last file exits gracefully."""
        # Create directory with single file
        single_file_dir = tempfile.mkdtemp()
        single_file = os.path.join(single_file_dir, 'only.txt')
        with open(single_file, 'w') as f:
            f.write('content')

        try:
            directory_expr = Literal(single_file_dir)

            def mock_body_execution():
                raise ContinueException()  # Always continue (skip)

            mock_stmt = MagicMock()
            mock_stmt.eval = mock_body_execution
            body = Program([mock_stmt])

            for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
            result = for_loop.eval()

            # Should complete without error
            self.assertIsNone(result)

        finally:
            shutil.rmtree(single_file_dir)

    def test_variable_cleanup_after_break(self):
        """Test that loop variable is cleaned up after break."""
        directory_expr = Literal(self.temp_dir)

        def mock_body_execution():
            raise BreakException()  # Break immediately

        mock_stmt = MagicMock()
        mock_stmt.eval = mock_body_execution
        body = Program([mock_stmt])

        for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
        for_loop.eval()

        # Variable should be cleaned up even after break
        self.assertNotIn('test_var', variables)

    def test_variable_cleanup_after_exception(self):
        """Test that loop variable is cleaned up after exception."""
        directory_expr = Literal(self.temp_dir)

        def mock_body_execution():
            raise ValueError("Test exception")

        mock_stmt = MagicMock()
        mock_stmt.eval = mock_body_execution
        body = Program([mock_stmt])

        for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)

        with self.assertRaises(ValueError):
            for_loop.eval()

        # Variable should be cleaned up even after exception
        self.assertNotIn('test_var', variables)

    def test_multiple_file_extensions(self):
        """Test handling of multiple file extensions correctly."""
        # Create directory with various image extensions
        multi_ext_dir = tempfile.mkdtemp()
        extensions = ['jpg', 'jpeg', 'png', 'gif']

        for ext in extensions:
            filepath = os.path.join(multi_ext_dir, f'test.{ext}')
            with open(filepath, 'w') as f:
                f.write(f'{ext} content')

        try:
            with patch('exiftool.ExifToolHelper') as mock_exiftool:
                mock_et = MagicMock()
                mock_et.get_metadata.return_value = [{'test': 'metadata'}]
                mock_exiftool.return_value.__enter__.return_value = mock_et

                directory_expr = Literal(multi_ext_dir)
                captured_types = []

                def capture_type():
                    if 'test_var' in variables:
                        captured_types.append(variables['test_var'].type)

                mock_stmt = MagicMock()
                mock_stmt.eval = capture_type
                body = Program([mock_stmt])

                for_loop = ForLoop(VariableType.UNKNOWN, 'test_var', directory_expr, body)
                for_loop.eval()

                # All should be IMAGE_FILE type
                self.assertEqual(len(captured_types), 4)
                self.assertTrue(all(t == VariableType.IMAGE_FILE for t in captured_types))

        finally:
            shutil.rmtree(multi_ext_dir)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestForLoop)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\nRan {result.testsRun} tests")
    if result.failures:
        print(f"Failures: {len(result.failures)}")
    if result.errors:
        print(f"Errors: {len(result.errors)}")
    if result.wasSuccessful():
        print("All tests passed!")