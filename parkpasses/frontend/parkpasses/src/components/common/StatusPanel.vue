<template id="CommsLogs">
    <div class="">
        <div class="card card-default">
            <div class="card-header">
                Status
            </div>
            <div class="card-body card-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Status</strong><br/>
                        <template v-if="badge">
                            <span class="badge" :class="badgeClass">{{ status }}</span>
                        </template>
                        <template v-else>
                            {{ status }}
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { helpers } from '@/utils/hooks'

export default {

    name: "PassForm",
    props: {
        status: {
            required: true,
            type: String,
        },
        badge: {
            required: false,
            type: Boolean,
            default: false,
        },
        badgeClass: {
            required: false,
            type: String,
            default: false,
        }
    },
    components: {
        helpers
    },
    methods: {
        getBadgeClass: function (status) {
            return helpers.getStatusBadgeClass(status)
        }
    }
}
</script>
