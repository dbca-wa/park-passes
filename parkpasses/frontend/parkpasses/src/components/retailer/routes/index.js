import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'

export default {
    path: '/retailer',
    component: RouterView,
    name: 'retailer',
    children: [
        {
            path: '/retailer',
            component: RetailerDashboard,
            name: 'retailer'
        },
    ]
}
