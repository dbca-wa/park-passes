<template lang="html">
    <div class="card section-wrapper" :id="custom_id">
        <div class="card-header fw-bold h4" style='padding:30px;'>
            <div class='row'>
                <div class='col-6'>
                    {{ label }}
                </div>
                <div class='col-6 text-end'>
                    <i class="bi fw-bold down-chevron-close chevron-toggle" :data-bs-target="'#' +section_body_id"></i>
                </div>
            </div>
        </div>
        <div class="card-body" :id='section_body_id' >
            <!--div id="ledger_ui_contact_details"></div-->
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
        /*
        noChevron: {
            default: false,
        },
        */
    },
    data:function () {
        return {
            custom_id: uuid(),
            /*
            title:"Section title",
            panel_chevron_class: null,
            chev_down_class_names: 'glyphicon glyphicon-chevron-down pull-right rotate_icon',
            chev_up_class_names:   'glyphicon glyphicon-chevron-down pull-right rotate_icon chev_rotated',
            */
        }
    },
    computed:{
        section_header_id: function () {
            return "section_header_"+this.Index;
        },
        section_body_id: function () {
            return "section_body_"+this.Index;
        },
        /*
        panel_collapse_class: function() {
            this.panel_chevron_class = this.chev_up_class_names
            return "card-body collapse in";
        },
        */
    },
    methods: {
        /*
        switchPanelChevronClass: function() {
            if (this.panel_chevron_class == this.chev_down_class_names) {
                this.panel_chevron_class = this.chev_up_class_names
            } else {
                this.panel_chevron_class = this.chev_down_class_names
            }
        },
        */
    },
    mounted: function() {
        /*
        let vm = this;
        $('#' + vm.custom_id).on('click',function () {
            vm.switchPanelChevronClass();
        });
        $('#mybutton').on('click', function(e) {
            console.log(e);
        });
        */
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
