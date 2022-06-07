<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted" class="mb-2">
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Type</label>
                        <select class="form-control" v-model="filterApplicationType">
                            <option value="all">All</option>
                            <option v-for="type in application_types" :value="type.code">{{ type.description }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterApplicationStatus">
                            <option value="all">All</option>
                            <option v-for="status in application_statuses" :value="status.code">{{ status.description }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Lodged From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
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
                        <label for="">Lodged To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                            <!--
                            <span class="input-group-addon">
                                <span class="fa fa-calendar"></span>
                            </span>
                            -->
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <!--div v-if="is_external" class="row">
            <div class="col-md-12">
                <div class="text-end">
                    <button type="button" class="btn btn-primary mb-2" @click="new_application_button_clicked"><i class="fa-solid fa-circle-plus"></i> New Application</button>
                </div>
            </div>
        </div-->

        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="application_datatable"
                    :id="datatable_id"
                    :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>

import datatable from '@/utils/vue/datatable.vue'
import { v4 as uuid } from 'uuid';
import { api_endpoints } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'

export default {
    name: 'TableApplications',
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        email_user_id_assigned: {
            type: Number,
            required: false,
            default: 0,
        },
        filterApplicationType_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationType',
        },
        filterApplicationStatus_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationStatus',
        },
        filterApplicationLodgedFrom_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedFrom',
        },
        filterApplicationLodgedTo_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedTo',
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'applications-datatable-' + uuid(),

            // selected values for filtering
            filterApplicationType: sessionStorage.getItem(vm.filterApplicationType_cache_name) ? sessionStorage.getItem(vm.filterApplicationType_cache_name) : 'all',
            filterApplicationStatus: sessionStorage.getItem(vm.filterApplicationStatus_cache_name) ? sessionStorage.getItem(vm.filterApplicationStatus_cache_name) : 'all',
            filterProposalLodgedFrom: sessionStorage.getItem(vm.filterProposalLodgedFrom_cache_name) ? sessionStorage.getItem(vm.filterProposalLodgedFrom_cache_name) : '',
            filterProposalLodgedTo: sessionStorage.getItem(vm.filterProposalLodgedTo_cache_name) ? sessionStorage.getItem(vm.filterProposalLodgedTo_cache_name) : '',

            // filtering options
            application_types: [],
            application_statuses: [],

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
        filterApplicationStatus: function() {
            this.$refs.application_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterApplicationStatus_cache_name, this.filterApplicationStatus);
        },
        filterApplicationType: function() {
            this.$refs.application_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterApplicationType_cache_name, this.filterApplicationType);
        },
        filterProposalLodgedFrom: function() {
            this.$refs.application_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterProposalLodgedFrom_cache_name, this.filterProposalLodgedFrom);
        },
        filterProposalLodgedTo: function() {
            this.$refs.application_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterProposalLodgedTo_cache_name, this.filterProposalLodgedTo);
        },
        filterApplied: function(){
            if (this.$refs.collapsible_filters){
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        number_of_columns: function() {
            let num =  this.$refs.application_datatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(this.filterApplicationStatus.toLowerCase() === 'all' && this.filterApplicationType.toLowerCase() === 'all' &&
                this.filterProposalLodgedFrom.toLowerCase() === '' && this.filterProposalLodgedTo.toLowerCase() === ''){
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
        is_external: function() {
            return this.level == 'external'
        },
        is_internal: function() {
            return this.level == 'internal'
        },
        dtHeaders: function(){
            if (this.is_external){
                return ['id', 'Number', 'Type', 'Submitter', 'Applicant', 'Status', 'Lodged On', 'Action',]
            }
            if (this.is_internal){
                return ['id', 'Number', 'Type', 'Submitter', 'Applicant', 'Status', 'Lodged On', 'Assigned Officer', 'Action']
            }
        },
        column_id: function(){
            let vm = this
            return {
                // 1. ID
                data: "id",
                orderable: false,
                searchable: false,
                visible: false,
                'render': function(row, type, full){
                    if(vm.debug){
                        console.log(full)
                    }
                    return full.id
                }
            }
        },
        column_lodgement_number: function(){
            return {
                // 2. Lodgement Number
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    if (full.migrated){
                        return full.lodgement_number + ' (M)'
                    } else {
                        return full.lodgement_number
                    }
                },
                name: 'lodgement_number',
            }
        },
        column_type: function(){
            return {
                // 3. Type (This corresponds to the 'ApplicationType' at the backend)
                data: "id",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    return full.application_type.name_display
                },
                name: 'application_type',
            }
        },
        column_submitter: function(){
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    if (full.submitter){
                        return full.submitter.fullname
                    } else {
                        return ''
                    }
                }
            }
        },
        column_applicant: function(){
            return {
                data: "id",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    /*
                    if (full.submitter){
                        return `${full.submitter.first_name} ${full.submitter.last_name}`
                    }
                    return ''
                    */
                    return full.applicant_name
                },
                //name: 'submitter__first_name, submitter__last_name',
            }
        },
        column_status: function(){
            let vm = this
            return {
                // 5. Status
                data: "id",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    if (vm.is_internal){
                        return full.processing_status
                    }
                    return full.customer_status
                }
            }
        },
        column_lodged_on: function(){
            return {
                // 6. Lodged
                data: "id",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    if (full.lodgement_date){
                        return moment(full.lodgement_date).format('DD/MM/YYYY')
                    }
                    return ''
                },
                name: 'lodgement_date',
            }
        },
        column_assigned_officer: function(){
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    if (full.assigned_officer){
                        return full.assigned_officer.fullname
                    } else {
                        return ''
                    }
                },
                name: 'assigned_officer__first_name, assigned_officer__last_name, assigned_approver__first_name, assigned_approver__last_name',
            }
        },
        column_action: function(){
            let vm = this
            return {
                // 8. Action
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    let links = '';
                    if (vm.is_internal){
                        if(full.accessing_user_can_process){
                            links +=  `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                        } else {
                            links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                        }
                    }
                    if (vm.is_external){
                        if (full.can_user_edit) {
                            links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                            links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                        }
                        else if (full.can_user_view) {
                            links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                        }
                        //for (let invoice of full.invoices){
                        //    console.log(invoice.payment_status.toLowerCase())
                        //    if (invoice.payment_status.toLowerCase() === 'unpaid' || invoice.payment_status.toLowerCase() === 'partially paid'){
                        //        links +=  `<a href='/application_fee_existing/${full.id}'>Pay</a>`
                        //    }
                        //}
                        //if (full.document_upload_url){
                        //    links +=  `<a href='${full.document_upload_url}'>Upload Documents</a>`
                        //}
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
            if(vm.is_external){
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_type,
                    vm.column_submitter,
                    vm.column_applicant,
                    vm.column_status,
                    vm.column_lodged_on,
                    //vm.column_assigned_officer,
                    vm.column_action,
                ]
                search = false
            }
            if(vm.is_internal){
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_type,
                    vm.column_submitter,
                    vm.column_applicant,
                    vm.column_status,
                    vm.column_lodged_on,
                    vm.column_assigned_officer,
                    vm.column_action,
                ]
                search = true
            }

            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                rowCallback: function (row, proposal){
                    let row_jq = $(row)
                    row_jq.attr('id', 'proposal_id_' + proposal.id)
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": api_endpoints.proposals_paginated_list + '?format=datatables&email_user_id_assigned=' + vm.email_user_id_assigned,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.filter_application_type = vm.filterApplicationType
                        d.filter_application_status = vm.filterApplicationStatus
                        d.filter_lodged_from = vm.filterProposalLodgedFrom
                        d.filter_lodged_to = vm.filterProposalLodgedTo
                        d.level = vm.level
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                order: [[1, 'desc']],

                columns: columns,
                processing: true,
                initComplete: function() {
                },
            }
        }
    },
    methods: {
        adjust_table_width: function(){
            this.$refs.application_datatable.vmDataTable.columns.adjust()
            this.$refs.application_datatable.vmDataTable.responsive.recalc()
        },
        collapsible_component_mounted: function(){
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        //getActionDetailTable: function(sticker){
        //    let thead = `<thead>
        //                    <tr>
        //                        <th scope="col">Date</th>
        //                        <th scope="col">User</th>
        //                        <th scope="col">Action</th>
        //                        <th scope="col">Date of Lost</th>
        //                        <th scope="col">Date of Returned</th>
        //                        <th scope="col">Reason</th>
        //                    </tr>
        //                <thead>`
        //    let tbody = ''
        //    for (let detail of sticker.sticker_action_details){
        //        tbody += `<tr>
        //            <td>${moment(detail.date_updated).format('DD/MM/YYYY')}</td>
        //            <td>${detail.user_detail ? detail.user_detail.first_name : ''} ${detail.user_detail ? detail.user_detail.last_name : ''} </td>
        //            <td>${detail.action ? detail.action : ''}</td>
        //            <td>${detail.date_of_lost_sticker ? moment(detail.date_of_lost_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.date_of_returned_sticker ? moment(detail.date_of_returned_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.reason}</td>
        //        </tr>`
        //    }
        //    tbody = '<tbody>' + tbody + '</tbody>'

        //    let details = '<table class="table table-striped table-bordered table-sm table-sticker-details" id="table-sticker-details-' + sticker.id + '">' + thead + tbody + '</table>'
        //    return details
        //},
        new_application_button_clicked: async function(){
            //await this.$router.isReady()
            console.log(this.$router)
            await this.$router.push({
                name: 'apply_proposal'
            })
            console.log(" new application")
        },
        discardProposal: function(proposal_id) {
            let vm = this;
            swal({
                title: "Discard Application",
                text: "Are you sure you want to discard this application?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Application',
                confirmButtonColor:'#dc3545'
            }).then(() => {
                fetch(api_endpoints.discard_proposal(proposal_id), { method: 'DELETE', })
                .then((response) => {
                    swal(
                        'Discarded',
                        'Your application has been discarded',
                        'success'
                    )
                    //vm.$refs.application_datatable.vmDataTable.ajax.reload();
                    vm.$refs.application_datatable.vmDataTable.draw();
                }, (error) => {
                });
            },(error) => {

            });
        },
        fetchFilterLists: function(){
            let vm = this;

            // Application Types
            fetch(api_endpoints.application_types_dict+'?apply_page=False').then((response) => {
                vm.application_types = response.body
            },(error) => {
            })

            // Application Statuses
            fetch(api_endpoints.application_statuses_dict).then((response) => {
                if (vm.is_internal){
                    vm.application_statuses = response.body.internal_statuses
                } else {
                    vm.application_statuses = response.body.external_statuses
                }
            },(error) => {
            })
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.application_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id)
            });
            /*
            // update to bs5
            // Lodged From
            $(vm.$refs.proposalDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalDateFromPicker).data('DateTimePicker').date()) {
                    // DateFrom has been picked
                    vm.filterProposalLodgedFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.proposalDateFromPicker).data('date') === "") {
                    vm.filterProposalLodgedFrom = "";
                    $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(false);
                }
            });

            // Lodged To
            $(vm.$refs.proposalDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateToPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalDateToPicker).data('DateTimePicker').date()) {
                    // DateTo has been picked
                    vm.filterProposalLodgedTo = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(e.date);
                }
                else if ($(vm.$refs.proposalDateToPicker).data('date') === "") {
                    vm.filterProposalLodgedTo = "";
                    $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(false);
                }
            });
            */

            // Listener for thr row
            vm.$refs.application_datatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Retrieve id from the id of the <tr>
                let tr_id = tr.attr('id')
                let proposal_id = tr_id.replace('proposal_id_', '')

                let first_td = tr.children().first()
                if(first_td.hasClass(vm.td_expand_class_name)){
                    // Expand

                    // If we don't need to retrieve the data from the server, follow the code below
                    let contents = '<div><strong>Site:</strong> (site name here)</div><div><strong>Group:</strong> (group name here)</div>'
                    let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
                    details_elem.hide()
                    details_elem.insertAfter(tr)
                    details_elem.fadeIn(1000)

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
</style>
