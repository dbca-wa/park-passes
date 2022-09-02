<template lang="html">
    <div v-if="pass" class="container" id="internalPass">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>{{ pass.pass_number }} - {{ pass.pass_type }}</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-3">
                        <CommsLog commsUrl="" :logsUrl="logsUrl" commAddUrl="" />
                        <StatusPanel :status="pass.processing_status_display_name" class="pt-3" />
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
                        <SectionToggle :label="'Park Pass - ' + pass.pass_type">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Pass Holder</label>
                                <div class="col-sm-6">
                                    <span class="form-text">{{ pass.first_name + ' ' + pass.last_name  }}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Pass PDF</label>
                                <div v-if="pdfUrl" class="col-sm-6">
                                    <a :href="pdfUrl" target="blank">{{ pass.park_pass_pdf }}</a>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Email Address</label>
                                <div class="col-sm-8">
                                    <span class="form-text"><a target="blank" :href="'mailto:' + pass.email">{{ pass.email  }}</a></span>
                                </div>
                            </div>
                            <div v-if="formattedMobile" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Mobile Number</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ formattedMobile }}</span>
                                </div>
                            </div>
                            <div v-if="postcode" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Postcode</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.postcode }}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Duration</label>
                                <div class="col-sm-8">
                                    <span class="form-text">14 Days</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="startDate" class="col-sm-4 col-form-label">Start Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="startDate" type="date" v-model="pass.datetime_start">
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">End Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="date" v-model="pass.datetime_expiry">
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">Vehicle Registration <span v-if="pass.vehicle_registration_2">1</span></label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="text" v-model="pass.vehicle_registration_1">
                                    </span>
                                </div>
                            </div>
                            <div v-if="!isHolidayPass" class="row mb-1">
                                <label for="endDate" class="col-sm-4 col-form-label">Vehicle Registration 2</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" name="endDate" type="text" v-model="pass.vehicle_registration_2">
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="preventFurtherVehicleUpdates" class="col-sm-4 col-form-label">Prevent Further Vehicle Updates</label>
                                <div class="col-sm-8">
                                    <div class="form-switch">
                                        <input class="form-check-input org-form-switch-primary" type="checkbox" id="preventFurtherVehicleUpdates" v-model="pass.prevent_further_vehicle_updates">
                                    </div>
                                </div>
                            </div>
                            </form>
                        </SectionToggle>
                        <SectionToggle v-if="showDiscountsPanel" label="Concession, Voucher and Discount">
                            <form>
                            <div v-if="pass.concession_type" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Type</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.concession_type }}</span>
                                </div>
                            </div>
                            <div v-if="pass.concession_discount_percentage" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Discount</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pass.concession_discount_percentage }}% Off</span>
                                </div>
                            </div>
                            <div v-else class="row mb-1">
                                <label class="col-sm-4 col-form-label">Concession Used for Purchase</label>
                                <div class="col-sm-8">
                                    <span class="form-text">No</span>
                                </div>
                            </div>
                            <div v-if="pass.voucher_number" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Voucher Used for Payment</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ voucher_number }}</span>
                                </div>
                            </div>
                            <div v-if="pass.voucher_transaction_amount" class="row mb-1">
                                <label class="col-sm-4 col-form-label">Voucher Amount</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ voucher_transaction_amount }}</span>
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
                                <label for="startDate" class="col-sm-4 col-form-label">Sold Via</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        {{ pass.sold_via_name }}
                                    </span>
                                </div>
                            </div>
                            </form>
                        </SectionToggle>
                    </div>
                </div>

            </div>
        </div>

    </div>
    <footer class="fixed-bottom mt-auto py-3 bg-light">
        <div class="container d-flex justify-content-end">
            <template v-if="!loading">
                <button @click="returnToPassesDash" class="btn licensing-btn-primary me-2">Cancel</button>
                <button @click="validateForm(true)" class="btn licensing-btn-primary me-2">Save and Exit</button>
                <button @click="validateForm(false)" class="btn licensing-btn-primary">Save and Continue Editing</button>
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
        <loader isLoading="true" />
    </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import Loader from '@/utils/vue/Loader.vue'

import Swal from 'sweetalert2'


import SectionToggle from '@/components/forms/SectionToggle.vue'
import CommsLog from '@/components/common/CommsLog.vue'
import StatusPanel from '@/components/common/StatusPanel.vue'

export default {
    name: "PassForm",
    props: {

    },
    data() {
        return {
            passId: null,
            pass: null,
            logsUrl: null,
            pdfUrl: null,
            loading: false,
        }
    },
    computed: {
        showDiscountsPanel: function() {
            return this.pass.concession_type || this.pass.voucher_number || this.pass.discount_code_used;
        },
        isHolidayPass: function () {
            return constants.HOLIDAY_PASS_NAME==this.pass.pass_type_name ? true : false
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
        }
    },
    components: {
        SectionToggle,
        CommsLog,
        Loader,
        StatusPanel,
    },
    methods: {
        returnToPassesDash: function() {
            this.$router.push({name: 'internal-dash'});
        },
        fetchPass: function (passId) {
            let vm = this;
            fetch(apiEndpoints.internalPass(passId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.pass = data
                vm.pass.datetime_start = helpers.getDateFromDatetime(vm.pass.datetime_start);
                vm.pass.datetime_expiry = helpers.getDateFromDatetime(vm.pass.datetime_expiry);
                console.log(vm.pass);
                console.log('date_start = ' + vm.pass.date_start);

                vm.logsUrl = apiEndpoints.userActionLog(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_PASS,
                    vm.pass.id
                )
                vm.pdfUrl = apiEndpoints.internalParkPassPdf(vm.pass.id)
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        submitForm: function (exitAfter) {
            let vm = this;
            vm.loading = true;
            vm.pass.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.pass);
            vm.pass.datetime_start  = new Date(vm.pass.datetime_start).toLocaleString();
            vm.pass.datetime_expiry  = new Date(vm.pass.datetime_expiry).toLocaleString();
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pass)
            };
            fetch(apiEndpoints.updatePass(vm.pass.id), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }

                    console.log(data);

                    Swal.fire({
                        title: 'Success',
                        text: 'Park Pass updated successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    if(exitAfter) {
                        vm.$router.push({name: 'internal-dash'});
                    }
                    var forms = document.querySelectorAll('.needs-validation');
                    Array.prototype.slice.call(forms).forEach(function (form) {
                        form.classList.remove('was-validated');
                    });
                    vm.pass.why = '';
                    $('#reasonFiles').val('');
                    vm.loading = false;
                })
                .catch(error => {
                    this.systemErrorMessage = "ERROR: Please try again in an hour.";
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
