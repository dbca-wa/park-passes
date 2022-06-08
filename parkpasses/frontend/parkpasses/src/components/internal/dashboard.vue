<template>
    <div class="container" id="externalDash">
        <div v-if="is_debug">src/components/internal/dashboard.vue</div>
        <ul class="nav nav-pills" id="pills-tab" role="tablist">
            <li class="nav-item">
                <a
                    class="nav-link"
                    id="pills-applications-tab"
                    data-bs-toggle="pill"
                    href="#pills-applications"
                    role="tab"
                    aria-controls="pills-applications"
                    aria-selected="true"
                    @click="tabClicked('applications')"
                >Applications</a>
            </li>
        </ul>

        <div class="tab-content" id="pills-tabContent">
            <div class="tab-pane active" id="pills-applications" role="tabpanel" aria-labelledby="pills-applications-tab">
                <FormSection :formCollapse="false" label="Applications" Index="applications">
                    <ApplicationsTable
                        ref="applications_table"
                        level="internal"
                        filterApplicationType_cache_name="filterApplicationTypeForApplicationTabley"
                        filterApplicationStatus_cache_name="filterApplicationStatusForApplicationTable"
                        filterApplicationLodgedFrom_cache_name="filterApplicationLodgedFromForApplicationTable"
                        filterApplicationLodgedTo_cache_name="filterApplicationLodgedToForApplicationTable"
                    />
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import ApplicationsTable from "@/components/common/table_proposals"

export default {
    name: 'InternalDashboard',
    data() {
        let vm = this;
        return {
            accessing_user: null,
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
        tabClicked: function(param){
            if (param == 'applications'){
                this.$refs.applications_table.adjust_table_width()
                this.$refs.applications_referred_to_me_table.adjust_table_width()
            } else if (param === 'competitive-processes'){
                this.$refs.competitive_processes_table.adjust_table_width()
            }
        },
        mapTabClicked: function(){
            this.$refs.component_map_with_filters.forceToRefreshMap()
        },
        set_active_tab: function(tab_href_name){
            let elem = $('#pills-tab a[href="#' + tab_href_name + '"]')
            let tab = bootstrap.Tab.getInstance(elem)
            if(!tab)
                tab = new bootstrap.Tab(elem)
            tab.show()
        },
        /*
        addEventListener: function(){
            let elems = $('a[data-bs-toggle="pill"]')
            console.log('---')
            console.log(elems)
            elems.on('click', function (e) {
                console.log('click: ')
                console.log(e.target);
            })
        }
        */
    },
    mounted: async function () {
        //let vm = this
        /*
        const res = await fetch('/api/profile');
        const resData = await res.json();
        this.accessing_user = resData
        */
        this.$nextTick(function(){
            //vm.addEventListener()
            chevron_toggle.init();
            this.set_active_tab('pills-applications')
        })
    },
    created: function() {

    },
}
</script>

<style lang="css" scoped>
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }

    .nav-item {
        margin-bottom: 2px;
    }

    .nav-item>li>a {
        background-color: yellow !important;
        color: #fff;
    }

    .nav-item>li.active>a, .nav-item>li.active>a:hover, .nav-item>li.active>a:focus {
      color: white;
      background-color: blue;
      border: 1px solid #888888;
    }

	.admin > div {
	  display: inline-block;
	  vertical-align: top;
	  margin-right: 1em;
	}
    .nav-pills .nav-link {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
        border-top-left-radius: 0.5em;
        border-top-right-radius: 0.5em;
        margin-right: 0.25em;
    }
    .nav-pills .nav-link {
        background: lightgray;
    }
    .nav-pills .nav-link.active {
        background: gray;
    }
</style>
