import { RouterView } from 'vue-router'
import ShopHome from '@/components/external/ShopHome.vue'
import PurchaseVoucher from '@/components/external/PurchaseVoucher.vue'
import PurchasePass from '@/components/external/PurchasePass.vue'
import Checkout from '@/components/external/Checkout.vue'
import ExternalDashboard from '@/components/external/Dashboard.vue'
export default
/*[{
    path: '/',
    component: RouterView,
    name: 'shop',
    children: [
        {
            path: '/',
            component: ShopHome,
            name: 'shop-home'
        },
    ]
},]*/
{
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
