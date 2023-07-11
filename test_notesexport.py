import os
import unittest
import shutil
from joplinexport import get_save_path, notebook_handling, note_handling
from joplinexport import notes_make

class TestNotesExport(unittest.TestCase):
    
    def setUp(self):
        self.notebook_name = "JoplinTestNotes"
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
        self.assertEqual(png_files, 0)

    def test_export_notes(self):
        results = notes_make.export_notes(self.notebook_name)
        self.assertEqual(results,
                         '<div id="Notes_200710_Monday" class="raw"><p class="date-box">Friday, July 10</p></div>This is the first note\n\nlinks to [Notes 200712 Wednesday](#Notes_200712_Wednesday)<div id="Notes_200711_Tuesday" class="raw"><p class="date-box">Saturday, July 11</p></div>Second Note\n\nwith a link to [Notes 200710 Monday](#Notes_200710_Monday)<div id="Notes_200712_Wednesday" class="raw"><p class="date-box">Sunday, July 12</p></div><div class="raw"><p class="date-box">Notes_Something_else</p></div>Here\'s the third note\n'
                        )
    
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



if __name__ == '__main__':
    unittest.main()
