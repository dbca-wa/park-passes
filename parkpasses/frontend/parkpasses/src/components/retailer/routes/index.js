import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'
import RetailerReports from '@/components/retailer/Reports.vue'
import SellPass from '@/components/retailer/SellPass.vue'
import RetailerGroupUserInviteResponse from '@/components/retailer/forms/RetailerGroupUserInviteResponse.vue'

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
            component: RetailerReports,
            name: 'retailer-reports'
        },
        {
            path: '/retailer/sell-a-pass',
            component: SellPass,
            name: 'sell-a-pass'
        },
        {
            path: '/retailer/respond-to-invite/:uuid/',
            component: RetailerGroupUserInviteResponse,
            name: 'retailer-respond-to-invite'
        },
        {
            path: '/retailer/sell-a-pass/:passTypeId/',
            component: SellPass,
            name: 'sell-a-pass-by-id'
        },
    ]
}
