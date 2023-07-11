import unittest
import os
from io import StringIO
from unittest.mock import patch
from parafix import fixmal, hyphenate

class TestCode(unittest.TestCase):
    def test_fixmal(self):
        # Test case for fixmal function
        text = "ന്‍"
        expected_output = "ൻ"
        self.assertEqual(fixmal(text), expected_output)

    def test_hyphenate(self):
        # Test case for hyphenate function
        text = "മലയാളം"
        expected_output = "മല-യാളം"
        self.assertEqual(hyphenate(text), expected_output)

    def test_hyphenate_with_custom_hyphen(self):
        # Test case for hyphenate function with custom hyphen character
        text = "ബോവർനെഗെസ്"
        hyphen_char = "-"
        expected_output = "ബോവർ-നെ-ഗെസ്"
        self.assertEqual(hyphenate(text, hyphen_char), expected_output)

    def test_hyphenate_different_text(self):
        # Test case for hyphenate function with a different text
        text = "കന്നട"
        expected_output = "കന്നട"
        self.assertEqual(hyphenate(text), expected_output)

    def test_handle_input_file(self):
        # Test case for handling an input file
        input_file = "input.txt"
        output_file = "output.txt"
        expected_output = "മല-യാളം"

        # Create input file
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("മലയാളം")

        # Run the code with patching input and output filenames
        with patch("sys.argv", ["parafix.py", "-i", input_file, "-o", output_file]):
            os.system("python parafix.py")  # Execute the code

        # Read the output file
        with open(output_file, "r", encoding="utf-8") as f:
            output_content = f.read()

        # Assert the output content
        self.assertEqual(output_content.strip(), expected_output)

        # Clean up files
        os.remove(input_file)
        os.remove(output_file)

    def test_handle_unsupported_file_type(self):
        # Test case for handling an unsupported file type
        input_file = "image.jpg"
        expected_output = "Sorry! image/jpeg is not currently supported."

        # Run the code with patching input filename
        with patch("sys.argv", ["parafix.py", "-i", input_file]):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                os.system("python parafix.py")  # Execute the code
                output = fake_out.getvalue().strip()

        # Assert the output message
        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()