Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> from rembg import remove
... from PIL import Image
... import io
... 
... def remove_background(input_path, output_path):
...     """
...     Remove background from image file and save the output.
... 
...     Args:
...     - input_path (str): Path to the input image file.
...     - output_path (str): Path to save the image with background removed.
...     """
...     # Open input image
...     with open(input_path, 'rb') as i:
...         input_data = i.read()
... 
...     # Remove background
...     output_data = remove(input_data)
... 
...     # Convert the result to an image
...     output_image = Image.open(io.BytesIO(output_data))
... 
...     # Save the output
...     output_image.save(output_path)
...     print(f"Background removed and saved to {output_path}")
... 
... if __name__ == "__main__":
...     # Example usage
...     input_file = "input_photo.jpg"       # replace with your photo path
...     output_file = "output_no_bg.png"     # better to save as PNG to preserve transparency
... 
