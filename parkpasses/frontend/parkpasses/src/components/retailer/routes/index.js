import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'
import SellPass from '@/components/retailer/SellPass.vue'

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
        {
            path: '/retailer/parkpasses',
            component: RetailerDashboard,
            name: 'retailer-park-passes'
        },
        {
            path: '/retailer/reports',
            component: RetailerDashboard,
            name: 'retailer-park-passes'
        },
        {
            path: '/retailer/sell-a-pass',
            component: SellPass,
            name: 'sell-a-pass'
        },
        {
            path: '/retailer/sell-a-pass/:passTypeId/',
            component: SellPass,
            name: 'sell-a-pass-by-id'
        },
    ]
}
