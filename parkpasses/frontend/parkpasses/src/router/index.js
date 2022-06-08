import { createRouter, createWebHistory } from 'vue-router'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'

var NotFoundComponent = null

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/:pathMatch(.*)',
            component: NotFoundComponent
        },
        external_routes,
        internal_routes,
    ]
})

export default router;
