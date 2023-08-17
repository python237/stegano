import logging

from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def encrypt(image, text: str) -> Image or None:
    """
    Hide text in an image
    :param image: The image to use.
    :param text: Text to hide
    :return: The new image containing the hidden text.
    """
    try:
        img = Image.open(image)

        # We get the image size
        width, height = img.size

        # We split image in 3 color (red, green, blue)
        red, green, blue, opacity = img.split()
        red = list(red.getdata())

        # Get text information
        text_size = len(text)
        value = bin(text_size)[2:].rjust(8, "0")

        # We transform text to list where values must be between 0 and 1 && Transform list to text
        tmp_text = "".join([bin(ord(x))[2:].rjust(8, "0") for x in text])

        # --

        for j in range(8):
            red[j] = 2 * int(red[j]//2) + int(value[j])

        for j in range(8 * text_size):
            red[j + 8] = 2 * int(red[j + 8]//2) + int(tmp_text[j])

        # Create new image
        new_image = Image.new("L", (width, height))
        new_image.putdata(red)

        return Image.merge("RGB", (new_image, green, blue))

    except Exception as e:
        logging.info(f"[!] Error when adding text to image : { e }")
        return None


def decrypt(image) -> str or None:
    """
    Extract hidden information from an image
    :param image: The image to analyze and extract information if present.
    :return: Information extracted from the image
    """
    try:
        red, green, blue = Image.open(image).split()
        red = list(red.getdata())

        # Get text size
        size = int("".join([str(x % 2) for x in red[0:8]]), 2)

        # Read message
        blue = "".join([str(x % 2) for x in red[8:8*(size+1)]])
        message = ""

        for k in range(0, size):
            message = message + chr(int(blue[8*k:8*k+8], 2))

        return message

    except Exception as e:
        logging.info(f"[!] Error when searching for information in image : { e }")
        return None
