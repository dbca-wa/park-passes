import { RouterView } from 'vue-router'
import ShopHome from '@/components/external/ShopHome.vue'
import FAQs from '@/components/external/FAQs.vue'
import PurchaseVoucher from '@/components/external/PurchaseVoucher.vue'
import PurchasePass from '@/components/external/PurchasePass.vue'
import Checkout from '@/components/external/Checkout.vue'

export default {
    path: '/',
    component: RouterView,
    name: 'external',
    children: [
        {
            path: '/',
            component: ShopHome,
            name: 'external'
        },
        {
            path: '/faq',
            component: FAQs,
            name: 'faqs'
        },
        {
            path: '/purchase-voucher',
            component: PurchaseVoucher,
            name: 'purchase-voucher'
        },
        {
            path: '/purchase-pass/:passTypeId',
            component: PurchasePass,
            name: 'purchase-pass'
        },
        {
            path: '/checkout',
            component: Checkout,
            name: 'checkout'
        },
    ]
}
