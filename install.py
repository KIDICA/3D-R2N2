import os
import subprocess

DEFAULT_WEIGHTS = 'output/ResidualGRUNet/default_model/weights.npy'


def download_model(fn):
    if not os.path.isfile(fn):
        print('Downloading a pretrained model')
        subprocess.call(['curl', 'ftp://cs.stanford.edu/cs/cvgl/ResidualGRUNet.npy', '--create-dirs', '-o', fn])


download_model(DEFAULT_WEIGHTS)
