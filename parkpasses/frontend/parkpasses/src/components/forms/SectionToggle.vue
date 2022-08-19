<template lang="html">
    <div class="card section-wrapper" :id="custom_id">
        <div class="card-header fw-bold h4" style='padding:30px;'>
            <div class='row'>
                <div class='col-10'>
                    {{ label }}
                </div>
                <div class='col-2 text-end'>
                    <i class="bi fw-bold down-chevron-close chevron-toggle" :data-bs-target="'#' +section_body_id"></i>
                </div>
            </div>
        </div>
        <div class="card-body" :id='section_body_id' >
            <slot></slot>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';

export default {
    name:"FormSection",
    props: {
        label: {},
        subtitle: {
            type: String,
            default: '',
        },
        Index: {},
        hideHeader: {},
    },
    data:function () {
        return {
            custom_id: uuid(),
        }
    },
    computed:{
        section_header_id: function () {
            return "section_header_"+this.Index;
        },
        section_body_id: function () {
            return "section_body_"+this.Index;
        },
    },
    methods: {

    },
    mounted: function() {

    },
    created: function() {

    },
}
</script>
<style scoped>

.section-wrapper {
    margin-bottom: 20px;
    padding: 0;
}

</style>
