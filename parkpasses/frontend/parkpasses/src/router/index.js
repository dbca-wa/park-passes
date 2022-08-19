import { createRouter, createWebHistory } from 'vue-router'
import ExternalRoutes from '@/components/external/routes'
import InternalRoutes from '@/components/internal/routes'
import RetailerRoutes from '@/components/retailer/routes'

var NotFoundComponent = null

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/:pathMatch(.*)',
            component: NotFoundComponent
        },
        ExternalRoutes,
        InternalRoutes,
        RetailerRoutes,
    ]
})

export default router;
