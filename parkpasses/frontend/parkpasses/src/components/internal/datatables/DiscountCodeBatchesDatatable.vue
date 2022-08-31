<template>
    <div>
        <div class="row mb-3">
            <div class="col">
                <button @click="addDiscountCodeBatch" class="btn licensing-btn-primary float-end" data-bs-toggle="modal"
                    data-bs-target="#discountCodeBatchModal">Add Discount Code Batch</button>
            </div>
        </div>
        <div v-if="successMessage" class="row mx-1">
            <div id="successMessageAlert" class="col alert alert-success show fade" role="alert">
                {{ successMessage }}
            </div>
        </div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsibleComponentMounted"
            class="mb-2">
            <div class="row mb-3">
                <div class="col-md-3">
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
                        <label for="filterDatetimeStartFrom">Start Date From</label>
                        <div class="input-group date" ref="voucherDatetimeToEmailFrom">
                            <input type="date" name="filterDatetimeStartFrom" class="form-control"
                                placeholder="DD/MM/YYYY" v-model="filterDatetimeStartFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filterDatetimeStartTo">Start Date To</label>
                        <div class="input-group date" ref="voucherDatetimeToEmailTo">
                            <input type="date" name="filterDatetimeStartTo" class="form-control"
                                placeholder="DD/MM/YYYY" v-model="filterDatetimeStartTo">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filterDatetimeExpiryFrom">End Date From</label>
                        <div class="input-group date" ref="filterDatetimeExpiryFrom">
                            <input type="date" name="filterDatetimeExpiryFrom" class="form-control"
                                placeholder="DD/MM/YYYY" v-model="filterDatetimeExpiryFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filterDatetimeExpiryTo">End Date To</label>
                        <div class="input-group date" ref="filterDatetimeExpiryTo">
                            <input type="date" name="filterDatetimeExpiryTo" class="form-control"
                                placeholder="DD/MM/YYYY" v-model="filterDatetimeExpiryTo">
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>
        <div :if="errorMessage">{{ errorMessage }}</div>
        <div class="row">
            <div class="col-lg-12">
                <datatable ref="discountCodeBatchDatatable" :id="datatableId" :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders" />
            </div>
        </div>
    </div>
    <DiscountCodeBatchFormModal @saveSuccess="saveSuccess" :selectedDiscountCodeBatch="selectedDiscountCodeBatch" />
</template>

<script>
import datatable from '@/utils/vue/Datatable.vue'
import { v4 as uuid } from 'uuid';
import { apiEndpoints } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/CollapsibleComponent.vue'
import DiscountCodeBatchFormModal from '@/components/internal/modals/DiscountCodeBatchFormModal.vue'

