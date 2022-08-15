<template>
    <div>
        <div class="row mb-3">
            <div class="col">
                <button class="btn licensing-btn-primary float-end" data-bs-toggle="modal" data-bs-target="#pricingWindowModal">Add New Pricing Window</button>
            </div>
        </div>
        <div v-if="successMessage" class="row mx-1">
            <div id="successMessageAlert" class="col alert alert-success show fade" role="alert">
                {{ successMessage }}
            </div>
        </div>
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
            </div>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Start Date From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateStartFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Start Date To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateStartTo">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">End Date From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateExpiryFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">End Date To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateExpiryTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{errorMessage}}</div>
        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="pricingWindowDatatable"
                    :id="datatable_id"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
    <PricingWindowFormModal @saveSuccess="saveSuccess" :passTypesDistinct="passTypesDistinct" />
    <PricingWindowConfirmDeleteModal @deleteSuccess="deleteSuccess" :pricingWindow="selectedPricingWindow" />
</template>

<script>
import datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { api_endpoints } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import PricingWindowFormModal from '@/components/internal/modals/PricingWindowFormModal.vue'
import PricingWindowConfirmDeleteModal from '@/components/internal/modals/PricingWindowConfirmDeleteModal.vue'
import BootstrapModalVue from '../../../utils/vue/BootstrapModal.vue';

