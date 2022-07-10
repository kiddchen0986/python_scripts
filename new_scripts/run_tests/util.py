import png

def read_image(image_path):
    temp = image_path.split('.')
    image_type = temp[len(temp) - 1]

    image = None
    if image_type == 'raw':
        with open(image_path, mode='rb') as f:
            image = f.read()

    elif image_type == 'png':
        png_reader = png.Reader(filename=image_path)
        w, h, pixels, metadata = png_reader.read_flat()
        image = pixels.tostring()
        #with open('ImageDriveImages.raw', 'wb') as f:
        #    f.write(image)

    return image
