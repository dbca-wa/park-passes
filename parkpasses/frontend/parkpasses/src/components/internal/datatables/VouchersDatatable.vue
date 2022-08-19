<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterStatus">
                            <option value="all" selected="selected">All</option>
                            <option v-for="status in statuses" :value="status">{{ status }}</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Send Date From</label>
                        <div class="input-group date" ref="voucherDatetimeToEmailFrom">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterVoucherDatetimeToEmailFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Send Date To</label>
                        <div class="input-group date" ref="voucherDatetimeToEmailTo">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterVoucherDatetimeToEmailTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{errorMessage}}</div>
        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="voucherDatatable"
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
import { apiEndpoints } from '@/utils/hooks'
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
        filterDiscountCodeBatchStatusCacheName: {
            type: String,
            required: false,
            default: 'filterDiscountCodeBatchStatus',
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'passes-datatable-' + uuid(),

            filterStatus: 'all',
            filterDiscountCodeBatchStatus: sessionStorage.getItem(vm.filterDiscountCodeBatchStatusCacheName) ? sessionStorage.getItem(vm.filterDiscountCodeBatchStatusCacheName) : 'all',
            filterVoucherDatetimeToEmailFrom: '',
            filterVoucherDatetimeToEmailTo: '',

            errorMessage: null,

            statuses: [
                'New',
                'Delivered',
                'Not Delivered',
            ],

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
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        }
    },
    components:{
        datatable,
        CollapsibleFilters,
    },
    watch: {
        filterDiscountCodeBatchStatus: function() {
            this.$refs.voucherDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDiscountCodeBatchStatusCacheName, this.filterDiscountCodeBatchStatus);
        },
    },
    computed: {
        number_of_columns: function() {
            let num =  this.$refs.voucherDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(this.filterDiscountCodeBatchStatus.toLowerCase() === 'all' && this.filterStatus.toLowerCase() === 'all' &&
                this.filterVoucherDatetimeToEmailFrom.toLowerCase() === '' && this.filterVoucherDatetimeToEmailTo.toLowerCase() === ''){
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
                'Recipient',
                'Purchaser',
                'Send Date',
                'Purchased Value',
                'Remaining Balance',
                'Status',
                'Invoice',
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
        column_voucher_number: function(){
            return {
                data: "voucher_number",
                visible: true,
                name: 'voucher_number',
                orderable: true,
            }
        },
        column_recipient_name: function(){
            return {
                data: "recipient_name",
                visible: true,
                name: 'recipient_name',
            }
        },
        column_recipient_email: function(){
            return {
                data: "recipient_email",
                visible: true,
                name: 'recipient_email',
            }
        },
        column_datetime_to_email: function(){
            return {
                data: "datetime_to_email",
                visible: true,
                name: 'datetime_to_email',
                'render': function(row, type, full){
                    const date = new Date(full.datetime_to_email);
                    return date.toLocaleDateString();
                }
            }
        },
        column_amount: function(){
            return {
                data: "amount",
                visible: true,
                name: 'amount',
                'render': function(row, type, full){
                    return `$${full.amount}`
                }
            }
        },
        column_remaining_balance: function(){
            return {
                data: "remaining_balance",
                visible: true,
                orderable: false,
                name: 'remaining_balance',
                'render': function(row, type, full){
                    return `$${full.remaining_balance}`
                }
            }
        },
        column_processing_status: function(){
            return {
                data: "processing_status",
                visible: true,
                name: 'processing_status'
            }
        },
        column_invoice: function(){
            let vm = this
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    return `<a href='/internal/voucher/${full.id}'>Invoice</a>`;
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
                    links +=  `<a href='/internal/voucher/${full.id}'>Edit</a> | `;
                    links +=  `<a href='/internal/voucher/${full.id}/cancel/'>Cancel</a> | `;
                    links +=  `<a href='/internal/voucher/${full.id}/payment-details/'>View Payment Details</a><br/>`;
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
                vm.column_voucher_number,
                vm.column_recipient_name,
                vm.column_recipient_email,
                vm.column_datetime_to_email,
                vm.column_amount,
                vm.column_remaining_balance,
                vm.column_processing_status,
                vm.column_invoice,
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
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.vouchersInternalPaginatedList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        //d.option__pricing_window__datetime_to_email__name = vm.filterStatus
                        d.processing_status = vm.filterDiscountCodeBatchStatus
                        //d.filter_lodged_from = vm.filterVoucherDatetimeToEmailFrom
                        //d.filter_lodged_to = vm.filterVoucherDatetimeToEmailTo
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
            this.$refs.voucherDatatable.vmDataTable.columns.adjust()
            this.$refs.voucherDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.collapsible_filters.showWarningIcon(this.filterApplied)
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
            let vm = this
            vm.$refs.voucherDatatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id)
            });

            // Listener for the row
            vm.$refs.voucherDatatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Retrieve id from the id of the <tr>
                let tr_id = tr.attr('id')
                let proposal_id = tr_id.replace('pass_id_', '')

                let first_td = tr.children().first()
                if(first_td.hasClass(vm.td_expand_class_name)){
                    // Expand

                    // If we don't need to retrieve the data from the server, follow the code below
                    let contents = '<div><strong>Site:</strong> (site name here)</div><div><strong>Group:</strong> (group name here)</div>'

                    // Change icon class name to vm.td_collapse_class_name
                    first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
                } else {
                    let nextElem = tr.next()
                    // Collapse
                    if(nextElem.is('tr') & nextElem.hasClass(vm.expandable_row_class_name)){
                        // Sticker details row is already shown.  Remove it.
                        nextElem.fadeOut(500, function(){
                            nextElem.remove()
                        })
                    }
                    // Change icon class name to vm.td_expand_class_name
                    first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
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
