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
                        <select class="form-control" v-model="filterProcessingStatus">
                            <option value="">All</option>
                            <option v-for="processingStatus in passProcessingStatusesDistinct" :value="processingStatus.code">{{ processingStatus.description }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6 text-end">
                    <button class="dt-button buttons-csv buttons-html5 btn licensing-btn-primary">Upload Personnel Passes</button>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Start Date From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeStartFrom">
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
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeStartTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{errorMessage}}</div>
        <div class="row">
            <div class="col-lg-12">
                <Datatable v-if="passProcessingStatusesDistinct"
                    ref="passDatatable"
                    :id="dataTableId"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
    <PassCancellationModal @cancelSuccess="cancelSuccess" :pass="selectedPass" />
</template>

<script>
import Datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import PassCancellationModal from '@/components/internal/modals/PassCancellationModal.vue'


export default {
    name: 'PassesDatatable',
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        filterProcessingStatusCacheName: {
            type: String,
            required: false,
            default: 'filterProcessingStatus',
        },
        filterPassTypeCacheName: {
            type: String,
            required: false,
            default: 'filterPassType',
        },
        filterDatetimeStartFromCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeStartFrom',
        },
        filterDatetimeStartToCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeStartTo',
        },

    },
    data() {
        let vm = this;
        return {
            dataTableId: 'passes-datatable-' + uuid(),

            filterPassType: sessionStorage.getItem(vm.filterPassTypeCacheName) ? sessionStorage.getItem(vm.filterPassTypeCacheName) : '',
            filterProcessingStatus: sessionStorage.getItem(vm.filterProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterProcessingStatusCacheName) : '',
            filterDatetimeStartFrom: sessionStorage.getItem(vm.filterDatetimeStartFromCacheName) ? sessionStorage.getItem(vm.filterDatetimeStartFromCacheName) : '',
            filterDatetimeStartTo: sessionStorage.getItem(vm.filterDatetimeStartToCacheName) ? sessionStorage.getItem(vm.filterDatetimeStartToCacheName) : '',

            selectedPass: null,

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
        Datatable,
        CollapsibleFilters,
        PassCancellationModal,
    },
    watch: {
        filterPassType: function() {
            this.$refs.passDatatable.vmDataTable.columns.adjust().draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassTypeCacheName, this.filterPassType);
        },
        filterProcessingStatus: function() {
            this.$refs.passDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDatetimeStartFrom: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeStartFromCacheName, this.filterDatetimeStartFrom);
        },
        filterDatetimeStartTo: function() {
            this.$refs.passDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeStartToCacheName, this.filterDatetimeStartTo);
        },
        filterApplied: function() {
            if (this.$refs.CollapsibleFilters){
                this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
            }
        }
    },
    computed: {
        numberOfColumns: function() {
            let num =  this.$refs.passDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(
                this.filterProcessingStatus.toLowerCase() === '' &&
                this.filterPassType === '' &&
                this.filterDatetimeStartFrom.toLowerCase() === '' &&
                this.filterDatetimeStartTo.toLowerCase() === ''
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
                 orderable: true,
                'render': function(row, type, full){
                    if(vm.debug){
                        console.log(full)
                    }
                    return full.id
                }
            }
        },
        columnPassNumber: function(){
            return {
                data: "pass_number",
                visible: true,
                name: 'pass_number',
                orderable: true,
            }
        },
        columnFirstName: function(){
            return {
                data: "first_name",
                visible: true,
                searchable: true,
                orderable: true,
                name: 'first_name',
            }
        },
        columnLastName: function(){
            return {
                data: "last_name",
                visible: true,
                name: 'last_name',
            }
        },
        columnPassType: function(){
            return {
                data: "pass_type",
                visible: true,
                searchable: false,
                name: 'option.pricing_window.pass_type.display_name'
            }
        },
        columnDatetimeStart: function(){
            return {
                data: "date_start",
                visible: true,
                name: 'date_start',
                'render': function(row, type, full){
                    const date = new Date(full.date_start);
                    return date.toLocaleDateString();
                }
            }
        },
        columnRenewAutomatically: function(){
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
        columnVehicleRegistration1: function(){
            let vm = this
            return {
                data: "vehicle_registration_1",
                visible: true,
                searchable: true,
                name: 'vehicle_registration_1',
            }
        },
        columnVehicleRegistration2: function(){
            let vm = this
            return {
                data: "vehicle_registration_2",
                visible: true,
                searchable: true,
                name: 'vehicle_registration_2',
            }
        },
        columnProcessingStatus: function(){
            let vm = this;
            return {
                data: "processing_status_display_name",
                visible: true,
                name: 'processing_status',
                'render': function(row, type, full){
                    return `<span class="badge ${helpers.getStatusBadgeClass(full.processing_status_display_name)}">${full.processing_status_display_name}</span>`;
                }
            }
        },
        columnParkPassPdf: function(){
            return {
                data: "park_pass_pdf",
                visible: true,
                orderable: false,
                name: 'park_pass_pdf',
                'render': function(row, type, full){
                    return `<a href="${apiEndpoints.internalParkPassPdf(full.id)}" target="blank">${full.park_pass_pdf}</a>`
                }
            }
        },
        columnSoldVia: function(){
            return {
                data: "sold_via_name",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'sold_via_name'
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
                    let editLink = vm.$router.resolve({
                        name: 'internal-pass-form',
                        params: { passId: full.id }
                    });
                    let links = '';
                    if(!full.user_can_edit_and_cancel && !full.user_can_view_payment_details){
                        links +=  `<a href="${editLink.href}">View</a>`;
                    } else {
                        if('CA'!=full.processing_status){
                            if(full.user_can_edit_and_cancel){
                                links +=  `<a href="${editLink.href}">Edit</a>`;
                                links +=  ` | <a href="javascript:void(0)" data-item-id="${full.id}" data-action="cancel" data-name="${full.pass_number}">Cancel</a>`;
                            }
                        } else {
                            links +=  `<a href="${editLink.href}">View</a>`;
                        }
                        if(full.user_can_view_payment_details){
                            links +=  ` | <a href="javascript:void(0)" data-item-id="${full.id}" data-action="view-payment-details">View Payment Details</a>`;
                        }
                    }

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
                    className: 'btn licensing-btn-primary ml-2',
                    exportOptions: {
                        columns: ':visible'
                    }
                },
                {
                    extend: 'csv',
                    text: '<i class="fa-solid fa-download"></i> CSV',
                    className: 'btn licensing-btn-primary',
                    exportOptions: {
                        columns: ':visible'
                    }
                },
            ]

            columns = [
                vm.columnId,
                vm.columnPassNumber,
                vm.columnFirstName,
                vm.columnLastName,
                vm.columnPassType,
                vm.columnDatetimeStart,
                vm.columnRenewAutomatically,
                vm.columnVehicleRegistration1,
                vm.columnVehicleRegistration2,
                vm.columnProcessingStatus,
                vm.columnParkPassPdf,
                vm.columnSoldVia,
                vm.columnAction,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML
                },
                rowCallback: function (row, pass){
                    let row_jq = $(row)
                    row_jq.attr('id', 'pass_id_' + pass.id)
                    //row_jq.children().first().addClass(vm.tdExpandClassName)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.passesList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.pass_type = vm.filterPassType
                        d.processing_status = vm.filterProcessingStatus
                        d.start_date_from = vm.filterDatetimeStartFrom
                        d.start_date_to = vm.filterDatetimeStartTo
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
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
        },
        cancelPass: function(pass) {
            this.selectedPass = pass;
            let passCancellationModalElement = document.getElementById('passCancellationModal')
            let passCancellationModal = new bootstrap.Modal(passCancellationModalElement, {});
            passCancellationModalElement.addEventListener('shown.bs.modal', function() {
                $('#cancellationReason').focus();
            });
            passCancellationModal.show();

        },
        cancelSuccess: function() {
            this.$refs.passDatatable.vmDataTable.draw();
        },
        fetchFilterLists: function(){
            let vm = this;

            // Pass Types
            fetch(apiEndpoints.passTypesDistinct)
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
            fetch(apiEndpoints.passProcessingStatusesDistinct)
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
            let vm = this;
            vm.$refs.passDatatable.vmDataTable.on('click', 'a[data-action="cancel"]', function(e) {
                e.preventDefault();
                let id = $(this).data('item-id');
                let name = $(this).data('name');
                vm.cancelPass({id, name})
            });
            vm.$refs.passDatatable.vmDataTable.on('click', 'a[data-action="view-payment-details"]', function(e) {
                e.preventDefault();
                let action = $(this).data('action');
                let id = $(this).data('item-id');
                // call
                console.log(action + id);
            });
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
