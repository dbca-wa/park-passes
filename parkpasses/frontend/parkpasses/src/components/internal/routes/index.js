
import { RouterView } from 'vue-router'
import InternalDashboard from '@/components/internal/Dashboard.vue'

import InternalPricingWindows from '@/components/internal/PricingWindows.vue'
import InternalPricingWindowForm from '@/components/internal/forms/PricingWindowForm.vue'

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
            path: '/internal/pricing-windows',
            component: InternalPricingWindows,
            name: 'internal-pricing-windows'
        },
        {
            path: '/internal/pricing-windows/:pricingWindowId',
            component: InternalPricingWindowForm,
            name: 'internal-pricing-window-form'
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
