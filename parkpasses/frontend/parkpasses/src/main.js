// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue'
import router from './router'
import App from './App'
import helpers from '@/utils/helpers'
import hooks from './packages'
import api_endpoints from './api'
import CKEditor from '@ckeditor/ckeditor5-vue';
require('@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css')
require('@/../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css')
require('@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css')

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

const app = createApp(App)

app.use(CKEditor)
app.use(router)
router.isReady().then(() => app.mount('#app'))