export default {
    name: 'PricingWindowsDatatable',
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
        filterDateStartFromCacheName: {
            type: String,
            required: false,
            default: 'filterDateStartFrom',
        },
        filterDateStartToCacheName: {
            type: String,
            required: false,
            default: 'filterDateStartTo',
        },
        filterDateExpiryFromCacheName: {
            type: String,
            required: false,
            default: 'filterDateExpiryFrom',
        },
        filterDateExpiryToCacheName: {
            type: String,
            required: false,
            default: 'filterDateExpiryTo',
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'pricing-window-datatable-' + uuid(),

            filterPassType: sessionStorage.getItem(vm.filterPassTypeCacheName) ? sessionStorage.getItem(vm.filterPassTypeCacheName) : '',
            filterProcessingStatus: sessionStorage.getItem(vm.filterProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterProcessingStatusCacheName) : '',
            filterDateStartFrom: sessionStorage.getItem(vm.filterDateStartFromCacheName) ? sessionStorage.getItem(vm.filterDateStartFromCacheName) : '',
            filterDateStartTo: sessionStorage.getItem(vm.filterDateStartToCacheName) ? sessionStorage.getItem(vm.filterDateStartToCacheName) : '',
            filterDateExpiryFrom: sessionStorage.getItem(vm.filterDateExpiryFromCacheName) ? sessionStorage.getItem(vm.filterDateExpiryFromCacheName) : '',
            filterDateExpiryTo: sessionStorage.getItem(vm.filterDateExpiryToCacheName) ? sessionStorage.getItem(vm.filterDateExpiryToCacheName) : '',

            selectedPricingWindow: null,

            errorMessage: null,
            successMessage: null,

            // filtering options
            passTypesDistinct: [],
            processingStatusesDistinct: [],

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
        PricingWindowFormModal,
        PricingWindowConfirmDeleteModal,
    },
    watch: {
        filterPassType: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterPassTypeCacheName, this.filterPassType);
        },
        filterProcessingStatus: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDateStartFrom: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterDateStartFromCacheName, this.filterDateStartFrom);
        },
        filterDateStartTo: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterDateStartToCacheName, this.filterDateStartTo);
        },
        filterDateExpiryFrom: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterDateExpiryFromCacheName, this.filterDateExpiryFrom);
        },
        filterDateExpiryTo: function() {
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterDateExpiryToCacheName, this.filterDateExpiryTo);
        },
        filterApplied: function() {
            if (this.$refs.CollapsibleFilters){
                this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
            }
        }
    },
    computed: {
        numberOfColumns: function() {
            let num =  this.$refs.pricingWindowDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(
                this.filterProcessingStatus.toLowerCase() === '' &&
                this.filterPassType.toLowerCase() === '' &&
                this.filterDateStartFrom.toLowerCase() === '' &&
                this.filterDateStartTo.toLowerCase() === '' &&
                this.filterDateExpiryFrom.toLowerCase() === '' &&
                this.filterDateExpiryTo.toLowerCase() === ''
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
                'Pass Type',
                'Name',
                'Start Date',
                'End Date',
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
        columnPassType: function(){
            return {
                data: "pass_type_display_name",
                visible: true,
                orderable: true,
                searchable: false,
                name: 'pass_type',
            }
        },
        columnName: function(){
            return {
                data: "name",
                visible: true,
                orderable: true,
                searchable: true,
                name: 'name',
            }
        },
        columnDateStart: function(){
            return {
                data: "date_start",
                visible: true,
                orderable: true,
                name: 'date_start',
                'render': function(row, type, full){
                    const date = new Date(full.date_start);
                    return date.toLocaleDateString();
                }
            }
        },
        columnDateExpiry: function(){
            return {
                data: "date_expiry",
                visible: true,
                orderable: true,
                name: 'date_expiry',
                'render': function(row, type, full){
                    if(full.date_expiry){
                        const date = new Date(full.date_expiry);
                        return date.toLocaleDateString();
                    } else {
                        return '';
                    }

                }
            }
        },
        columnAction: function(){
            let vm = this
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    let links = '';
                    links +=  `<a href="javascript:void(0)" data-item-id="${full.id}" data-action="edit">Edit</a>`;
                    if(full.date_expiry) {
                        links +=  ` | <a href="javascript:void(0)" data-item-id="${full.id}" data-action="delete">Delete</a>`;
                    }
                    // Todo don't show delete option if the pricing window has already commenced.
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
                vm.columnPassType,
                vm.columnName,
                vm.columnDateStart,
                vm.columnDateExpiry,
                vm.columnAction,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                'createdRow': function (row, data, dataIndex){
                    //console.log('data = ' + JSON.stringify(data));
                    $(row).find('a[data-action="delete"]').on('click', function(e){
                        var id = $(this).data('item-id');
                        console.log('Delete ' + id);
                        vm.deletePricingWindow(data);
                        // Add a call to a vue function here that confirms deletion and then delete the record and
                        // redraws the datatable... :D
                    });
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": api_endpoints.pricingWindowsPaginatedList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.pass_type = vm.filterPassType
                        d.processing_status = vm.filterProcessingStatus
                        d.start_date_from = vm.filterDateStartFrom
                        d.start_date_to = vm.filterDateStartTo
                        d.date_expiry_from = vm.filterDateExpiryFrom
                        d.date_expiry_to = vm.filterDateExpiryTo
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                order: [[1, 'asc']],

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
            this.$refs.pricingWindowDatatable.vmDataTable.columns.adjust()
            this.$refs.pricingWindowDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
        },
        saveSuccess: function({message, pricingWindow}) {
            window.scrollTo(0,0);
            this.successMessage = message;
            console.log(pricingWindow.name);
            this.$nextTick(() => {
                $('#successMessageAlert').fadeOut(4000, function(){
                    this.successMessage = null;
                });
            });
            this.$refs.pricingWindowDatatable.vmDataTable.search(pricingWindow.name).draw();
        },
        deletePricingWindow: function(pricingWindow) {
            this.selectedPricingWindow = pricingWindow;
            let pricingWindowConfirmDeleteModal = new bootstrap.Modal(document.getElementById('pricingWindowConfirmDeleteModal'), {});
            pricingWindowConfirmDeleteModal.show();
        },
        deleteSuccess: function({message, pricingWindow}) {
            window.scrollTo(0,0);
            this.successMessage = message;
            console.log(pricingWindow.name);
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
            console.log('#successMessageAlert.length = ' + $('#successMessageAlert').length);
            this.$nextTick(() => {
                $('#successMessageAlert').fadeOut(4000, function(){
                    this.successMessage = null;
                });
            });
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
                vm.processingStatusesDistinct = data
            })
            .catch(error => {
                //this.errorMessage = error;
                console.error("There was an error!", error);
            });
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.pricingWindowDatatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id)
            });

            // Listener for the row
            vm.$refs.pricingWindowDatatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.tdExpandClassName) || td_link.hasClass(vm.tdCollapseClassName))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Retrieve id from the id of the <tr>
                let tr_id = tr.attr('id')
                let proposal_id = tr_id.replace('pricingWindowId', '')

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
        $('input[type=search]').focus();
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
