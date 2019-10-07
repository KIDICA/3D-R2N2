import logging
import socket
import subprocess
import sys

import tornado.ioloop
import tornado.options
import tornado.web
import signal
import os

from PIL import Image
from models import load_model
from lib.config import cfg, cfg_from_list
from lib.solver import Solver
from lib.voxel import voxel2obj
import numpy as np

verbose = ((sys.argv[1] if 1 < len(sys.argv) else "") == "verbose")

# For SSL pass through a proxy.
PORT = 8000

# Number of images taken before a voxel model is generated.
IMAGE_COUNT = 4

# Paths
STATIC_APP_FOLDER = os.path.join(os.path.dirname(__file__), 'app/dist')
STATIC_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
STATIC_VOXEL_FOLDER = os.path.join(os.path.dirname(__file__), 'voxel')

# This is where the temp image will go
EXPORT_LOCATION = "/tmp"

STATIC_IMG_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "img"
)

DEFAULT_WEIGHTS = 'output/ResidualGRUNet/default_model/weights.npy'


def parse_static_filepath(filepath):
    split_filepath = filepath.split('/')
    while len(split_filepath) > 2:
        split_filepath.pop(0)

    return '/'.join(split_filepath)


def run_model(filename):
    pass


def copy_file(old="avon.png", new="avon.png"):
    command_string = "cp " + old + " " + new
    subprocess.check_output(command_string.split(" "))


def load_demo_images():
    ims = []
    files = []

    for i in range(IMAGE_COUNT):
        file = 'uploads/%d.png' % i
        files.append(file)
        im = Image.open(file)
        ims.append([np.array(im).transpose((2, 0, 1)).astype(np.float32) / 255.])
    return np.array(ims), files


def render():
    # Save prediction into a file named 'prediction.obj' or the given argument
    pred_file_name = sys.argv[1] if len(sys.argv) > 1 else 'voxel/prediction.obj'

    demo_imgs, files = load_demo_images()
    NetClass = load_model('ResidualGRUNet')

    net = NetClass(compute_grad=False)  # instantiate a network
    net.load(DEFAULT_WEIGHTS)  # load downloaded weights
    solver = Solver(net)  # instantiate a solver

    voxel_prediction, _ = solver.test_output(demo_imgs)

    # Save the prediction to an OBJ file (mesh file).
    voxel2obj(pred_file_name, voxel_prediction[0, :, 1, :, :] > cfg.TEST.VOXEL_THRESH)

    return files, pred_file_name


class UploadHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        """Allow CORS."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self, name=None):
        try:
            self.application.logger.info("Recieved a file")
            file = self.request.files['file'][0]
            pngs = [file for file in os.listdir("uploads/") if file.endswith('.png')]
            count = len(pngs)
            filename = f"{count}.png"
            output_file = open("uploads/" + filename, 'wb')
            output_file.write(file['body'])
            output_file.close()

            im = Image.open(f"uploads/{filename}")
            # Has to be this exact size, the NN has this input shape, also 24-bit png.
            im = im.resize((127, 127), Image.ANTIALIAS).convert('RGB')
            im.save("uploads/" + filename, "PNG")

            if len([file for file in os.listdir("uploads/") if file.endswith('.png')]) >= IMAGE_COUNT:
                files, prediction_file = render()
                print("Building model based on:", files)
                for file in files:
                    os.remove(file)
                self.write({'prediction': prediction_file})

            self.finish()
        except Exception as err:
            print("Error", err)


class MainApplication(tornado.web.Application):
    is_closing = False

    def signal_handler(self, signum, frame):
        logging.info('exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            tornado.ioloop.IOLoop.instance().stop()
            logging.info('exit success')

    def __init__(self, **settings):
        tornado.web.Application.__init__(self, **settings)
        # Add in various member variables here that you want the handlers to be aware of
        # e.g. a database client

        # Add the handlers here - use regular expressions or hardcoded paths to link the endpoints
        # with handlers?
        self.port = settings.get('port', PORT)
        self.address = settings.get('address', "0.0.0.0")
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.logger = logging.getLogger()
        self.ssl_options = {"certfile": os.path.join("config/server.crt"), "keyfile": os.path.join("certs/server.key")}

        # Tie the handlers to the routes here
        self.add_handlers(".*", [
            (r"/upload", UploadHandler),
            (r"/voxel/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_VOXEL_FOLDER}),
            (r"/uploads/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_UPLOAD_FOLDER}),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_APP_FOLDER}),
        ])

    def run(self):
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            self.listen(self.port, self.address)
            tornado.ioloop.PeriodicCallback(self.try_exit, 100).start()

        except socket.error as e:
            self.logger.fatal("Unable to listen on {}:{} = {}".format(
                self.address, self.port, e))
            sys.exit(1)
        self.ioloop.start()


if __name__ == "__main__":
    tornado.options.define('port', default=PORT, help='Port to listen on.')

    host = "0.0.0.0"
    if sys.platform == "win32":
        host = "127.0.0.1"

    tornado.options.define('address', default=host, help='Url')

    tornado.options.parse_command_line()
    options = tornado.options.options.as_dict()

    if verbose:
        print(options)

    app = MainApplication(**options)
    app.run()
