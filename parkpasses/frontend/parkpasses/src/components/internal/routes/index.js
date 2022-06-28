
import { RouterView } from 'vue-router'
import InternalDashboard from '@/components/internal/Dashboard.vue'

export default
{
    path: '/internal',
    component: RouterView,
    children: [
        {
            path: '/internal',
            component: InternalDashboard
        },
    ]
}
