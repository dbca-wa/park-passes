import { RouterView } from 'vue-router'

import RetailerDashboard from '@/components/retailer/Dashboard.vue'
import RetailerPassForm from '@/components/retailer/forms/PassForm.vue'
import RetailerReports from '@/components/retailer/Reports.vue'
import RetailerSellPass from '@/components/retailer/SellPass.vue'
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
            name: 'retailer-dash'
        },
        {
            path: '/retailer/passes/:passId/created-successfully',
            component: RetailerPassForm,
            name: 'retailer-pass-created-successfully',
            props: { created: true, }
        },
        {
            path: '/retailer/passes/:passId/',
            component: RetailerPassForm,
            name: 'retailer-pass-form'
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
            component: RetailerSellPass,
            name: 'retailer-sell-a-pass'
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
            component: RetailerSellPass,
            name: 'retailer-sell-a-pass-by-slug'
        },
    ]
}
