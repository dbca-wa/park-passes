import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'
export default

{
    path: '/retailer',
    component: RouterView,
    name: 'external',
    children: [
        {
            path: '/retailer',
            component: ShopHome,
            name: 'retailer'
        },
    ]
}
