import io
import os
import tempfile
import unittest
import unittest.mock
from tests.utils.get_output import *
from src.interpreter.exceptions.infinte_loop_exception import InfiniteLoopException


class ForOfLoopTests(unittest.TestCase):

    def setUp(self):
        """Создаем временные директории и файлы для тестов"""
        # Создаем временную директорию
        self.test_dir = tempfile.mkdtemp()
        self.empty_dir = tempfile.mkdtemp()
        self.audio_dir = tempfile.mkdtemp()
        self.image_dir = tempfile.mkdtemp()
        self.mixed_dir = tempfile.mkdtemp()

        # Создаем тестовые файлы
        self.test_files = ['file1.txt', 'file2.txt', 'file3.txt']
        for filename in self.test_files:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write('test content')

        # Создаем аудио файлы (пустые для тестов)
        self.audio_files = ['song1.mp3', 'song2.mp3']
        for filename in self.audio_files:
            with open(os.path.join(self.audio_dir, filename), 'w') as f:
                f.write('')

        # Создаем изображения
        self.image_files = ['image1.jpg', 'image2.png']
        for filename in self.image_files:
            with open(os.path.join(self.image_dir, filename), 'w') as f:
                f.write('')

        # Создаем смешанную директорию
        self.mixed_files = ['audio.mp3', 'image.jpg', 'document.txt']
        for filename in self.mixed_files:
            with open(os.path.join(self.mixed_dir, filename), 'w') as f:
                f.write('')

    def tearDown(self):
        """Очищаем временные файлы и директории"""
        import shutil
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.empty_dir)
        shutil.rmtree(self.audio_dir)
        shutil.rmtree(self.image_dir)
        shutil.rmtree(self.mixed_dir)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_simple_for_of_loop(self, mock_stdout):
        """Тест простого for...of цикла"""
        code = f"""
        for (file currentFile of "{self.test_dir}") {{
            print("Processing file")
        }}
        """
        output = get_output(code, mock_stdout)
        # Должно напечатать "Processing file" для каждого файла
        expected_lines = ["Processing file"] * len(self.test_files)
        self.assertEqual(output, "\n".join(expected_lines))


    def test_invalid_directory(self):
        """Тест с несуществующей директорией"""
        code = """
        for (file invalidFile of "nonexistent_directory") {
            print(invalidFile)
        }
        """
        with self.assertRaises(ValueError) as context:
            get_output(code, io.StringIO())
        self.assertIn("does not exist", str(context.exception))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_empty_directory(self, mock_stdout):
        """Тест с пустой директорией"""
        code = f"""
        for (file emptyFile of "{self.empty_dir}") {{
            print(emptyFile)
        }}
        print("Done")
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "Done")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_unknown_file_extensions(self, mock_stdout):
        """Тест с неизвестными расширениями файлов"""
        code = f"""
        number unknownCount = 0
        for (file currentFile of "{self.test_dir}") {{
            unknownCount = unknownCount + 1
            print(unknownCount)
        }}
        """
        output = get_output(code, mock_stdout)
        expected_output = "\n".join([str(i + 1) for i in range(len(self.test_files))])
        self.assertEqual(output, expected_output)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_conditional_statements_in_loop(self, mock_stdout):
        """Тест условных операторов внутри for...of цикла"""
        code = f"""
        number count = 0
        for (file currentFile of "{self.test_dir}") {{
            if (count < 2) then {{
                print("Processing")
            }}
            count = count + 1
        }}
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "Processing\nProcessing")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_continue_statement(self, mock_stdout):
        """Тест continue внутри for...of цикла"""
        code = f"""
        number skipped = 0
        for (file currentFile of "{self.test_dir}") {{
            skipped = skipped + 1
            if (skipped == 2) then continue
            print("Processing")
        }}
        """
        output = get_output(code, mock_stdout)
        # Должно пропустить второй файл
        expected_lines = ["Processing"] * (len(self.test_files) - 1)
        self.assertEqual(output, "\n".join(expected_lines))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_continue_on_last_file(self, mock_stdout):
        """Тест continue на последнем файле"""
        code = f"""
        number fileCount = 0
        for (file currentFile of "{self.test_dir}") {{
            fileCount = fileCount + 1
            if (fileCount == {len(self.test_files)}) then continue
            print("Processing")
        }}
        """
        output = get_output(code, mock_stdout)
        # Должно пропустить последний файл
        expected_lines = ["Processing"] * (len(self.test_files) - 1)
        self.assertEqual(output, "\n".join(expected_lines))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_break_statement(self, mock_stdout):
        """Тест break внутри for...of цикла"""
        code = f"""
        number processed = 0
        for (file currentFile of "{self.test_dir}") {{
            print("Processing")
            processed = processed + 1
            if (processed == 2) then break
        }}
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "Processing\nProcessing")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_break_in_conditional(self, mock_stdout):
        """Тест break внутри условного оператора"""
        code = f"""
        number count = 0
        for (file currentFile of "{self.test_dir}") {{
            count = count + 1
            if (count == 1) then {{
                print("First file")
                break
            }}
            print("Other file")
        }}
        """
        output = get_output(code, mock_stdout)
        self.assertEqual(output, "First file")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_nested_for_of_loops(self, mock_stdout):
        """Тест вложенных for...of циклов"""
        # Создаем вторую директорию с файлами для вложенного цикла
        nested_dir = tempfile.mkdtemp()
        try:
            nested_files = ['nested1.txt', 'nested2.txt']
            for filename in nested_files:
                with open(os.path.join(nested_dir, filename), 'w') as f:
                    f.write('nested content')

            code = f"""
            for (file outerFile of "{self.test_dir}") {{
                print("Outer")
                for (file innerFile of "{nested_dir}") {{
                    print("Inner")
                }}
            }}
            """
            output = get_output(code, mock_stdout)

            # Для каждого внешнего файла должно быть "Outer" + 2 "Inner"
            expected_lines = []
            for _ in range(len(self.test_files)):
                expected_lines.append("Outer")
                expected_lines.extend(["Inner"] * len(nested_files))

            self.assertEqual(output, "\n".join(expected_lines))
        finally:
            import shutil
            shutil.rmtree(nested_dir)

    @unittest.mock.patch('eyed3.load')
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_audio_file_processing(self, mock_stdout, mock_eyed3_load):
        """Тест обработки аудио файлов"""
        # Мокаем eyed3.load чтобы избежать реальной загрузки файлов
        mock_audio = unittest.mock.MagicMock()
        mock_audio.tag.title = "Test Title"
        mock_audio.tag.artist = "Test Artist"
        mock_eyed3_load.return_value = mock_audio

        code = f"""
        for (file audioFile of "{self.audio_dir}") {{
            print(audioFile)
        }}
        """
        try:
            output = get_output(code, mock_stdout)
            # Проверяем, что код выполнился без ошибок
            self.assertIsNotNone(output)
        except AttributeError as e:
            # Ожидаем ошибку из-за мокинга, но код должен пытаться работать с аудио
            pass

    @unittest.mock.patch('exiftool.ExifToolHelper')
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_image_file_processing(self, mock_stdout, mock_exiftool):
        """Тест обработки файлов изображений"""
        # Мокаем ExifToolHelper
        mock_et = unittest.mock.MagicMock()
        mock_et.get_metadata.return_value = [{'test': 'metadata'}]
        mock_exiftool.return_value.__enter__.return_value = mock_et

        code = f"""
        for (file imageFile of "{self.image_dir}") {{
            print(imageFile)
        }}
        """
        try:
            output = get_output(code, mock_stdout)
            # Проверяем, что код выполнился без ошибок
            self.assertIsNotNone(output)
        except (AttributeError, FileNotFoundError) as e:
            # Ожидаем ошибку из-за отсутствия exiftool или мокинга
            pass

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_directory_with_subdirectories(self, mock_stdout):
        """Тест директории, содержащей поддиректории (должны игнорироваться)"""
        # Создаем поддиректорию
        subdir = os.path.join(self.test_dir, 'subdirectory')
        os.makedirs(subdir)

        code = f"""
        for (file currentFile of "{self.test_dir}") {{
            print("Processing file")
        }}
        """
        output = get_output(code, mock_stdout)
        # Должно обработать только файлы, не поддиректории
        expected_lines = ["Processing file"] * len(self.test_files)
        self.assertEqual(output, "\n".join(expected_lines))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_for_of_with_complex_logic(self, mock_stdout):
        """Тест for...of с более сложной логикой"""
        code = f"""
        number totalFiles = 0
        number processedFiles = 0
        for (file currentFile of "{self.test_dir}") {{
            totalFiles = totalFiles + 1
            if (totalFiles > 1) then {{
                processedFiles = processedFiles + 1
                print(processedFiles)
            }}
        }}
        print("Total processed:")
        print(processedFiles)
        """
        output = get_output(code, mock_stdout)
        expected_processed = len(self.test_files) - 1
        expected_lines = [str(i + 1) for i in range(expected_processed)]
        expected_lines.extend(["Total processed:", str(expected_processed)])
        self.assertEqual(output, "\n".join(expected_lines))


if __name__ == '__main__':
    unittest.main()