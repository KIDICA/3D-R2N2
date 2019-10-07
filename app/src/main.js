import Vue from 'vue';
import App from './App.vue';
import {library} from "@fortawesome/fontawesome-svg-core";
import axios from "axios";
import router from "./route/router";

import {
  faCamera,
  faUpload,
  faCube,
  faPrint,
  faTrash,
  faSearchPlus,
  faSearchMinus
} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";

// |========================================================|
// | Application bootstrapping                              |
// |========================================================|

// Include them one by one to keep the binary small.
library.add(faPrint, faCube, faCamera, faUpload, faTrash, faSearchPlus, faSearchMinus);
Vue.component("font-awesome", FontAwesomeIcon);

const c = window.console;
Vue.prototype.$log = {
  info(...args) {
    c.info.apply(undefined, args);
  },
  error(...args) {
    c.error.apply(undefined, args);
  },
  debug(...args) {
    c.debug.apply(undefined, args);
  },
  success(...args) {
    c.success.apply(undefined, args);
  }
};

Vue.prototype.$http = axios.create();

Vue.config.productionTip = false;

new Vue({
  router,
  render: h => h(App),
}).$mount('#app');
