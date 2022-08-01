<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="CollapsibleFilters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Pass Type</label>
                        <select class="form-control" v-model="filterPassType">
                            <option value="" selected="selected">All</option>
                            <option v-for="passType in passTypesDistinct" :value="passType.code">{{ passType.description }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterPassProcessingStatus">
                            <option value="">All</option>
                            <option v-for="processingStatus in passProcessingStatusesDistinct" :value="processingStatus.code">{{ processingStatus.description }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6 text-end">
                    <button class="dt-button buttons-csv buttons-html5 btn btn-primary">Upload Personnel Passes</button>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Start Date From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterPassDatetimeStartFrom">
                            <!--
                            <span class="input-group-addon">
                                <span class="fa fa-calendar"></span>
                            </span>
                            -->
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Start Date To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterPassDatetimeStartTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{errorMessage}}</div>
        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="passDatatable"
                    :id="datatable_id"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { api_endpoints } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'

export default {
    name: 'TablePasses',
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        filterPassProcessingStatusCacheName: {
            type: String,
            required: false,
            default: 'filterPassProcessingStatus',
        },
        filterPassTypeCacheName: {
            type: String,
            required: false,
            default: 'filterPassType',
        },
        filterPassDatetimeStartFromCacheName: {
            type: String,
            required: false,
            default: 'filterPassDatetimeStartFrom',
        },
        filterPassDatetimeStartToCacheName: {
            type: String,
            required: false,
            default: 'filterPassDatetimeStartTo',
        },

    },
    data() {
        let vm = this;
        return {
            datatable_id: 'passes-datatable-' + uuid(),

            filterPassType: '',
            filterPassProcessingStatus: sessionStorage.getItem(vm.filterPassProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterPassProcessingStatusCacheName) : '',
            filterPassDatetimeStartFrom: '',
            filterPassDatetimeStartTo: '',

            errorMessage: null,

            // filtering options
            passTypesDistinct: [],
            passProcessingStatusesDistinct: [],

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },

            // For Expandable row
            tdExpandClassName:      'expand-icon',
            tdCollapseClassName:    'collapse-icon',
            expandableRowClassName: 'expandableRowClassName',
        }
    },
    components:{
        datatable,
        CollapsibleFilters,
    },
    watch: {
        filterPassType: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassTypeCacheName, this.filterPassType);
        },
        filterPassProcessingStatus: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassProcessingStatusCacheName, this.filterPassProcessingStatus);
        },
        filterPassDatetimeStartFrom: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassDatetimeStartFromCacheName, this.filterPassDatetimeStartFrom);
        },
        filterPassDatetimeStartTo: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassDatetimeStartToCacheName, this.filterPassDatetimeStartTo);
        },
        filterApplied: function() {
            if (this.$refs.CollapsibleFilters){
                this.$refs.CollapsibleFilters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        number_of_columns: function() {
            let num =  this.$refs.passDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(
                this.filterPassProcessingStatus.toLowerCase() === 'all' &&
                this.filterPassType.toLowerCase() === 'all' &&
                this.filterPassDatetimeStartFrom.toLowerCase() === '' &&
                this.filterPassDatetimeStartTo.toLowerCase() === ''
            ){
                filter_applied = false
            }
            return filter_applied
        },
        debug: function(){
            if (this.$route.query.debug){
                return this.$route.query.debug === 'true'
            }
            return false
        },
        dtHeaders: function(){
            return [
                'id',
                'Number',
                'First Name',
                'Last Name',
                'Pass Type',
                'Start Date',
                'Automatic Renewal',
                'Vehicle 1',
                'Vehicle 2',
                'Status',
                'Pass',
                'Sold Via',
                'Action'
            ]
        },
        columnId: function(){
            let vm = this
            return {
                data: "id",
                visible: false,
                'render': function(row, type, full){
                    if(vm.debug){
                        console.log(full)
                    }
                    return full.id
                }
            }
        },
        column_pass_number: function(){
            return {
                data: "pass_number",
                visible: true,
                name: 'pass_number',
                orderable: true,
            }
        },
        column_first_name: function(){
            return {
                data: "first_name",
                visible: true,
                searchable: true,
                name: 'first_name',
            }
        },
        column_last_name: function(){
            return {
                data: "last_name",
                visible: true,
                name: 'last_name',
            }
        },
        column_pass_type: function(){
            return {
                data: "pass_type",
                visible: true,
                searchable: false,
                name: 'option.pricing_window.pass_type.display_name'
            }
        },
        column_datetime_start: function(){
            return {
                data: "datetime_start",
                visible: true,
                name: 'datetime_start',
                'render': function(row, type, full){
                    const date = new Date(full.datetime_start);
                    return date.toLocaleDateString();
                }
            }
        },
        column_renew_automatically: function(){
            return {
                data: "renew_automatically",
                visible: true,
                className: 'text-center',
                name: 'renew_automatically',
                'render': function(row, type, full){
                    if(full.renew_automatically){
                        return '<i class="fa fa-check" aria-hidden="true" style="color:green;"></i>';
                    } else {
                        return '<i class="fa fa-times" aria-hidden="true" style="color:red;"></i>';
                    }
                }

            }
        },
        column_vehicle_registration_1: function(){
            let vm = this
            return {
                data: "vehicle_registration_1",
                visible: true,
                searchable: true,
                name: 'vehicle_registration_1',
            }
        },
        column_vehicle_registration_2: function(){
            let vm = this
            return {
                data: "vehicle_registration_2",
                visible: true,
                searchable: true,
                name: 'vehicle_registration_2',
            }
        },
        column_processing_status: function(){
            let vm = this;
            return {
                data: "processing_status",
                visible: true,
                name: 'processing_status',
                'render': function(row, type, full){
                    const processingStatus = vm.passProcessingStatusesDistinct.find(obj => {
                        return obj.code === full.processing_status
                    })
                    return processingStatus.description
                }
            }
        },
        column_park_pass_pdf: function(){
            return {
                data: "park_pass_pdf",
                visible: true,
                orderable: false,
                name: 'park_pass_pdf',
                'render': function(row, type, full){
                    return `<a href="${full.park_pass_pdf}" target="blank">ParkPass.pdf</a>`
                }
            }
        },
        column_sold_via: function(){
            return {
                data: "sold_via",
                visible: true,
                name: 'sold_via.name'
            }
        },
        columnAction: function(){
            let vm = this
            return {
                // 8. Action
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    let links = '';
                    links +=  `<a href='/internal/pass/${full.id}'>Edit</a> | `;
                    links +=  `<a href='/internal/pass/${full.id}/cancel/'>Cancel</a> | `;
                    links +=  `<a href='/internal/pass/${full.id}/payment-details/'>View Payment Details</a><br/>`;
                    return links;
                }
            }
        },
        dtOptions: function(){
            let vm = this

            let columns = []
            let search = null
            let buttons = [
                {
                    extend: 'excel',
                    text: '<i class="fa-solid fa-download"></i> Excel',
                    className: 'btn btn-primary ml-2',
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: 'csv',
                    text: '<i class="fa-solid fa-download"></i> CSV',
                    className: 'btn btn-primary',
                    exportOptions: {
                        columns: ':visible'
                    }
                },
            ]

            columns = [
                vm.columnId,
                vm.column_pass_number,
                vm.column_first_name,
                vm.column_last_name,
                vm.column_pass_type,
                vm.column_datetime_start,
                vm.column_renew_automatically,
                vm.column_vehicle_registration_1,
                vm.column_vehicle_registration_2,
                vm.column_processing_status,
                vm.column_park_pass_pdf,
                vm.column_sold_via,
                vm.columnAction,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                rowCallback: function (row, pass){
                    let row_jq = $(row)
                    row_jq.attr('id', 'pass_id_' + pass.id)
                    row_jq.children().first().addClass(vm.tdExpandClassName)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": api_endpoints.passesPaginatedList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.option__pricing_window__pass_type__name = vm.filterPassType
                        d.processing_status = vm.filterPassProcessingStatus
                        d.start_date_from = vm.filterPassDatetimeStartFrom
                        d.start_date_to = vm.filterPassDatetimeStartTo
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                order: [[1, 'desc']],

                columns: columns,
                processing: true,
                pagingType: "full_numbers",
                initComplete: function() {
                },
            }
        }
    },
    methods: {
        adjustTableWidth: function(){
            this.$refs.passDatatable.vmDataTable.columns.adjust()
            this.$refs.passDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.CollapsibleFilters.show_warning_icon(this.filterApplied)
        },
        fetchFilterLists: function(){
            let vm = this;

            // Pass Types
            fetch(api_endpoints.passTypesDistinct)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    return Promise.reject(error);
                }
                vm.passTypesDistinct = data
            })
            .catch(error => {
                //this.errorMessage = error;
                console.error("There was an error!", error);
            });

            // Pass Processing Statuses
            fetch(api_endpoints.passProcessingStatusesDistinct)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    return Promise.reject(error);
                }
                vm.passProcessingStatusesDistinct = data
            })
            .catch(error => {
                //this.errorMessage = error;
                console.error("There was an error!", error);
            });
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.passDatatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id)
            });

            // Listener for the row
            vm.$refs.passDatatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.tdExpandClassName) || td_link.hasClass(vm.tdCollapseClassName))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Retrieve id from the id of the <tr>
                let tr_id = tr.attr('id')
                let proposal_id = tr_id.replace('pass_id_', '')

                let first_td = tr.children().first()
                if(first_td.hasClass(vm.tdExpandClassName)){
                    // Expand

                    // If we don't need to retrieve the data from the server, follow the code below
                    let contents = '<div><strong>Site:</strong> (site name here)</div><div><strong>Group:</strong> (group name here)</div>'

                    // Change icon class name to vm.tdCollapseClassName
                    first_td.removeClass(vm.tdExpandClassName).addClass(vm.tdCollapseClassName)
                } else {
                    let nextElem = tr.next()
                    // Collapse
                    if(nextElem.is('tr') & nextElem.hasClass(vm.expandableRowClassName)){
                        // Sticker details row is already shown.  Remove it.
                        nextElem.fadeOut(500, function(){
                            nextElem.remove()
                        })
                    }
                    // Change icon class name to vm.tdExpandClassName
                    first_td.removeClass(vm.tdCollapseClassName).addClass(vm.tdExpandClassName)
                }
            })
        },
    },
    created: function(){
        this.fetchFilterLists()
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style scoped>
    i.fa-check {
        color:green;
    }
    i.fa-cross {
        color:red;
    }
</style>

<style>
.collapse-icon {
    cursor: pointer;
}
.collapse-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '-';
    color: white;
    background-color: #d33333;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
.expand-icon {
    cursor: pointer;
}
.expand-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '+';
    color: white;
    background-color: #337ab7;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}

div.dt-buttons{
    margin-left:8px;
}

li.paginate_button{
    padding-right:5px;
}

</style>
