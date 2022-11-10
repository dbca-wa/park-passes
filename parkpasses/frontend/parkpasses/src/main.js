
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App'
import helpers from '@/utils/helpers'
import { useStore } from '@/stores/state'
import CKEditor from '@ckeditor/ckeditor5-vue';
import { extendMoment } from 'moment-range';
import titleMixin from './mixins/titleMixin'

import "datatables.net";
import "datatables.net-bs5";
import "datatables.net-buttons";
import "datatables.net-buttons-bs5";
import "datatables.net-responsive";
import "datatables.net-responsive-bs5";
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

import "select2";
import "currency.js";
import "sweetalert2/dist/sweetalert2.css";

extendMoment(moment);

import '@fortawesome/fontawesome-free/css/all.min.css';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.min.css';
import 'datatables.net-bs5/css/dataTables.bootstrap5.min.css';
import 'datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css';

// Add CSRF Token to every request
const customHeaders = new Headers({
    'X-CSRFToken': helpers.getCookie( 'csrftoken' ),
});
const customHeadersJSON = new Headers({
    'X-CSRFToken': helpers.getCookie( 'csrftoken' ),
    'Content-Type': 'application/json',
});
fetch = (originalFetch => {
    return (...args) => {
        if (args.length > 1) {
            if (typeof(args[1].body) === 'string') {
                args[1].headers = customHeadersJSON;
            } else {
                args[1].headers = customHeaders;
            }
        }
        const result = originalFetch.apply(this, args);
        return result;
    };
})(fetch);

const pinia = createPinia();

const app = createApp(App);

app.mixin(titleMixin);

app.use(CKEditor);
app.use(router);
app.use(pinia);

router.isReady().then(() => app.mount('#app')).catch(console.error).then(console.log);

const store = useStore();
store.fetchUserData();
