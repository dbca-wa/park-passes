<template lang="html">
    <div v-if="pass" class="container" id="retailerPass">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>{{ pass.pass_number }} - {{ pass.pass_type }}</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-3">
                        <StatusPanel :status="pass.processing_status_display_name" :badge="true" :badgeClass="badgeClass" class="pt-3" />
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
                        <SectionToggle :label="pass.pass_number + ' - ' + pass.pass_type">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div v-if="isPassCancelled" class="row">
                                <div class="col">
                                    <BootstrapAlert type="warning" icon="exclamation-triangle-fill">
                                        This pass has been cancelled and can't be modified.
                                    </BootstrapAlert>
                                </div>
                            </div>
                            <div v-if="pdfUrl" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Pass PDF</label>
                                <div class="col-sm-6">
                                    <a :href="pdfUrl" target="blank">{{ pass.park_pass_pdf }}</a>
                                </div>
                            </div>
                            <div v-if="pass.invoice_link" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Invoice PDF</label>
                                <div class="col-sm-6">
                                    <a :href="pass.invoice_link" target="blank">Ledger Invoice PDF</a>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="soldViaName" class="col-sm-4 col-form-label">Sold Via</label>
                                <div class="col-sm-6">
                                    <span class="form-text">
                                        {{ pass.sold_via_name }}
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">First Name</label>
                                <div class="col-sm-6">
                                    <input class="form-control" name="firstName" type="text" v-model="pass.first_name" :disabled="fieldDisabled">
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Last Name</label>
                                <div class="col-sm-6">
                                    <input class="form-control" name="lastName" type="text" v-model="pass.last_name" :disabled="fieldDisabled">
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Email Address</label>
                                <div class="col-sm-8">
                                    <input class="form-control" name="email" type="text" v-model="pass.email" :disabled="fieldDisabled">
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Mobile Number</label>
                                <div class="col-sm-8">
                                    <input class="form-control" name="mobile" type="text" v-model="pass.mobile" :disabled="fieldDisabled">
                                </div>
                            </div>
                            <div v-if="pass.postcode" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Postcode</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.postcode }}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Duration</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.duration }}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="startDate" class="col-sm-4 col-form-label">Start Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="startDate" type="date" v-model="pass.date_start" :disabled="fieldDisabled">
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">End Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="date" v-model="pass.date_expiry" readonly>
                                    </span>
                                </div>
                            </div>
                            <div v-if="!pass.prevent_further_vehicle_updates" class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">Vehicle Registration <span v-if="pass.vehicle_registration_2">1</span></label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="text" v-model="pass.vehicle_registration_1" maxlength="10" :disabled="fieldDisabled">
                                    </span>
                                </div>
                            </div>
                            <div v-if="showSecondVehicleRego" class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">Vehicle Registration 2</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="text" v-model="pass.vehicle_registration_2" maxlength="10" :disabled="fieldDisabled">
                                    </span>
                                </div>
                            </div>

                            </form>
                        </SectionToggle>
                        <SectionToggle v-if="showDiscountsPanel" label="Concession, Voucher &amp; Discounts" class="mb-5">
                            <form>
                            <div v-if="pass.concession_type" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Type</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.concession_type }}</span>
                                </div>
                            </div>
                            <div v-else class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Used for Purchase</label>
                                <div class="col-sm-8">
                                    <span class="form-text">No</span>
                                </div>
                            </div>
                            <div v-if="pass.concession_discount_percentage" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Discount</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.concession_discount_percentage }}% Off</span>
                                </div>
                            </div>
                            <div v-if="pass.concession_card_number" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Card Number</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.concession_card_number }}</span>
                                </div>
                            </div>
                            <div v-if="pass.voucher_number" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Voucher Used for Payment</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.voucher_number }}</span>
                                </div>
                            </div>
                            <div v-if="pass.voucher_transaction_amount" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Voucher Transaction Amount</label>
                                <div class="col-sm-8">
                                    <span class="form-text">${{ pass.voucher_transaction_amount }}</span>
                                </div>
                            </div>
                            <div v-if="pass.discount_code_used" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Discount Code Used</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.discount_code_used }}</span>
                                </div>
                            </div>
                            <div v-if="pass.discount_code_discount" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Discount Amount</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{pass.discount_code_discount}}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">RAC Discount Used for Purchase</label>
                                <div class="col-sm-8">
                                    <span v-if="pass.rac_discount_percentage" class="form-text">Yes</span>
                                    <span v-else class="form-text">No</span>
                                </div>
                            </div>
                            <div v-if="pass.rac_discount_percentage" class="row mb-1">
                                <label class="col-sm-4 col-form-label">RAC Discount Percentage</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{pass.rac_discount_percentage}}% OFF</span>
                                </div>
                            </div>
                            </form>
                        </SectionToggle>
                    </div>
                </div>

            </div>
        </div>
        <div id="printerDiv" style="display:none"></div>

    </div>
    <footer v-if="pass" class="fixed-bottom mt-auto py-3 bg-light">
        <div class="container d-flex justify-content-end">
            <template v-if="!loading">
                <button @click="returnToPassesDash" class="btn licensing-btn-primary me-2">Exit</button>
                <button v-if="!fieldDisabled" @click="validateForm(true)" class="btn licensing-btn-primary me-2">Save and Exit</button>
                <button v-if="!fieldDisabled" @click="validateForm(false)" class="btn licensing-btn-primary">Save and Continue Editing</button>
            </template>
            <template v-else>
                <button class="btn licensing-btn-primary px-4 ms-2">
                    <div class="spinner-border spinner-border-sm text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </button>
            </template>
        </div>
    </footer>
    <div v-if="!pass">
        <BootstrapSpinner :isLoading="true" />
    </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

