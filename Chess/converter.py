import base64

image = open('bpawn.png', 'rb')
image_read = image.read()
image_64_encode = base64.encodebytes(image_read)
with open('test.txt', 'wb') as f:
    f.write(image_64_encode)