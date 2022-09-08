<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="CollapsibleFilters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Date From</label>
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
                        <label for="">Date To</label>
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
                    ref="ordersDatatable"
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
import { apiEndpoints } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import PassCancellationModal from '@/components/internal/modals/PassCancellationModal.vue'


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
            this.$refs.ordersDatatable.vmDataTable.columns.adjust().draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterPassTypeCacheName, this.filterPassType);
        },
        filterProcessingStatus: function() {
            this.$refs.ordersDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDatetimeStartFrom: function() {
            this.$refs.ordersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeStartFromCacheName, this.filterDatetimeStartFrom);
        },
        filterDatetimeStartTo: function() {
            this.$refs.ordersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
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
            let num =  this.$refs.ordersDatatable.vmDataTable.columns(':visible').nodes().length;
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
                '',
                'Number',
                'Date',
                'Total',
                'Invoice'
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
        columnDtControl: function() {
            return {
                targets: 'no-sort',
                className: 'dt-control',
                orderable: false,
                searchable: false,
                data: null,
                defaultContent: '',
            }
        },
        columnOrderNumber: function(){
            return {
                data: "order_number",
                visible: true,
                name: 'order_number',
                orderable: true,
            }
        },
        columnDatetimeCreated: function(){
            return {
                data: "datetime_created",
                visible: true,
                name: 'datetime_created',
                'render': function(row, type, full){
                    const date = new Date(full.datetime_created);
                    return date.toLocaleDateString();
                }
            }
        },
        columnTotal: function(){
            return {
                data: "total",
                visible: true,
                searchable: true,
                orderable: true,
                name: 'total',
                'render': function(row, type, full){
                    return `$${full.total.toFixed(2)}`;
                }
            }
        },
        columnInvoice: function(){
            return {
                data: 'invoice_reference_link',
                visible: true,
                searchable: false,
                orderable: false,
                'render': function(row, type, full){
                    return `<a target="blank" href="${full.invoice_link}">View Invoice</a>`;
                }
            }
        },
        columnItems: function(){
            return {
                data: 'items',
                visible: false,
                searchable: false,
                orderable: false,
                'render': function(row, type, full){
                    return 'Items'
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
                vm.columnDtControl,
                vm.columnOrderNumber,
                vm.columnDatetimeCreated,
                vm.columnTotal,
                vm.columnInvoice,
                vm.columnItems,
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
                    //row_jq.children().first().addClass(vm.tdExpandClassName)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.ordersListExternal + '?format=datatables',
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
                order: [[2, 'desc']],

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
            this.$refs.ordersDatatable.vmDataTable.columns.adjust()
            this.$refs.ordersDatatable.vmDataTable.responsive.recalc()
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
        formatChildRow: function(rowData) {
            let childRowHtml = '<table class="table table-sm table-child-row">';
            childRowHtml += '<tr><th>Description</th><th>Amount</th></tr>';
            rowData.items.forEach(item => {
                childRowHtml += '<tr>';
                childRowHtml += '   <td>' + item.description + '</td>';
                childRowHtml += '   <td>$' + Number.parseFloat(item.amount).toFixed(2) + '</td>';
                childRowHtml += '<tr>';
            });
            childRowHtml += '</table>'
            return childRowHtml
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.ordersDatatable.vmDataTable.on('click', 'td.dt-control', function(e) {
                var tr = $(this).closest('tr');
                var row = vm.$refs.ordersDatatable.vmDataTable.row(tr);

                if (row.child.isShown()) {
                    // This row is already open - close it
                    row.child.hide();
                    tr.removeClass('shown');
                } else {
                    // Open this row
                    row.child(vm.formatChildRow(row.data())).show();
                    tr.addClass('shown');
                }
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
