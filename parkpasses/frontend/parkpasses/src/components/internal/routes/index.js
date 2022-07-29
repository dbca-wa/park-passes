
import { RouterView } from 'vue-router'
import InternalDashboard from '@/components/internal/Dashboard.vue'
import InternalVouchers from '@/components/internal/Vouchers.vue'
import InternalDiscountCodes from '@/components/internal/DiscountCodes.vue'

export default
{
    path: '/internal',
    component: RouterView,
    children: [
        {
            path: '/internal',
            component: InternalDashboard
        },
        {
            path: '/internal/vouchers',
            component: InternalVouchers,
            name: 'internal-vouchers'
        },
        {
            path: '/internal/discount-codes',
            component: InternalDiscountCodes,
            name: 'innteral-discount-codes'
        },
    ]
}
