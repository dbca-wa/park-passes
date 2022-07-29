<template>
    <!--router-view></router-view-->
    <div class="container" id="externalDash">
        <!--div v-if="is_debug">src/components/external/dashboard.vue</div-->
        <FormSection
            :formCollapse="false"
            label="Applications"
            subtitle="- View existing applications and lodge new ones"
            Index="applications"
        >
            <ApplicationsTable
                level="external"
            />
        </FormSection>


    </div>
</template>

<script>
import FormSection from "@/components/forms/SectionToggle.vue"
import ApplicationsTable from "@/components/common/TablePasses"

export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
        }
    },
    components:{
        FormSection,
        ApplicationsTable,
    },
    watch: {

    },
    computed: {
        is_debug: function(){
            return this.$route.query.hasOwnProperty('debug') && this.$route.query.debug == 'true' ? true : false
        },
        is_external: function() {
            return this.level == 'external'
        },
        is_internal: function() {
            return this.level == 'internal'
        },
    },
    methods: {
    },
    mounted: function () {
        // must be at top level of every page with <FormSection> component
        chevron_toggle.init();

    },
    created: function() {

    },
}
</script>
<style>


</style>
