import scipy.io as sio
import io
import matplotlib.pyplot as plt
import numpy as np
import base64


def show_model(data, dx):
    mat_contents = sio.loadmat(data)
    keys = sorted(mat_contents.keys())
    pressure_field = mat_contents[keys[0]]
    figure = plt.figure(figsize=(5, 5))

    n = pressure_field.shape[0]
    extent = [- n * dx / 2, n * dx / 2, - n * dx / 2, n * dx / 2]
    im = plt.matshow(np.abs(pressure_field), fignum=figure.number, extent=extent)
    plt.colorbar()
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png')
    buffer.seek(0)
    result_image = base64.b64encode(buffer.getvalue())
    return result_image.decode('ascii')
