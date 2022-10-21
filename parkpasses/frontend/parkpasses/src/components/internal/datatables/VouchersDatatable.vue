<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="CollapsibleFilters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterProcessingStatus">
                            <option value="" selected="selected">All</option>
                            <option v-for="status in statuses" :value="status.id">{{ status.value }}</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Send Date From</label>
                        <div class="input-group date" ref="filterDatetimeToEmailFrom">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeToEmailFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Send Date To</label>
                        <div class="input-group date" ref="filterDatetimeToEmailTo">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeToEmailTo">
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
                    :id="datatableId"
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
import { apiEndpoints, constants } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'

export default {
    name: 'VouchersDatatable',
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
        filterDatetimeToEmailFromCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeToEmailFrom',
        },
        filterDatetimeToEmailToCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeToEmailTo',
        },
    },
    data() {
        let vm = this;
        return {
            datatableId: 'vouchers-datatable-' + uuid(),

            filterProcessingStatus: sessionStorage.getItem(vm.filterProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterProcessingStatusCacheName) : '',
            filterDatetimeToEmailFrom: sessionStorage.getItem(vm.filterDatetimeToEmailFromCacheName) ? sessionStorage.getItem(vm.filterDatetimeToEmailFromCacheName) : '',
            filterDatetimeToEmailTo: sessionStorage.getItem(vm.filterDatetimeToEmailToCacheName) ? sessionStorage.getItem(vm.filterDatetimeToEmailToCacheName) : '',

            errorMessage: null,

            statuses: [
                {id:'N', value:'New'},
                {id:'D', value:'Delivered'},
                {id:'ND', value:'Not Delivered'},
            ],

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
        filterProcessingStatus: function() {
            this.$refs.voucherDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDatetimeToEmailFrom: function() {
            this.$refs.voucherDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeToEmailFromCacheName, this.filterDatetimeToEmailFrom);
        },
        filterDatetimeToEmailTo: function() {
            this.$refs.voucherDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeToEmailToCacheName, this.filterDatetimeToEmailTo);
        },
        filterApplied: function() {
            if (this.$refs.CollapsibleFilters){
                this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
            }
        }
    },
    computed: {
        numberOfColumns: function() {
            let num =  this.$refs.voucherDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filterApplied = true
            if(
                this.filterProcessingStatus === '' &&
                this.filterDatetimeToEmailFrom === '' &&
                this.filterDatetimeToEmailTo === ''){
                filterApplied = false
            }
            console.log('filter applied = ' + filterApplied);
            return filterApplied
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
                'Recipient Name',
                'Recipient Email',
                'Purchaser',
                'Send Date',
                'Purchased Value',
                'Remaining Balance',
                'Status',
                'Invoice',
                'Code',
                'Pin',
                'Action',
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

        columnVoucherNumber: function(){
            return {
                data: "voucher_number",
                visible: true,
                name: 'voucher_number',
                orderable: true,
            }
        },
        columnRecipientName: function(){
            return {
                data: "recipient_name",
                visible: true,
                name: 'recipient_name',
            }
        },
        columnRecipientEmail: function(){
            return {
                data: "recipient_email",
                visible: true,
                name: 'recipient_email',
            }
        },
        columnPurchaserName: function(){
            return {
                data: "purchaser_name",
                visible: true,
                name: 'purchaser_name',
            }
        },
        columnDatetimeToEmail: function(){
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
        columnAmount: function(){
            return {
                data: "amount",
                visible: true,
                name: 'amount',
                'render': function(row, type, full){
                    return `$${full.amount}`
                }
            }
        },
        columnRemainingBalance: function(){
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
        columnProcessingStatus: function(){
            return {
                data: "processing_status",
                visible: true,
                name: 'processing_status',
                'render': function(row, type, full){
                    let html = '';
                    if('Delivered to Recipient'==full.processing_status){
                        html = `<span class="badge bg-success">${full.processing_status}</span>`;
                    } else  if('New'==full.processing_status) {
                        html = `<span class="badge org-badge-primary">${full.processing_status}</span>`;
                    } else if('Purchaser Notified'==full.processing_status) {
                        html = `<span class="badge org-badge-primary">${full.processing_status}</span>`;
                    } else {
                        html = `<span class="badge bg-danger">${full.processing_status}</span>`;
                    }
                    return html;
                }
            }
        },
        columnInvoice: function(){
            let vm = this
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    return `<a target="_blank" href='${apiEndpoints.internalVoucherInvoice(full.id)}'>Invoice</a>`;
                }
            }
        },
        columnCode: function(){
            return {
                data: "code",
                visible: true,
                name: 'code',
                orderable: true,
            }
        },
        columnPin: function(){
            return {
                data: "pin",
                visible: true,
                name: 'pin'
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
                    if(full.user_can_view_payment_details){
                        links +=  `<a target="_blank" href='${apiEndpoints.internalVoucherPaymentDetails(full.id)}'>View Payment Details</a><br/>`;
                    } else {
                        links += 'Available to [Park Passes Payments Officer] only';
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
                vm.columnVoucherNumber,
                vm.columnRecipientName,
                vm.columnRecipientEmail,
                vm.columnPurchaserName,
                vm.columnDatetimeToEmail,
                vm.columnAmount,
                vm.columnRemainingBalance,
                vm.columnProcessingStatus,
                vm.columnInvoice,
                vm.columnCode,
                vm.columnPin,
                vm.columnAction,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML
                },
                rowCallback: function (row, voucher){
                    let row_jq = $(row)
                    row_jq.attr('id', 'voucherId' + voucher.id)
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
                        d.processing_status = vm.filterProcessingStatus
                        d.datetime_to_email_from = vm.filterDatetimeToEmailFrom
                        d.datetime_to_email_to = vm.filterDatetimeToEmailTo
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
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
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
                let proposal_id = tr_id.replace('voucherId', '')

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

    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>
