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
                        {{ status }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "PassForm",
    props: {
        status: {
            required: true,
            type: String,
        }
    },
}
</script>
