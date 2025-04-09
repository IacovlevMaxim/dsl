import unittest
from unittest import mock
import io

# Mocking the context or dependencies
def get_output(code, mock_stdout, context):
    # Simulate the evaluation of the code
    exec(code, context)
    return mock_stdout.getvalue()

class TestPrintInfoAudio(unittest.TestCase):
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_audio_file_partial_metadata(self, mock_stdout):
        # Mock song with partial metadata
        partial_song = {"title": "Partial Song", "artist": "Unknown Artist"}
        code = """
try:
    print(f"Title: {song['title']}, Artist: {song['artist']}, Duration: {song.get('duration', 'Unknown')}")
except KeyError as e:
    print(f"Missing metadata: {e}")
"""
        # Capture the output
        output = get_output(code, mock_stdout, {"song": partial_song})
        # Validate the output
        self.assertIn("Title: Partial Song", output)
        self.assertIn("Artist: Unknown Artist", output)
        self.assertIn("Duration: Unknown", output)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_audio_file_minimum_metadata(self, mock_stdout):
        # Mock song with minimum metadata
        minimum_song = {"title": "Minimal Song"}
        code = """
try:
    print(f"Title: {song['title']}, Artist: {song.get('artist', 'Unknown')}, Duration: {song.get('duration', 'Unknown')}")
except KeyError as e:
    print(f"Missing metadata: {e}")
"""
        # Capture the output
        output = get_output(code, mock_stdout, {"song": minimum_song})
        # Validate the output
        self.assertIn("Title: Minimal Song", output)
        self.assertIn("Artist: Unknown", output)
        self.assertIn("Duration: Unknown", output)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_audio_file_after_metadata_change(self, mock_stdout):
        # Mock song with full metadata
        song = {"title": "Original Song", "artist": "Original Artist", "duration": "4:20"}
        code = """
# Update the metadata
song['artist'] = "New Artist"
print(f"Title: {song['title']}, Artist: {song['artist']}, Duration: {song['duration']}")
"""
        # Capture the output
        output = get_output(code, mock_stdout, {"song": song})
        # Validate the output
        self.assertIn("Title: Original Song", output)
        self.assertIn("Artist: New Artist", output)
        self.assertIn("Duration: 4:20", output)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_audio_file_changed_but_not_saved(self, mock_stdout):
        # Mock song with full metadata
        song = {"title": "Original Song", "artist": "Original Artist", "duration": "4:20"}
        code = """
# Change metadata but do not save
song['artist'] = "Temporary Artist"
print(f"Title: {song['title']}, Artist: {song['artist']}, Duration: {song['duration']}")
"""
        # Capture the output
        output = get_output(code, mock_stdout, {"song": song})
        # Validate the output
        self.assertIn("Title: Original Song", output)
        self.assertIn("Artist: Temporary Artist", output)
        self.assertIn("Duration: 4:20", output)

if __name__ == "__main__":
    unittest.main()