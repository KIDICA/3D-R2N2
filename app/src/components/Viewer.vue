<template>
  <div>
    <div ref="viewer" style="position: fixed;left: 0;right: 0;top:0;bottom: 0;"></div>
    <busy ref="busy"></busy>
    <toolbar>
      <slot>
        <div class="row">
          <div class="col"></div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="print">
              <font-awesome icon="print" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="trash">
              <font-awesome icon="trash" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="plus">
              <font-awesome icon="search-plus" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col-2 text-center p-0">
            <button class="btn cam mb-1 text-primary" @click="minus">
              <font-awesome icon="search-minus" class="fa-2x text-primary"></font-awesome>
            </button>
          </div>
          <div class="col"></div>
        </div>
      </slot>

    </toolbar>
  </div>
</template>

<script>
  import * as THREE from "three-full";
  import Toolbar from "./Toolbar";
  import Busy from "./Busy";

  export default {
    name: "Viewer",
    components: {
      "toolbar": Toolbar,
      "busy": Busy,
    },
    data() {
      return {
        busy: false,
      }
    },
    watch: {
      busy(val) {
        this.$refs.busy.work = val;
      },
    },
    methods: {
      trash() {
        alert('trash');
      },
      print() {
        alert("print");
      },
      plus() {
        this.camera.zoom += 0.1;
        this.camera.updateProjectionMatrix();
      },
      minus() {
        this.camera.zoom -= 0.1;
        this.camera.updateProjectionMatrix();
      }
    },
    mounted() {
      this.busy = true;
      const renderer = new THREE.WebGLRenderer({antialias: true});
      const scene = new THREE.Scene();
      scene.background = new THREE.Color('white');

      const group = new THREE.Group();

      scene.add(group);
      const axesHelper = new THREE.AxesHelper(5);
      group.add(axesHelper);

      const el = this.$refs.viewer;
      renderer.setSize(el.offsetWidth, el.offsetHeight);
      this.$refs.viewer.appendChild(renderer.domElement);

      const fov = 30;
      const aspect = 2;  // the canvas default
      const near = 0.1;
      const far = 100;

      const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
      camera.position.set(0, 20, 5);
      camera.lookAt(0, 0, 0);

      this.controls = new THREE.OrbitControls(camera, this.$refs.viewers);
      this.controls.enablePan = false;
      this.controls.panSpeed = 0.0001;

      const hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 1);
      hemiLight.color.setHSL(0.6, 1, 0.6);
      hemiLight.groundColor.setHSL(0.095, 1, 0.75);
      hemiLight.position.set(0, 500, 0);
      scene.add(hemiLight);

      //const material = new THREE.MeshPhongMaterial();
      const material = new THREE.MeshNormalMaterial();
      //material.color.setHex(0xf0f0f0);
      //material.flatShading = true;
      const loader = new THREE.OBJLoader();
      // Force reload
      loader.load('/voxel/prediction.obj?' + new Date().getTime(), obj => {
        obj.traverse(function (child) {
          if (child instanceof THREE.Mesh) {
            child.material = material;
          }
        });

        // Center geometry.
        const box = new THREE.Box3().setFromObject(obj);
        const x = (box.max.x - box.min.x) / 2;
        const z = (box.max.y - box.min.z) / 2;
        const y = (box.max.y - box.min.y) / 2;

        obj.position.x = -x;
        obj.position.z = -z;
        obj.position.y = 0;

        group.add(obj);

        // Angle from above slightly lowered.
        camera.position.x = x * 8;
        camera.position.z = 0;
        camera.position.y = y * 2;
        camera.lookAt(new THREE.Vector3(0, -y, 0));

        this.camera = camera;

        this.controls.target.set(0, y, 0);
        this.controls.update();

        this.busy = false;

        // Continuous rotation around a center point.
        const rad = Math.PI / 200;

        function animate() {
          requestAnimationFrame(animate);
          group.rotation.y += rad;
          renderer.render(scene, camera);
        }

        animate();
      });
    }
  }
</script>

<style scoped>
</style>