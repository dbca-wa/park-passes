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
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import PricingWindowFormModal from '@/components/internal/modals/PricingWindowFormModal.vue'
import PricingWindowConfirmDeleteModal from '@/components/internal/modals/PricingWindowConfirmDeleteModal.vue'

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
            filterDateStartFrom: sessionStorage.getItem(vm.filterDateStartFromCacheName) ? sessionStorage.getItem(vm.filterDateStartFromCacheName) : '',
            filterDateStartTo: sessionStorage.getItem(vm.filterDateStartToCacheName) ? sessionStorage.getItem(vm.filterDateStartToCacheName) : '',
            filterDateExpiryFrom: sessionStorage.getItem(vm.filterDateExpiryFromCacheName) ? sessionStorage.getItem(vm.filterDateExpiryFromCacheName) : '',
            filterDateExpiryTo: sessionStorage.getItem(vm.filterDateExpiryToCacheName) ? sessionStorage.getItem(vm.filterDateExpiryToCacheName) : '',

            selectedPricingWindow: null,

            errorMessage: null,
            successMessage: null,

            // filtering options
            passTypesDistinct: [],

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
                this.filterPassType === '' &&
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
                'Options',
                'Status',
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
        columnStatus: function () {
            return {
                data: "status",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'status',
                'render': function(row, type, full){
                    return `<span class="badge ${helpers.getStatusBadgeClass(full.status)}">${full.status}</span>`;
                }
            }
        },
        columnOptions: function(){
            let vm = this
            return {
                data: "options",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    let optionsHtml = '';
                    console.log(full.options);
                    if(full.options && full.options.length){
                        full.options.forEach((option) => {
                            optionsHtml += `<span class="badge org-badge-primary">${option.name}`;
                            optionsHtml += `    <span class="badge bg-secondary">$${option.price}`;
                            optionsHtml += `    </span>`;
                            optionsHtml += `</span> `;
                        });
                        return optionsHtml;
                    } else {
                        return 'No options specified. This is bad.';
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
                    let editLink = vm.$router.resolve({
                        name: 'internal-pricing-window-form',
                        params: { pricingWindowId: full.id }
                    });
                    let links = '';
                    const expiryDate = new Date(full.date_expiry);
                    if(full.date_expiry && expiryDate < new Date()) {
                        links +=  '';
                    } else {
                        links +=  `<a href="${editLink.href}">Edit</a>`;

                    }
                    const startDate = new Date(full.date_start);
                    if(full.date_expiry && startDate > new Date()) {
                        links +=  ` | <a href="javascript:void(0)" data-item-id="${full.id}" data-name="${full.name}" data-action="delete">Delete</a>`;
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
                vm.columnOptions,
                vm.columnStatus,
                vm.columnAction,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.pricingWindowsPaginatedList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.pass_type = vm.filterPassType
                        d.start_date_from = vm.filterDateStartFrom
                        d.start_date_to = vm.filterDateStartTo
                        d.expiry_date_from = vm.filterDateExpiryFrom
                        d.expiry_date_to = vm.filterDateExpiryTo
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
        saveSuccess: function() {
            window.scrollTo(0,0);
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
        },
        deletePricingWindow: function(pricingWindow) {
            this.selectedPricingWindow = pricingWindow;
            let pricingWindowConfirmDeleteModal = new bootstrap.Modal(document.getElementById('pricingWindowConfirmDeleteModal'), {});
            pricingWindowConfirmDeleteModal.show();
        },
        deleteSuccess: function() {
            window.scrollTo(0,0);
            this.$refs.pricingWindowDatatable.vmDataTable.draw();
        },
        fetchFilterLists: function(){
            let vm = this;
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
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.pricingWindowDatatable.vmDataTable.on('click', 'a[data-action="edit"]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-item-id');
                vm.deletePricingWindow({'id':id, 'name':name})
            });
            vm.$refs.pricingWindowDatatable.vmDataTable.on('click', 'a[data-action="delete"]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-item-id');
                let name = $(this).attr('data-name');
                vm.deletePricingWindow({'id':id, 'name':name})
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