export default {
    name: 'DiscountCodeBatchDatatable',
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'retailer', 'external'];
                return options.indexOf(val) != -1 ? true : false;
            }
        },
        filterStatusCacheName: {
            type: String,
            required: false,
            default: 'filterDiscountCodeBatchStatus',
        },
    },
    data() {
        let vm = this;
        return {
            datatableId: 'discount-code-batch-datatable-' + uuid(),

            filterStatus: sessionStorage.getItem(vm.filterStatusCacheName) ? sessionStorage.getItem(vm.filterStatusCacheName) : 'all',
            filterDatetimeStartFrom: '',
            filterDatetimeStartTo: '',
            filterDatetimeExpiryFrom: '',
            filterDatetimeExpiryTo: '',

            selectedDiscountCodeBatch: null,
            discountCodeBatchModal: null,

            successMessage: null,
            errorMessage: null,

            // filtering options
            passTypesDistinct: [],
            passProcessingStatusesDistinct: [],

            dateFormat: 'DD/MM/YYYY',

            statuses: [
                'Future',
                'Current',
                'Expired',
            ],

            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true
            },

            // For Expandable row
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        }
    },
    components: {
        datatable,
        CollapsibleFilters,
        DiscountCodeBatchFormModal,
    },
    watch: {
        filterStatus: function () {
            this.$refs.discountCodeBatchDatatable.vmDataTable.draw();
            sessionStorage.setItem(this.filterStatusCacheName, this.filterStatus);
        },
    },
    computed: {
        numberOfColumns: function () {
            let num = this.$refs.discountCodeBatchDatatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function () {
            let filter_applied = true
            if (
                this.filterStatus.toLowerCase() === 'all' &&
                this.filterDatetimeStartFrom.toLowerCase() === '' &&
                this.filterDatetimeStartTo.toLowerCase() === '' &&
                this.filterDatetimeExpiryFrom.toLowerCase() === '' &&
                this.filterDatetimeExpiryTo.toLowerCase() === ''

            ) {
                filter_applied = false;
            }
            return filter_applied;
        },
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        dtHeaders: function () {
            return [
                'id',
                'Number',
                'Creation Date',
                'Start Date',
                'End Date',
                'Discount Amount',
                'Discount Percentage',
                'Created By',
                'Uses',
                'Status',
                'Action',
                'Discount code(s)',
                'Valid for Pass Type(s)',
                'Valid for User(s)',
            ]
        },
        columnId: function () {
            let vm = this
            return {
                data: "id",
                visible: false,
                'render': function (row, type, full) {
                    if (vm.debug) {
                        console.log(full)
                    }
                    return full.id
                }
            }
        },
        column_discount_code_batch_number: function () {
            return {
                data: "discount_code_batch_number",
                visible: true,
                name: 'discount_code_batch_number',
                orderable: true,
            }
        },
        column_datetime_created: function () {
            return {
                data: "datetime_created",
                visible: true,
                name: 'datetime_created',
                'render': function (row, type, full) {
                    const date = new Date(full.datetime_created);
                    return date.toLocaleDateString();
                }
            }
        },
        column_datetime_start: function () {
            return {
                data: "datetime_start",
                visible: true,
                name: 'datetime_start',
                'render': function (row, type, full) {
                    const date = new Date(full.datetime_start);
                    return date.toLocaleDateString();
                }
            }
        },
        column_datetime_expiry: function () {
            return {
                data: "datetime_expiry",
                visible: true,
                name: 'datetime_expiry',
                'render': function (row, type, full) {
                    const date = new Date(full.datetime_expiry);
                    return date.toLocaleDateString();
                }
            }
        },
        column_discount_amount: function () {
            return {
                data: "discount_amount",
                visible: true,
                name: 'discount_amount',
                'render': function (row, type, full) {
                    if (full.discount_amount) {
                        return `$${full.discount_amount}`
                    }
                    return '';
                }
            }
        },
        column_discount_percentage: function () {
            return {
                data: "discount_percentage",
                visible: true,
                name: 'discount_percentage',
                'render': function (row, type, full) {
                    if (full.discount_percentage) {
                        return `${full.discount_percentage}%`;
                    }
                    return '';
                }
            }
        },
        column_created_by: function () {
            return {
                data: "created_by_name",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'created_by_name',
            }
        },
        column_times_each_code_can_be_used: function () {
            return {
                data: "times_each_code_can_be_used",
                visible: true,
                name: 'times_each_code_can_be_used',
                'render': function (row, type, full) {
                    if (!full.times_each_code_can_be_used) {
                        return '<span class="to-infinity-and-beyond">&infin;</span>';
                    }
                    return full.times_each_code_can_be_used;
                }
            }
        },
        columnStatus: function () {
            return {
                data: "status",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'status'

            }
        },
        columnAction: function () {
            let vm = this
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    let links = '';
                    let today = new Date();
                    let expiryDate = new Date(full.datetime_expiry);
                    let editLink = vm.$router.resolve({
                        name: 'internal-discount-code-batch-form',
                        params: { discountCodeBatchId: full.id }
                    });
                    if (today < expiryDate) {
                        links += `<a href="${editLink.href}">Edit</a> | `;
                        links += `<a href="javascript:void(0)" data-item-id="${full.id}" data-action="invalidate" data-discount-code-batch-number="${full.discount_code_batch_number}">Invalidate</a>`;
                    }
                    return links;
                }
            }
        },
        columnDiscountCodes: function () {
            return {
                data: "discount_codes",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'discount_codes',
                'render': function (row, type, full) {
                    let discountCodes = '';
                    if (1 == full.discount_codes.length) {
                        return '<span class="badge org-badge-primary">' + full.discount_codes[0].code + '</span>';

                    } else if (1 < full.discount_codes.length) {
                        return `<a data-id="${full.id}" data-action="view-discount-codes" href="${apiEndpoints.discountCodesXlsx(full.id)}">View ${full.discount_codes.length} Discount Codes</a>`;
                    } else {
                        return '<span class="badge badge-danger">Error no codes were created</span>';
                    }
                    return discountCodes;
                }
            }
        },
        columnValidPassTypes: function () {
            return {
                data: "valid_pass_types",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'valid_pass_types',
                'render': function (row, type, full) {
                    let validPassTypes = '';
                    if (full.valid_pass_types.length) {
                        full.valid_pass_types.forEach(function (validPassType, index) {
                            validPassTypes += '<span class="badge org-badge-primary">' + validPassType.pass_type_display_name + '</span>&nbsp;';

                        });
                    } else {
                        return '<span class="badge org-badge-primary">All Pass Types</span>';
                    }
                    return validPassTypes;
                }
            }
        },
        columnValidUsers: function () {
            return {
                data: "valid_users",
                visible: true,
                orderable: false,
                searchable: false,
                name: 'valid_users',
                'render': function (row, type, full) {
                    let validUsers = '';
                    if (full.valid_users.length) {
                        full.valid_users.forEach(function (validUser, index) {
                            validUsers += '<span class="badge org-badge-primary">' + validUser.display_name + '</span>&nbsp;';

                        });
                    } else {
                        return '<span class="badge org-badge-primary">All Users</span>';
                    }
                    return validUsers;
                }
            }
        },
        dtOptions: function () {
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
                vm.column_discount_code_batch_number,
                vm.column_datetime_created,
                vm.column_datetime_start,
                vm.column_datetime_expiry,
                vm.column_discount_amount,
                vm.column_discount_percentage,
                vm.column_created_by,
                vm.column_times_each_code_can_be_used,
                vm.columnStatus,
                vm.columnAction,
                vm.columnDiscountCodes,
                vm.columnValidPassTypes,
                vm.columnValidUsers,
            ]
            search = true

            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                rowCallback: function (row, pass) {
                    let row_jq = $(row)
                    row_jq.attr('id', 'pass_id_' + pass.id)
                    //row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ajax: {
                    "url": apiEndpoints.discountCodeBatchPaginatedList + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        //d.option__pricing_window__datetime_to_email__name = vm.filterStatus
                        d.processing_status = vm.filterPassProcessingStatus
                        //d.filter_lodged_from = vm.filterDatetimeStartFrom
                        //d.filter_lodged_to = vm.filterDatetimeStartTo
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
                initComplete: function () {
                },
            }
        }
    },
    methods: {
        adjustTableWidth: function () {
            this.$refs.discountCodeBatchDatatable.vmDataTable.columns.adjust();
            this.$refs.discountCodeBatchDatatable.vmDataTable.responsive.recalc();
        },
        collapsibleComponentMounted: function () {
            this.$refs.collapsible_filters.showWarningIcon(this.filterApplied)
        },
        saveSuccess: function ({ message, discountCodeBatch }) {
            window.scrollTo(0, 0);
            this.successMessage = message;
            console.log(JSON.stringify(discountCodeBatch));
            this.$nextTick(() => {
                $('#successMessageAlert').fadeOut(4000, function () {
                    this.successMessage = null;
                });
            });
            this.$refs.discountCodeBatchDatatable.ajax.reload();
        },
        addDiscountCodeBatch: function () {
            console.log('addDiscountCodeBatch');
            this.selectedDiscountCodeBatch = null;
        },
        editDiscountCodeBatch: function (id) {
            this.selectedDiscountCodeBatch = id;
            console.log("selectedDiscountCodeBatch = " + this.selectedDiscountCodeBatch);
            this.discountCodeBatchModal.show();
        },
        invalidateDiscountCodeBatch: function (discountCodeBatch) {
            alert('About to invalidate discount code batch = ' + discountCodeBatch.discountCodeBatchNumber);
        },
        addEventListeners: function () {
            let vm = this
            vm.$refs.discountCodeBatchDatatable.vmDataTable.on('click', 'a[data-action="edit"]', function (e) {
                e.preventDefault();
                let action = $(this).data('action');
                let id = $(this).data('item-id');
                console.log(action + id);
                vm.editDiscountCodeBatch(id);
            });
            vm.$refs.discountCodeBatchDatatable.vmDataTable.on('click', 'a[data-action="invalidate"]', function (e) {
                e.preventDefault();
                let id = $(this).data('item-id');
                let discountCodeBatchNumber = $(this).data('discount-code-batch-number');
                vm.invalidateDiscountCodeBatch({ id, discountCodeBatchNumber });
            });
        },
    },
    created: function () {

    },
    mounted: function () {
        let vm = this;
        vm.addEventListeners();
        let discountCodeBatchModal = document.getElementById('discountCodeBatchModal');
        discountCodeBatchModal.addEventListener('shown.bs.modal', function () {
            // This next line is needed to reveal the placeholders in the select2s
            $('.select2-search__field').attr("style", "width:750px");
            $('#discountCodeBatchModal').find('input:visible:first').focus();
        });
        this.discountCodeBatchModal = new bootstrap.Modal(discountCodeBatchModal);
    }
}
</script>

<style scoped>
td.child span.dtr-title {
    width: 200px;
}
</style>
