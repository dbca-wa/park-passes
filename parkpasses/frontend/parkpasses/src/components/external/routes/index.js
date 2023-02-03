import { RouterView } from 'vue-router'
import ShopHome from '@/components/external/ShopHome.vue'
import FAQs from '@/components/external/FAQs.vue'
import Help from '@/components/external/Help.vue'
import YourParkPasses from '@/components/external/YourParkPasses.vue'
import YourOrders from '@/components/external/YourOrders.vue'
import Cart from '@/components/external/Cart.vue'
import CheckoutSuccess from '@/components/external/CheckoutSuccess.vue'

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
            path: '/purchase-voucher/',
            component: ShopHome,
            name: 'purchase-voucher'
        },
        {
            path: '/purchase-pass/:passTypeSlug/',
            component: ShopHome,
            name: 'purchase-pass'
        },
        {
            path: '/cart/',
            component: Cart,
            name: 'cart'
        },
        {
            path: '/checkout-success/:uuid/',
            component: CheckoutSuccess,
            name: 'checkout-success'
        },
        {
            path: '/your-park-passes/',
            component: YourParkPasses,
            name: 'your-park-passes'
        },
        {
            path: '/your-orders/',
            component: YourOrders,
            name: 'your-orders'
        },
        {
            path: '/faq/',
            component: FAQs,
            name: 'faqs'
        },
        {
            path: '/help/',
            component: Help,
            name: 'help'
        },
    ]
}
