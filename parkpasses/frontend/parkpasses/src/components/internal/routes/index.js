
import { RouterView } from 'vue-router'
import InternalDashboard from '@/components/internal/dashboard.vue'

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
