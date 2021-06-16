import numpy as np
import scipy.io


def matlab_to_arrays(filename):
    arrays = []
    mat = scipy.io.loadmat(filename)
    for content in mat.values():
        if isinstance(content, np.ndarray):
            arrays.append(np.asarray(content))
    return arrays


def get_matlab_model(filename):
    arrays = matlab_to_arrays(filename)
    info = arrays[0][0]
    type = info[0].decode()
    arch = info[2].decode()
    layers = info[3].flatten()
    weights = arrays[1]
    return weights, (type, arch, layers)


if __name__ == '__main__':
    filename = 'D:/Personal/Crick/oRAScle i2i pathology/DeepHistology-0.2/networks/resnet18_512.mat'
    model_params = get_matlab_model(filename)
    print(model_params)
