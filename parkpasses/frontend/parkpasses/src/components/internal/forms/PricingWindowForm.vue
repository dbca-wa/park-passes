<template>
<div class="container" id="pricingWindowForm">
    <div class="row">
        <h3>{{ pricing_window.name }}</h3>
        <div class="col-md-3">
            <CommsLogs :commsUrl="commsUrl" :logsUrl="logsUrl" :comms_add_url="comms_add_url" :disableAddEntry="false"/>
            <div class="row">
                <div class="card card-default">
                    <div class="card-header">
                        Workflow
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ pricing_window.status }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div class="card card-default">
                  <div class="card-header">
                      <h3 class="card-title">
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse" expanded="true"  data-parent="#userInfo" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                </div>
            </div>

        </div>
    </div>
</div>
</template>

<script>
export default {
    name: "PricingWindowForm",
    props: {
        pricing_window_id:{
            type: Number,
            required: true,
        },
    },
    data() {
        return {

        }
    },
    computed: {

    },
    methods: {

    },

}
</script>

<style scoped>

</style>
