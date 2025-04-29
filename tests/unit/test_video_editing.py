import os
import unittest
import shutil
from mutagen.mp4 import MP4

class TestVideoMetadataEditing(unittest.TestCase):

    def setUp(self):
        # Create a working copy of a sample video
        self.original_video_path = "C:/Users/user/Desktop/UniFiles/Anul2_Sem2/dsl/tests/temp/test.mp4"
        self.test_video_path = "test_temp_video.mp4"
        shutil.copyfile(self.original_video_path, self.test_video_path)

    def tearDown(self):
        # Remove the working test video
        if os.path.exists(self.test_video_path):
            os.remove(self.test_video_path)

    def test_load_video_file(self):
        """Test loading a video file."""
        video = MP4(self.test_video_path)
        self.assertIsNotNone(video)
        self.assertIsInstance(video, MP4)

    def test_edit_and_verify_metadata(self):
        """Test changing and verifying metadata fields."""
        video = MP4(self.test_video_path)

        # Set metadata fields
        video["\xa9nam"] = ["Test Title"]
        video["\xa9ART"] = ["Test Artist"]
        video["\xa9alb"] = ["Test Album"]
        video["\xa9gen"] = ["Test Genre"]
        video["desc"] = ["Test Description"]

        # Save the changes
        video.save()

        # Reload to verify
        reloaded_video = MP4(self.test_video_path)

        self.assertEqual(reloaded_video.get("\xa9nam", [""])[0], "Test Title")
        self.assertEqual(reloaded_video.get("\xa9ART", [""])[0], "Test Artist")
        self.assertEqual(reloaded_video.get("\xa9alb", [""])[0], "Test Album")
        self.assertEqual(reloaded_video.get("\xa9gen", [""])[0], "Test Genre")
        self.assertEqual(reloaded_video.get("desc", [""])[0], "Test Description")

    def test_save_video_file(self):
        """Test saving the video file works."""
        video = MP4(self.test_video_path)
        video.save()
        self.assertTrue(os.path.exists(self.test_video_path))
        reloaded_video = MP4(self.test_video_path)
        self.assertIsNotNone(reloaded_video.tags)

if __name__ == "__main__":
    unittest.main()
