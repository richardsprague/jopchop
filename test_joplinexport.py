import os
import unittest
import shutil
from joplinexport import get_save_path, notebook_handling, note_handling

class TestJoplinExport(unittest.TestCase):
    
    def setUp(self):
        self.notebook_name = "JoplinTest"
        self.temp_dir = "test_downloads"
        os.makedirs(self.temp_dir, exist_ok=True)
        get_save_path(self.temp_dir)  # Assuming you have a variable in your joplinexport module that sets the download path
        
        # call your method to export the notebook files
        notebook_handling.export_notebook(self.notebook_name)  # Assuming you have a function that exports the files of the given notebook

    def tearDown(self):
        # remove the test directory after the test
        shutil.rmtree(self.temp_dir)

    def test_files_count(self):
        # count the number of .md and .png files
        md_files = len([name for name in os.listdir(self.temp_dir) if name.endswith(".md")])
        png_files = len([name for name in os.listdir(self.temp_dir) if name.endswith(".png")])
        self.assertEqual(md_files, 6)
        self.assertEqual(png_files, 2)
    
    def test_pandocable_filename(self):
        # test the pandocable_filename function
        result = note_handling.pandocable_filename("abc")
        expected = "abc"
        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")

        result = note_handling.pandocable_filename("hello, world")
        expected = "hello, world"
        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")

        result = note_handling.pandocable_filename("Daal: Lentils and Spinach")
        expected = "Daal- Lentils and Spinach"
        self.assertEqual(result, expected, f"Expected {expected}, but got {result}")

    def test_notes_notes(self):
        notes_files = sorted(note_handling.md_files(self.temp_dir))  # Sort the files
        self.assertEqual(len(notes_files),2)

        result = note_handling.concat_files(notes_files, before_str="")
        expected_result = (
            '<div id="Notes 230710 Monday" class="raw"><p class="date-box">Monday, July 10</p></div>\n\n<div id="Notes 230711 Tuesday" class="raw"><p class="date-box">Tuesday, July 11</p></div>\nSecond Note\n\nwith a link to [Notes 230710 Monday](Notes 230710 Monday.md)'
        )
        self.assertEqual(result, expected_result)



    def test_resource_link_replacement(self):
        download_path = self.temp_dir
        expected_resource_file = os.path.join(download_path, '572294a665a65a6def31c5593cb24c24.png')
        self.assertTrue(os.path.exists(expected_resource_file), f"{expected_resource_file} does not exist")

        with open(os.path.join(download_path, 'From OneDrive.md'), 'r', encoding='utf-8') as f:
            content = f.read()
            expected_link = '![572294a665a65a6def31c5593cb24c24.png](572294a665a65a6def31c5593cb24c24.png)'
            self.assertIn(expected_link, content, f"Expected link not found in file content")


if __name__ == '__main__':
    unittest.main()
