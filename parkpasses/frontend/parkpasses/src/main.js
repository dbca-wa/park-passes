
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App'
import helpers from '@/utils/helpers'
import { useStore } from '@/stores/state'
import CKEditor from '@ckeditor/ckeditor5-vue';
import('@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css')
import('@/../node_modules/select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css')
import('@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css')

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

app.use(CKEditor);
app.use(router);
app.use(pinia);

router.isReady().then(() => app.mount('#app'));

const store = useStore();
store.fetchUserData();
