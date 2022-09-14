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
                            <span :class="'badge ' + helpers.getBadgeClass(status)">{{ status }}</span>
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
        }
    },
    methods: {
        getBadgeClass: function () {
            switch(this.status) {
                case 'Current':
                    return 'bg-success'
                    break;
                case 'Future':
                    return 'bg-info';
                    break;
                case 'Expired':
                    return 'bg-danger';
                    break;
                case 'Cancelled':
                    return 'bg-danger';
                    break;
                default:
                    return 'org-badge-primary';
            }
        }
    }
}
</script>
