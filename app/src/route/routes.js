import Capture from "../components/Capture";
import Viewer from "../components/Viewer";

/**
 * @type {
 * [{
 *   path: String,
 *   component: Vue
 * }]}
 */
const routes = [
  {path: '/', component: Capture},
  {path: '/viewer', component: Viewer},
];

export default routes;