<template>
    <div>
        <div v-if="there_are_overdue_invoices">
            <BootstrapAlert type="danger" icon="exclamation-triangle-fill">
                You have one or more overdue invoices to pay.  Please pay them as soon as possible.
            </BootstrapAlert>
        </div>
        <CollapsibleFilters label="Filters" component_title="Filters" ref="CollapsibleFilters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Invoice Payment Status</label>
                        <select class="form-control" v-model="filterProcessingStatus">
                            <option value="" selected="selected">All</option>
                            <option v-for="status in statuses" :value="status.id">{{ status.value }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Date From</label>
                        <div class="input-group date" ref="filterDatetimeCreatedFrom">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeCreatedFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Date To</label>
                        <div class="input-group date" ref="filterDatetimeCreatedTo">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeCreatedTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{errorMessage}}</div>
        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="reportDatatable"
                    :id="datatableId"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>

import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'
import datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import Swal from 'sweetalert2'
import DOMPurify from 'dompurify'

export default {
    name: 'ReportsDatatable',
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
        filterDatetimeCreatedFromCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeCreatedFrom',
        },
        filterDatetimeCreatedToCacheName: {
            type: String,
            required: false,
            default: 'filterDatetimeCreatedTo',
        },
    },
    data() {
        let vm = this;
        return {
            datatableId: 'reports-datatable-' + uuid(),

            filterProcessingStatus: sessionStorage.getItem(vm.filterProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterProcessingStatusCacheName) : '',
            filterDatetimeCreatedFrom: sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) : '',
            filterDatetimeCreatedTo: sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) : '',

            errorMessage: null,

            statuses: [
                {id:'P', value:'Paid'},
                {id:'U', value:'Unpaid'},
            ],

            there_are_overdue_invoices: false,

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },

            invoicingDisabled: true,
            invoicingDisabledHtml: '<span class="badge bg-warning">Disabled</span> <span class="text-secondary">Refer to Oracle</span>',

            // For Expandable row
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        }
    },
    components:{
        datatable,
        CollapsibleFilters,
        BootstrapAlert,
    },
    watch: {
        filterProcessingStatus: function() {
            this.$refs.reportDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDatetimeCreatedFrom: function() {
            this.$refs.reportDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeCreatedFromCacheName, this.filterDatetimeCreatedFrom);
        },
        filterDatetimeCreatedTo: function() {
            this.$refs.reportDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeCreatedToCacheName, this.filterDatetimeCreatedTo);
        },
        filterApplied: function() {
            if (this.$refs.CollapsibleFilters){
                this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
            }
        }
    },
    computed: {
        numberOfColumns: function() {
            let num =  this.$refs.reportDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filterApplied = true
            if(
                this.filterProcessingStatus === '' &&
                this.filterDatetimeCreatedFrom === '' &&
                this.filterDatetimeCreatedTo === ''){
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
                'Monthly Report',
                'Statement',
                'Invoice',
                'Payment Status',
                'Date Generated',
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
        columnReportNumber: function(){
            return {
                data: "report_number",
                visible: true,
                name: 'report_number',
                orderable: true,
            }
        },
        columnReport: function(){
            return {
                data: "report_filename",
                visible: true,
                name: 'report_filename',
                'render': function(row, type, full){
                    let html = '';
                    if(full.report_filename){
                        html = `<a href="${apiEndpoints.retrieveReportPdfRetailer(full.id)}" target="_blank">Report.pdf</a>`;
                    }
                    return html;
                }
            }
        },
        columnStatement: function(){
            return {
                data: "statement_filename",
                visible: true,
                name: 'statement_filename',
                'render': function(row, type, full){
                    let html = '';
                    if(full.statement_filename){
                        html = `<a href="${apiEndpoints.retrieveStatementPdfRetailer(full.id)}" target="_blank">Statement.pdf</a>`;
                    }
                    return html;
                }
            }
        },
        columnInvoice: function(){
            let vm = this;
            return {
                data: "invoice_link",
                visible: true,
                name: 'invoice_link',
                'render': function(row, type, full){
                    console.log(full.processing_status)
                    console.log(full.invoice_reference)
                    let html = '';
                    if(vm.invoicingDisabled){
                        html = vm.invoicingDisabledHtml;
                    } else {
                        if('P'===full.processing_status) {
                            html += `<a href="${apiEndpoints.retrieveReportInvoiceReceiptPdfRetailer(full.id)}" target="_blank">Receipt.pdf</a>`;
                        }

                        else if(full.invoice_link){
                            html += `<a href="${full.invoice_link}" target="_blank">Invoice.pdf</a>`;
                        }

                        if('Unpaid'==full.processing_status_display && full.overdue){
                            html += ` <span class="badge bg-danger">Overdue</span>`;
                        }
                    }

                    return html;
                }
            }
        },
        columnProcessingStatusDisplay: function(){
            let vm = this;
            return {
                data: "processing_status_display",
                visible: true,
                name: 'processing_status_display',
                'render': function(row, type, full){
                    let html = '';
                    if(vm.invoicingDisabled){
                        html = vm.invoicingDisabledHtml;
                    } else {
                        if('Paid'==full.processing_status_display){
                            html = `<span class="badge bg-success">Paid</span>`;
                        } else {
                            html = `<span class="badge bg-danger">Unpaid</span> | <a href="${apiEndpoints.retailerPayInvoice(full.id)}">Pay Now</a>`;
                        }
                    }

                    return html;
                }
            }
        },
        columnDatetimeCreated: function(){
            return {
                data: "datetime_created",
                visible: true,
                name: 'datetime_created'
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
                vm.columnReportNumber,
                vm.columnReport,
                vm.columnStatement,
                vm.columnInvoice,
                vm.columnProcessingStatusDisplay,
                vm.columnDatetimeCreated,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML
                },
                rowCallback: function (row, report){
                    let row_jq = $(row)
                    row_jq.attr('id', 'reportId' + report.id)
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.reportsListRetailer + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.retailer_group = vm.filterRetailerGroups
                        d.processing_status = vm.filterProcessingStatus
                        d.datetime_created_from = vm.filterDatetimeCreatedFrom
                        d.datetime_created_to = vm.filterDatetimeCreatedTo
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
                initComplete: function(settings, json) {
                    json.data.forEach(function(currentValue, index, arr){
                        if(currentValue.overdue){
                            vm.there_are_overdue_invoices = true;
                            return;
                        }
                    })
                },
            }
        }
    },
    methods: {
        adjustTableWidth: function(){
            this.$refs.reportDatatable.vmDataTable.columns.adjust()
            this.$refs.reportDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
        },
        updateProcessingStatus: function(id, reportNumber, processingStatus, action) {
            let vm = this;
            let report = {id:id, processing_status:processingStatus}
            console.log('report = ' + report)
            const requestOptions = {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(report)
            };
            fetch(apiEndpoints.reportUpdateInternal(id), requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                vm.$refs.reportDatatable.vmDataTable.draw();
                Swal.fire({
                    title: 'Success',
                    text: `Invoice ${reportNumber} marked as ${action}.`,
                    icon: 'success',
                    showConfirmButton: false,
                    timer: 1500
                });
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
                console.error("There was an error!", error);
            });
        },
        payNow: function (id) {
            var form = document.createElement("form");
            var csrftoken = document.createElement("input");
            csrftoken.setAttribute("type", "hidden");

            form.method = "POST";
            form.action = apiEndpoints.retailerPayInvoice(id);

            csrftoken.value=helpers.getCookie('csrftoken');
            csrftoken.name="csrfmiddlewaretoken";
            form.appendChild(csrftoken);

            document.body.appendChild(form);
            form.submit();
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.reportDatatable.vmDataTable.on('click', 'a[data-action="pay-now"]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-id');
                vm.payNow(id)
            });


            // Listener for the row
            vm.$refs.reportDatatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Retrieve id from the id of the <tr>
                let tr_id = tr.attr('id')
                let proposal_id = tr_id.replace('reportId', '')

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
            console.log(vm.$route.params)
            if(vm.$route.params.reportNumber){
                let reportNumber = DOMPurify.sanitize(vm.$route.params.reportNumber);
                let paymentStatus = DOMPurify.sanitize(vm.$route.params.paymentStatus);
                if('success'===paymentStatus){
                    Swal.fire({
                        title: 'Success',
                        text: `Invoice ${reportNumber} paid successfully.`,
                        icon: 'success',
                        showConfirmButton: true,
                    }).then(function() {
                        vm.$router.push({ name: 'retailer-reports' });
                    });
                } else {
                    Swal.fire({
                        title: 'Failure',
                        text: `Payment for invoice ${reportNumber} failed.`,
                        icon: 'error',
                        showConfirmButton: true,
                    }).then(function() {
                        vm.$router.push({ name: 'retailer-reports' });
                    });
                }

            }
        });
    }
}
</script>

<style scoped>
.swal2-confirm {
    background-color:#efefef;
}
</style>
