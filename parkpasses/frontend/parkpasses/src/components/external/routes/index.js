import { RouterView } from 'vue-router'
import ShopHome from '@/components/external/ShopHome.vue'
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
    ]
}
