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
                        <label for="">Is Admin</label>
                        <select class="form-control" v-model="filterIsAdmin">
                            <option value="" selected="selected">All</option>
                            <option value="0">No</option>
                            <option value="1">Yes</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Date Added From</label>
                        <div class="input-group date" ref="filterDatetimeCreatedFrom">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDatetimeCreatedFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Date Added To</label>
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
                    ref="retailerGroupUsersDatatable"
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
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import Swal from 'sweetalert2'

export default {
    name: 'RetailerGroupUsersDatatable',
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
        filterIsAdminCacheName: {
            type: String,
            required: false,
            default: 'filterIsAdmin',
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
            filterIsAdmin: sessionStorage.getItem(vm.filterIsAdminCacheName) ? sessionStorage.getItem(vm.filterIsAdminCacheName) : '',
            filterDatetimeCreatedFrom: sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedFromCacheName) : '',
            filterDatetimeCreatedTo: sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) ? sessionStorage.getItem(vm.filterDatetimeCreatedToCacheName) : '',

            errorMessage: null,

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
    },
    watch: {
        filterRetailerGroups: function() {
            this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterRetailerGroupsCacheName, this.filterRetailerGroups);
        },
        filterIsAdmin: function() {
            this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterIsAdminCacheName, this.filterIsAdmin);
        },
        filterDatetimeCreatedFrom: function() {
            this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(this.filterDatetimeCreatedFromCacheName, this.filterDatetimeCreatedFrom);
        },
        filterDatetimeCreatedTo: function() {
            this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
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
            let num =  this.$refs.retailerGroupUsersDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filterApplied = true
            if(
                this.filterRetailerGroups === '' &&
                this.filterIsAdmin === '' &&
                this.filterDatetimeCreatedFrom === '' &&
                this.filterDatetimeCreatedTo === ''){
                filterApplied = false
            }
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
                'Retailer Group',
                'Email',
                'Active',
                'Is Admin',
                'Date Added',
                'Date Updated',
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
                data: "emailuser_email",
                visible: true,
                name: 'emailuser_email',
                orderable: false,
                searchable: false,
            }
        },
        columnActive: function(){
            return {
                data: "active",
                visible: true,
                className: 'text-center',
                name: 'active',
                'render': function(row, type, full){
                    let html = '<div class="form-check form-switch ms-5">';
                    let disabled = '';
                    if(full.active){
                        if(full.is_admin && 1==full.retailer_group_admin_user_count){
                            disabled = 'disabled';
                        }
                        html += `<input class="form-check-input" type="checkbox" data-item-id="${full.id}" data-action="toggleUserActive" checked ${disabled}>`;
                    } else {
                        html+= `<input class="form-check-input" type="checkbox" data-item-id="${full.id}" data-action="toggleUserActive"></div>`;
                    }
                    html += '</div>';
                    return html;
                }
            }
        },
        columnIsAdmin: function(){
            return {
                data: "is_admin",
                visible: true,
                className: 'text-center',
                name: 'is_admin',
                'render': function(row, type, full){
                    let html = '<div class="form-check form-switch ms-5">';
                    let disabled = '';
                    if(full.is_admin){
                        if(1==full.retailer_group_admin_user_count){
                            disabled = 'disabled';
                        }
                        html += `<input class="form-check-input" type="checkbox" data-item-id="${full.id}" data-action="toggleUserIsAdmin" checked ${disabled}>`;
                    } else {
                        html+= `<input class="form-check-input" type="checkbox" data-item-id="${full.id}" data-action="toggleUserIsAdmin"></div>`;
                    }
                    html += '</div>';
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
        columnDatetimeUpdated: function(){
            return {
                data: "datetime_updated",
                visible: true,
                name: 'datetime_updated'
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
                vm.columnActive,
                vm.columnIsAdmin,
                vm.columnDatetimeCreated,
                vm.columnDatetimeUpdated,
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
                    "url": apiEndpoints.retailerGroupUserListInternal + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.retailer_group = vm.filterRetailerGroups
                        d.is_admin = vm.filterIsAdmin
                        d.datetime_created_from = vm.filterDatetimeCreatedFrom
                        d.datetime_created_to = vm.filterDatetimeCreatedTo
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                order: [[5, 'desc']],

                columns: columns,
                processing: true,
                pagingType: "full_numbers",
                initComplete: function() {
                },
            }
        }
    },
    methods: {
        draw: function () {
            this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();
        },
        adjustTableWidth: function(){
            this.$refs.retailerGroupUsersDatatable.vmDataTable.columns.adjust()
            this.$refs.retailerGroupUsersDatatable.vmDataTable.responsive.recalc()
        },
        collapsibleComponentMounted: function(){
            this.$refs.CollapsibleFilters.showWarningIcon(this.filterApplied)
        },
        toggleRetailerGroupUserActive: function (id) {
            let vm = this;
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({'csrfmiddlewaretoken':helpers.getCookie('csrftoken'),'id':id})
            };
            fetch(apiEndpoints.internalToggleRetailerGroupUserActive(id), requestOptions).then(async response => {
                if (!response.ok) {
                    const error = response.statusText;
                    return Promise.reject(error);
                }
                this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();
                Swal.fire({
                title: 'Success',
                text: 'User active status toggled successfully.',
                icon: 'success',
                showConfirmButton: false,
                timer: 1000
                });
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        toggleRetailerGroupUserIsAdmin: function (id) {
            let vm = this;
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({'csrfmiddlewaretoken':helpers.getCookie('csrftoken'),'id':id})
            };
            fetch(apiEndpoints.internalToggleRetailerGroupUserIsAdmin(id), requestOptions).then(async response => {
                if (!response.ok) {
                    const error = response.statusText;
                    return Promise.reject(error);
                }
                // It's important to redraw the datatable because to disable the toggle if there is only one
                // admin user left in a retailer group
                this.$refs.retailerGroupUsersDatatable.vmDataTable.draw();
                Swal.fire({
                title: 'Success',
                text: 'User admin status toggled successfully.',
                icon: 'success',
                showConfirmButton: false,
                timer: 1000
                });
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
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
        addEventListeners: function(){
            let vm = this;
            vm.$refs.retailerGroupUsersDatatable.vmDataTable.on('click', 'input[data-action="toggleUserActive"]', function(e) {
                let id = $(this).data('item-id');
                vm.toggleRetailerGroupUserActive(id);
            });
            vm.$refs.retailerGroupUsersDatatable.vmDataTable.on('click', 'input[data-action="toggleUserIsAdmin"]', function(e) {
                let id = $(this).data('item-id');
                vm.toggleRetailerGroupUserIsAdmin(id);
            });

            // Listener for the row
            vm.$refs.retailerGroupUsersDatatable.vmDataTable.on('click', 'td', function(e) {
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
    },
    expose: ['draw'],
}
</script>

<style scoped>
.swal2-confirm {
    background-color:#efefef;
}
</style>
