import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'
import RetailerReports from '@/components/retailer/Reports.vue'
import SellPass from '@/components/retailer/SellPass.vue'
import RetailerGroupUsers from '@/components/retailer/RetailerGroupUsers.vue'
import RetailerInviteRetailerGroupUser from '@/components/retailer/forms/InviteRetailerGroupUser.vue'
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
            path: '/retailer/users',
            component: RetailerGroupUsers,
            name: 'retailer-retailer-group-users'
        },
        {
            path: '/retailer/sell-a-pass',
            component: SellPass,
            name: 'sell-a-pass'
        },
        {
            path: '/retailer/invite-a-user',
            component: RetailerInviteRetailerGroupUser,
            name: 'retailer-invite-user'
        },
        {
            path: '/retailer/respond-to-invite/:uuid/',
            component: RetailerGroupUserInviteResponse,
            name: 'retailer-respond-to-invite'
        },
        {
            path: '/retailer/sell-a-pass/:passTypeSlug/',
            component: SellPass,
            name: 'sell-a-pass-by-id'
        },
    ]
}