import Swal from 'sweetalert2'


import SectionToggle from '@/components/forms/SectionToggle.vue'
import CommsLog from '@/components/common/CommsLog.vue'
import StatusPanel from '@/components/common/StatusPanel.vue'

export default {
    name: "PassForm",
    props: {
        created: {
            default: false,
            required: false,
        }
    },
    data() {
        return {
            passId: null,
            pass: null,
            listUserActionsLogUrl: null,
            listCommsUrl: null,
            createCommUrl: apiEndpoints.createCommunicationsLogEntry,
            pdfUrl: null,
            appLabel: constants.PARKPASSES_APP_LABEL,
            model: constants.PARKPASSES_MODELS_PASS,
            loading: false,
        }
    },
    computed: {
        showDiscountsPanel: function() {
            return this.pass.concession_type || this.pass.voucher_number || this.pass.discount_code_used;
        },
        isHolidayPass: function () {
            return constants.HOLIDAY_PASS_NAME==this.pass.pass_type_name ? true : false;
        },
        isPassCancelled: function () {
            return (constants.PASS_PROCESSING_STATUS_CANCELLED==this.pass.processing_status) ? true : false;
        },
        fieldDisabled: function () {
            return this.isPassCancelled || this.hasPassExpired || !this.pass.user_can_edit;
        },
        showSecondVehicleRego: function () {
            if(this.isHolidayPass){
                return false;
            }
            if(this.pass.prevent_further_vehicle_updates){
                return false;
            }
            return true;
        },
        formattedMobile: function () {
            if(!this.pass){
                return '';
            }
            console.log('this.pass.mobile.length = ' + this.pass.mobile.length)
            if(10!=this.pass.mobile.length){
                return this.pass.mobile;
            }
            return this.pass.mobile.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3');
        },
        badgeClass: function () {
            return helpers.getStatusBadgeClass(this.pass.processing_status_display_name);
        },
    },
    components: {
        SectionToggle,
        CommsLog,
        BootstrapSpinner,
        BootstrapAlert,
        StatusPanel,
    },
    methods: {
        returnToPassesDash: function() {
            this.$router.push({name: 'retailer-dash'});
        },
        fetchPass: function (passId) {
            let vm = this;
            fetch(apiEndpoints.retrievePassRetailer(passId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.pass = data
                //vm.pass.date_start = helpers.getDateFromDatetime(vm.pass.date_start);
                //vm.pass.date_expiry = helpers.getDateFromDatetime(vm.pass.date_expiry);
                console.log(vm.pass);
                console.log('date_start = ' + vm.pass.date_start);
                console.log('pass.user = ' + vm.pass.user)

                vm.listUserActionsLogUrl = apiEndpoints.listUserActionsLog(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_PASS,
                    vm.pass.id
                )
                vm.listCommsUrl = apiEndpoints.listCommunicationsLogEntries(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_PASS,
                    vm.pass.id
                )
                vm.pdfUrl = apiEndpoints.retailerParkPassPdf(vm.pass.id)
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
                console.error("There was an error!", error);
            });
        },
        submitForm: function (exitAfter) {
            let vm = this;
            vm.loading = true;
            vm.pass.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.pass);
            // vm.pass.date_start  = new Date(vm.pass.date_start).toLocaleString();
            // vm.pass.date_expiry  = new Date(vm.pass.date_expiry).toLocaleString();
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pass)
            };
            fetch(apiEndpoints.updatePassRetailer(vm.pass.id), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }

                    Swal.fire({
                        title: 'Success',
                        text: 'Park Pass updated successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    if(exitAfter) {
                        vm.$router.push({name: 'retailer-dash'});
                    }
                    vm.pass.date_expiry = data.date_expiry
                    var forms = document.querySelectorAll('.needs-validation');
                    Array.prototype.slice.call(forms).forEach(function (form) {
                        form.classList.remove('was-validated');
                    });
                    vm.pass.why = '';
                    $('#reasonFiles').val('');
                    vm.loading = false;
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.SYSTEM;
                    console.error("There was an error!", error);
                });
            return false;
        },
        validateForm: function (exitAfter) {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation');
            Array.prototype.slice.call(forms)
                .forEach(function (form) {
                    if (form.checkValidity()) {
                        vm.submitForm(exitAfter);
                    } else {
                        form.classList.add('was-validated');
                        $(".invalid-feedback:visible:first").siblings('input').focus();
                    }
                });
            return false;
        }
    },
    created: function() {
        const route = useRoute()
        this.fetchPass(route.params['passId']);
    },
    mounted: function () {
        if(this.created){
            Swal.fire({
                title: 'Success',
                text: 'Park Pass created successfully.',
                icon: 'success',
                confirmButtonText: 'OK'
            })
        }
    }
}
</script>

<style scoped>
    .form-text{
        display:block;
        padding: 0.375rem 0.75rem 0 0;
        margin:0;
        font-size:1rem;
    }

    .form-switch{
         padding-top:0.375em;
    }
</style>
