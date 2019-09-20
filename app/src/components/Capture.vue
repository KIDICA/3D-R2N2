<template>
  <div class="align-middle">
    <busy ref="busy"></busy>

    <form style="display: none" ref="form" method="post" enctype="multipart/form-data">
      <input ref="inputFile" name="file" type="file" accept="image/jpeg,image/jpg,image/png;capture=camera">
    </form>

    <video ref="cam" class="bg-light" autoplay="true" playsInline></video>
    <!--<audio style="display: none" ref="click" src="./sound/camera.mp3"></audio>-->

    <toolbar>
      <slot>
        <div class="row">
          <div class="col"></div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="capture" v-bind:disabled="busy">
              <font-awesome icon="camera" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="render">
              <font-awesome icon="print" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="render">
              <font-awesome icon="cube" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col"></div>
        </div>
      </slot>
    </toolbar>
  </div>
</template>

<script>
  import CameraPhoto, {FACING_MODES, IMAGE_TYPES} from "jslib-html5-camera-photo";
  import imageHelper from "../utils/image";
  import Toolbar from "./Toolbar";
  import Busy from "./Busy";

  export default {
    name: "kdc-capture",
    components: {
      "toolbar": Toolbar,
      "busy": Busy,
    },
    data() {
      return {
        resourceUrl: "/upload",
        busy: false,
      };
    },
    watch: {
      busy(val) {
        this.$refs.busy.work = val;
      },
    },
    methods: {
      render() {

      },
      capture() {
        this.busy = true;
        //this.$refs.click.play();
        const settings = this.cameraPhoto.getCameraSettings();
        settings.imageType = IMAGE_TYPES.PNG;
        //settings.imageCompression = 0.80;
        const dataUri = this.cameraPhoto.getDataUri(settings);
        this.$refs.cam.pause();
        const blob = imageHelper.dataURItoBlob(dataUri);
        this.upload(blob)
          .then(response => {
            const data = response.data;
            this.$log.debug(data);
            this.$emit("snapshot", data);
            this.busy = false;
            this.$refs.cam.play();
          })
          .catch(error => {
            this.busy = false;
            this.$refs.cam.play();
            this.$log.error(error);
          });
      },
      upload(file) {
        return new Promise((resolve, reject) => {
          const formData = new FormData(this.$refs.form);
          formData.append("file", file, "file.png");
          this.$http.post(this.resourceUrl, formData)
            .then(response => {
              resolve(response);
            })
            .catch(error => {
              this.$log.error(error);
              reject(error);
            });
        });
      },
    },
    mounted() {
      this.cameraPhoto = new CameraPhoto(this.$refs.cam);
      this.cameraPhoto.startCamera(FACING_MODES.ENVIRONMENT, {width: 200, height: 200})
        .then(stream => {
          this.$log.debug("Camera started");
        })
        .catch(error => {
          alert(error);
          this.$log.error(error);
        });
    },
    beforeRouteLeave(to, from, next) {
      this.cameraPhoto.stopCamera()
        .then(() => {
          this.$log.debug("Camera stopped");
          next();
        })
        .catch((error) => {
          this.$log.error("No camera to stop:", error);
          next();
        });
    },
  };
</script>

<style scoped>
  video {
    left: 0;
    right: 0;
    margin: 0;
    padding: 0;
    position: fixed;
    width: 100%;
    top: 20%;
    height: auto;
  }

  .cam {
    border: 2px solid;
    border-radius: 2em;
    padding: 0.5em;
  }
</style>