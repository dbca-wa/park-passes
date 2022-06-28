import { RouterView } from 'vue-router'
import ExternalDashboard from '@/components/external/Dashboard.vue'
export default
{
    path: '/external',
    component: RouterView,
    name: 'external-dashboard',
    children: [
        {
            path: '/external',
            component: ExternalDashboard,
            name: 'external-dashboard'
        },
    ]
}
