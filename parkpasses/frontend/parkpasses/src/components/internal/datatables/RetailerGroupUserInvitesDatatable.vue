<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="CollapsibleFilters" @created="collapsibleComponentMounted" class="mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Retailer</label>
                        <select v-if="retailerGroups" class="form-control" v-model="filterRetailerGroups">
                            <option value="" selected="selected">All</option>
                            <option v-for="retailerGroup in retailerGroups" :value="retailerGroup.id">{{ retailerGroup.name }}</option>
                        </select>
                    </div>
                </div>
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
                    ref="retailerGroupUserInvitesDatatable"
                    :id="datatableId"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
    <RetailerGroupUserInviteApprovalModal @approvalProcessed="approvalProcessed" :retailerGroupUserInvite="selectedRetailerGroupUserInvite" />
</template>

<script>
import datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { apiEndpoints, constants } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import RetailerGroupUserInviteApprovalModal from '@/components/internal/modals/RetailerGroupUserInviteApprovalModal.vue'

import Swal from 'sweetalert2'

export default {
    name: 'RetailerGroupUserInvitesDatatable',
    emits: ['approvalProcessed'],
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        filterRetailerGroupsCacheName: {
            type: String,
            required: false,
            default: 'filterRetailerGroups',
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

            filterRetailerGroups: sessionStorage.getItem(vm.filterRetailerGroupsCacheName) ? sessionStorage.getItem(vm.filterRetailerGroupsCacheName) : '',
            filterProcessingStatus: sessionStorage.getItem(vm.filterProcessingStatusCacheName) ? sessionStorage.getItem(vm.filterProcessingStatusCacheName) : '',
            filterDatetimeCreatedFrom: sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) : '',
            filterDatetimeCreatedTo: sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) : '',

            errorMessage: null,

            selectedRetailerGroupUserInvite: null,

            retailerGroups: null,
            statuses: [
                {id:'P', value:'Paid'},
                {id:'U', value:'Unpaid'},
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
        RetailerGroupUserInviteApprovalModal,
    },
    watch: {
        filterRetailerGroups: function() {
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterRetailerGroupsCacheName, this.filterRetailerGroups);
        },
        filterProcessingStatus: function() {
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterProcessingStatusCacheName, this.filterProcessingStatus);
        },
        filterDatetimeCreatedFrom: function() {
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeCreatedFromCacheName, this.filterDatetimeCreatedFrom);
        },
        filterDatetimeCreatedTo: function() {
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
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
            let num =  this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filterApplied = true
            if(
                this.filterRetailerGroups === '' &&
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
                'Retailer',
                'Email',
                'Status',
                'Date Created',
                'Date Updated',
                'Actions',
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
        columnRetailerGroup: function(){
            return {
                data: "retailer_group_name",
                visible: true,
                name: 'retailer_group_name',
                orderable: false,
                searchable: false,
            }
        },
        columnEmail: function(){
            return {
                data: "email",
                visible: true,
                name: 'email',
                orderable: false,
                searchable: false,
            }
        },
        columnStatus: function(){
            return {
                data: "status_display",
                visible: true,
                className: 'status_display',
                name: 'active',
            }
        },
        columnDatetimeCreated: function(){
            return {
                data: "datetime_created",
                visible: true,
                name: 'datetime_created'
            }
        },
        columnDatetimeUpdated: function(){
            return {
                data: "datetime_updated",
                visible: true,
                name: 'datetime_updated',
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
                    console.log(full.status)
                    let links = '';
                    if('N'==full.status){
                        links +=  `<a href="javascript:void(0)" data-id="${full.id}" data-action="reattempt-to-send-invite">Reattempt to Send Invite</a><br/>`;
                    } else if('S'==full.status) {
                        links +=  `<a href="javascript:void(0)" data-id="${full.id}" data-action="resend-invite">Resend Invite</a><br/>`;
                    } else if('UA'==full.status) {
                        links +=  `<a href="javascript:void(0)" data-id="${full.id}" data-retailer-group-name="${full.retailer_group_name}" data-email="${full.email}" data-action="approve-invite">Approve Invite</a><br/>`;
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
                vm.columnRetailerGroup,
                vm.columnEmail,
                vm.columnStatus,
                vm.columnDatetimeCreated,
                vm.columnDatetimeUpdated,
                vm.columnAction,
            ]

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
                bFilter:false,
                ajax: {
                    "url": apiEndpoints.retailerGroupInviteListInternal + '?format=datatables',
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
                initComplete: function() {
                },
            }
        }
    },
    methods: {
        adjustTableWidth: function(){
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.columns.adjust()
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
        },
        fetchFilterLists: function(){
            let vm = this;

            // Pass Types
            fetch(apiEndpoints.retailerGroupListInternal)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    return Promise.reject(error);
                }
                vm.retailerGroups = data.results
            })
            .catch(error => {
                //this.errorMessage = error;
                console.error("There was an error!", error);
            });

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
                vm.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();
                Swal.fire({
                    title: 'Success',
                    text: `Invoice ${reportNumber} marked as ${action}.`,
                    icon: 'success',
                    showConfirmButton: false,
                    timer: 1500
                });
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        approvalProcessed: function () {
            this.$emit('approvalProcessed')
            this.$refs.retailerGroupUserInvitesDatatable.vmDataTable.draw();
        },
        approveInvite: function (retailerGroupUserInvite) {
            this.selectedRetailerGroupUserInvite = retailerGroupUserInvite;
            let retailerUserGroupInviteApprovalModalElement = document.getElementById('retailerUserGroupInviteApprovalModal')
            let retailerUserGroupInviteApprovalModal = new bootstrap.Modal(retailerUserGroupInviteApprovalModalElement, {});
            retailerUserGroupInviteApprovalModal.show();
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.retailerGroupUserInvitesDatatable.vmDataTable.on('click', 'a[data-action="approve-invite"]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-id');
                let retailerGroupName = $(this).attr('data-retailer-group-name');
                let email = $(this).attr('data-email');
                vm.approveInvite({'id':id, 'retailer_group_name':retailerGroupName, 'email':email});
            });

            // Listener for the row
            vm.$refs.retailerGroupUserInvitesDatatable.vmDataTable.on('click', 'td', function(e) {
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
        this.fetchFilterLists();
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
.swal2-confirm {
    background-color:#efefef;
}
</style>
