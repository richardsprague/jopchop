import os
import unittest
import shutil
from joplinexport import get_save_path, notebook_handling

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
        self.assertEqual(md_files, 4)
        self.assertEqual(png_files, 1)

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
