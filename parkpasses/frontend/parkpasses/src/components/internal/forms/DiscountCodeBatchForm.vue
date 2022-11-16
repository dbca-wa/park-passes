<template lang="html">
    <div v-if="discountCodeBatch" class="container" id="discountCodeBatchForm">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>{{ 'Discount Code Batch - ' + discountCodeBatch.discount_code_batch_number }}</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-3">
                        <CommsLog
                            :commsUrl="listCommsUrl"
                            :logsUrl="listUserActionsLogUrl"
                            :commAddUrl="createCommUrl"
                            :appLabel="appLabel"
                            :model="model"
                            :customerId="null"
                            :objectId="discountCodeBatch.id" />
                        <StatusPanel :status="discountCodeBatch.status" :badge="true" :badgeClass="badgeClass" class="pt-3" />
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
                        <SectionToggle :label="'Discount Code Batch - ' + discountCodeBatch.discount_code_batch_number">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                        <div class="container">
                            <div v-if="startDateHasPassed" class="row">
                                <div class="col">
                                    <BootstrapAlert type="warning" icon="exclamation-triangle-fill">
                                        This discount code batch is already active so only the expiry date can be modified.
                                    </BootstrapAlert>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <label for="datetimeStart" class="col-form-label">Valid From</label>
                                    <input type="datetime-local" class="form-control"
                                        :class="errors.datetime_start ? 'is-invalid' : ''" id="datetimeStart"
                                        name="datetimeStart" v-model="discountCodeBatch.datetime_start" required="required"
                                        :min="startDate()" aria-describedby="validationServerDateStartFeedback" :disabled="startDateHasPassed">
                                    <div v-if="errors.datetime_start"  id="validationServerDateStartFeedback" class="invalid-feedback">
                                        <p v-for="(error, index) in errors.datetime_start" :key="index">{{ error }}</p>
                                    </div>
                                    <div v-else id="validationServerDateStartFeedback" class="invalid-feedback">
                                        Please enter a date the code(s) will be valid from.
                                    </div>
                                </div>
                                <div class="col">
                                    <label for="datetimeExpiry" class="col-form-label">Valid To</label>
                                    <input type="datetime-local" class="form-control"
                                        :class="errors.datetime_expiry ? 'is-invalid' : ''" id="datetimeExpiry"
                                        name="datetimeExpiry" v-model="discountCodeBatch.datetime_expiry" required="required"
                                        :min="minEndDate" aria-describedby="validationServerDateExpiryFeedback">
                                    <div v-if="errors.datetime_expiry"  id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                        <p v-for="(error, index) in errors.datetime_expiry" :key="index">{{ error }}</p>
                                    </div>
                                    <div v-else id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                        Please enter a date the code(s) will be valid to.
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="discountType" class="col-form-label">Discount:</label>
                                    <div>
                                        <div class="form-check form-check-inline">
                                            <input @change="discountTypeChanged" type="radio" class="form-check-input"
                                                id="discountTypePercentage" name="discountType" v-model="discountCodeBatch.discount_type" value="percentage"
                                                aria-describedby="validationServerDiscountTypeFeedback" required :disabled="fieldDisabled" />
                                            <label for="discountTypePercentage" class="col-form-label">Percentage</label>
                                        </div>
                                        <div class="form-check form-check-inline">
                                            <input @change="discountTypeChanged" type="radio" class="form-check-input"
                                                id="discountTypeAmount" name="discountType" v-model="discountCodeBatch.discount_type" value="amount"
                                                aria-describedby="validationServerDiscountTypeFeedback" required :disabled="fieldDisabled" />
                                            <label for="discountTypeAmount" class="col-form-label">Amount</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-8">
                                    <label for="discountPercentage" class="col-form-label">&nbsp;</label>
                                    <div>
                                        <input v-if="'percentage'==discountCodeBatch.discount_type" type="number" class="form-control" :class="errors.discount_percentage ? 'is-invalid' : ''" id="discountPercentage"
                                            name="discountPercentage" placeholder="Percentage" v-model="discountCodeBatch.discount_percentage"
                                            aria-describedby="validationServerNameFeedback" min="1" max="100" required :disabled="fieldDisabled" />
                                        <input v-if="'amount'==discountCodeBatch.discount_type" type="number" class="form-control" :class="errors.discount_amount ? 'is-invalid' : ''" id="discountAmount"
                                            name="discountAmount" placeholder="Amount" v-model="discountCodeBatch.discount_amount"
                                            aria-describedby="validationServerNameFeedback" min="1" required :disabled="fieldDisabled" />
                                        <div v-if="errors.discount_amount" id="validationServerDiscountTypeFeedback" class="invalid-feedback">
                                            <p v-for="(error, index) in errors.discount_amount" :key="index">{{ error }}</p>
                                        </div>
                                        <div v-else id="validationDiscountTypeFeedback" class="invalid-feedback">
                                            Please enter a discount for the pricing window.
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div v-if="discountCodeBatch.discount_codes" class="col">
                                    <label for="" class="col-form-label">Discount Codes:</label>
                                    <div>
                                        <template v-for="discount_code in discountCodeBatch.discount_codes">
                                            <span class="badge org-badge-primary">{{ discount_code.code }}</span>&nbsp;
                                        </template>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <label for="uses" class="col-form-label">Number of times each code can be used:</label>
                                    <input type="number" class="form-control" :class="errors.name ? 'is-invalid' : ''" id="uses"
                                        name="uses" placeholder="Unlimited" v-model="discountCodeBatch.times_each_code_can_be_used"
                                        aria-describedby="validationServerNameFeedback" min="1" :disabled="startDateHasPassed" />
                                    <div v-if="errors.times_each_code_can_be_used" id="validationServerNameFeedback" class="invalid-feedback">
                                        <p v-for="(error, index) in errors.times_each_code_can_be_used" :key="index">{{ error }}</p>
                                    </div>
                                </div>
                                <div class="col">
                                    <label for="codesToGenerate" class="col-form-label">Number of codes to be created:</label>
                                    <input type="number" class="form-control" :class="errors.codes_to_generate ? 'is-invalid' : ''" id="codesToGenerate"
                                        name="codesToGenerate" v-model="discountCodeBatch.codes_to_generate"
                                        aria-describedby="validationServerCodesToGenerateFeedback" min="1" required :disabled="startDateHasPassed" />
                                    <div v-if="errors.codes_to_generate" id="validationServerCodesToGenerateFeedback" class="invalid-feedback">
                                        <p v-for="(error, index) in errors.codes_to_generate" :key="index">{{ error }}</p>
                                    </div>
                                    <div v-else id="validationServerCodesToGenerateFeedback" class="invalid-feedback">
                                        Please enter how many discount codes you would like to generate.
                                    </div>
                                </div>
                            </div>
                            <div v-if="passTypes" class="mb-3">
                                <label for="validPassTypes" class="col-form-label">Valid for pass type(s):</label>

                                <select class="form-select" id="validPassTypes" name="validPassTypes" ref="validPassTypes" placeholder="All Pass Types" v-model="discountCodeBatch.valid_pass_types"
                                    aria-describedby="validationServervalidPassTypesFeedback" multiple :disabled="startDateHasPassed">
                                    <option v-for="passType in passTypes" :key="passType.id" :value="passType.id">{{ passType.display_name }}</option>
                                </select>

                                <div v-if="errors.valid_pass_types" id="validationServervalidPassTypesFeedback" class="invalid-feedback">
                                    <p v-for="(error, index) in errors.valid_pass_types" :key="index">{{ error }}</p>
                                </div>
                                <div v-else id="validationServervalidPassTypesFeedback" class="invalid-feedback">
                                    Please select one or more valid pass types.
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="validUsers" class="col-form-label">Valid for user(s):</label>

                                <select class="form-select" id="validUsers" name="validUsers" ref="validUsers" placeholder="All Users" v-model="discountCodeBatch.valid_users"
                                    aria-describedby="validationServerValidUsersFeedback" multiple :disabled="startDateHasPassed">
                                </select>

                                <div v-if="errors.name" id="validationServervalidUsersFeedback" class="invalid-feedback">
                                    <p v-for="(error, index) in errors.valid_users" :key="index">{{ error }}</p>
                                </div>
                                <div v-else id="validationvalidUsersFeedback" class="invalid-feedback">
                                    Please select one or more valid users.
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="reason" class="col-form-label">Reason for <span v-if="discountCodeBatch.id">Updating {{ discountCodeBatch.discount_code_batch_number }}</span><span v-else>Creating Discount Code Batch</span>:</label>
                                <textarea class="form-control" :class="errors.reason ? 'is-invalid' : ''" id="reason" name="reason" v-model="discountCodeBatch.why" aria-describedby="validationServerReasonFeedback" required></textarea>
                                <div v-if="errors.reason" id="validationServerReasonFeedback" class="invalid-feedback">
                                    <p v-for="(error, index) in errors.reason" :key="index">{{ error }}</p>
                                </div>
                                <div v-else id="validationReasonFeedback" class="invalid-feedback">
                                    Please enter the reason this discount code batch is being
                                    <span v-if="discountCodeBatch.id">updated</span>
                                    <span v-else>created</span>.
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="reasonFiles" class="col-form-label">Files</label>
                                <input class="form-control" type="file" id="reasonFiles" name="reasonFiles" multiple>
                            </div>
                        </div>

                            </form>
                        </SectionToggle>
                    </div>
                </div>

            </div>
        </div>

        <div v-if="successMessage" class="row mx-1">
            <div id="successMessageAlert" class="col alert alert-success show fade" role="alert">
                {{ successMessage }}
            </div>
        </div>

    </div>
    <footer class="fixed-bottom mt-auto py-3 bg-light">
        <div class="container d-flex justify-content-end">
            <button @click="returnToDiscountCodeBatchDash" class="btn licensing-btn-primary me-2">Exit</button>
            <button @click="validateForm(true)" class="btn licensing-btn-primary me-2">Save and Exit</button>
            <button @click="validateForm(false)" class="btn licensing-btn-primary">Save and Continue Editing</button>
        </div>
    </footer>
    <div v-if="!discountCodeBatch">
        <BootstrapSpinner :isLoading="true" />
    </div>
</template>

<script>
import { apiEndpoints, constants, helpers, utils } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

import SectionToggle from '@/components/forms/SectionToggle.vue'
import CommsLog from '@/components/common/CommsLog.vue'
import StatusPanel from '@/components/common/StatusPanel.vue'

import DOMPurify from 'dompurify'

import Swal from 'sweetalert2'

export default {
    name: "DiscountCodeBatchForm",
    props: {

    },
    data() {
        return {
            discountCodeBatchId: null,
            discountCodeBatch: null,
            passTypes: null,
            listUserActionsLogUrl: null,
            listCommsUrl: null,
            createCommUrl: apiEndpoints.createCommunicationsLogEntry,
            appLabel: constants.PARKPASSES_APP_LABEL,
            model: constants.PARKPASSES_MODELS_DISCOUNT_CODE_BATCH,
            errors: {},
            successMessage: null,
        }
    },
    computed: {
        minEndDate: function () {
            let startDate = new Date(this.discountCodeBatch.datetime_start);
            let endDate = startDate.setDate(startDate.getDate() + 1);
            console.log('endDate = ' + endDate);
            return moment(endDate).format(helpers.getDatetimeLocalFormat());
        },
        startDateHasPassed: function () {
            let now = new Date();
            let startDate = new Date(this.discountCodeBatch.datetime_start);
            return startDate <= now;
        },
        fieldDisabled: function () {
            return this.startDateHasPassed || !this.discountCodeBatch.user_can_create_percentage_discounts;
        },
        badgeClass: function () {
            return helpers.getStatusBadgeClass(this.discountCodeBatch.status);
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
        returnToDiscountCodeBatchDash: function() {
            this.$router.push({name: 'internal-discount-codes'});
        },
        startDate: function () {
            const today = new Date();
            return today.toISOString();
        },
        discountTypeChanged: function (event) {
            if('percentage'==event.target.value) {
                this.discountCodeBatch.discount_amount = '';
            } else {
                this.discountCodeBatch.discount_percentage = '';
            }
        },
        initialiseValidUsersSelect2: function() {
            let vm = this;
            $('#validUsers').select2({
                ajax: {
                    url: apiEndpoints.select2Customers,
                    dataType: 'json'
                },
                "theme": "bootstrap-5",
                multiple: true,
                placeholder: "All Users",
            }).on('change', function() {
                vm.discountCodeBatch.valid_users = $(this).val();
            });
        },
        initialiseValidPassTypesSelect2: function() {
            let vm = this;
            $('#validPassTypes').select2({
                "theme": "bootstrap-5",
                multiple: true,
                placeholder: "All Pass Types",
            }).on('change', function() {
                console.log($(this).val());
                vm.discountCodeBatch.valid_pass_types = $(this).val();
            });
        },
        fetchPassTypes: function () {
            let vm = this;
            fetch(apiEndpoints.passTypesInternal)
            .then(async (response) => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                vm.passTypes = data.results;
            })
            .catch((error) => {
                this.errorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        fetchDiscountCodeBatch: function (discountCodeBatchId) {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.discountCodeBatch(discountCodeBatchId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.discountCodeBatch = Object.assign({}, data);
                if(vm.discountCodeBatch.discount_percentage) {
                    vm.discountCodeBatch.discount_type = 'percentage';
                } else {
                    vm.discountCodeBatch.discount_type = 'amount';
                }

                vm.discountCodeBatch.valid_pass_types =
                vm.discountCodeBatch.valid_pass_types.map(({pass_type_id}) => pass_type_id);

                vm.discountCodeBatch.datetime_start = moment(vm.discountCodeBatch.datetime_start).format(helpers.getDatetimeLocalFormat());
                vm.discountCodeBatch.datetime_expiry = new Date(vm.discountCodeBatch.datetime_expiry).toISOString().slice(0, -1) ;

                console.log('vm.discountCodeBatch.datetime_start = ' + vm.discountCodeBatch.datetime_start);
                console.log('vm.discountCodeBatch.datetime_expiry = ' + vm.discountCodeBatch.datetime_expiry);

                vm.listUserActionsLogUrl = apiEndpoints.listUserActionsLog(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_DISCOUNT_CODE_BATCH,
                    vm.discountCodeBatch.id
                )
                vm.listCommsUrl = apiEndpoints.listCommunicationsLogEntries(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_DISCOUNT_CODE_BATCH,
                    vm.discountCodeBatch.id
                )

                if(vm.valid_pass_types) {
                    var validPassTypes = vm.valid_pass_types.split(',');
                    $(".select2").select2().val(validPassTypes).trigger('change');
                }
                vm.loading = false;
            })
            .catch(error => {
                vm.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            }).finally(() =>{
                vm.initialiseValidUsersSelect2();
                vm.discountCodeBatch.valid_users.forEach(function(validUser){
                    console.log(validUser)
                    var option = new Option(
                        DOMPurify.sanitize(validUser.display_name),
                        DOMPurify.sanitize(validUser.user),
                        true,
                        true
                    );
                    $('#validUsers').append(option);
                    $('#validUsers').trigger('change');
                });
                vm.initialiseValidPassTypesSelect2();
            });
        },
        submitForm: function (exitAfter) {
            let vm = this;
            vm.discountCodeBatch.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.discountCodeBatch);
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.discountCodeBatch)
            };
            fetch(apiEndpoints.updateDiscountCodeBatch(vm.discountCodeBatch.id), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }

                    console.log(data);
                    let files = $('#reasonFiles')[0].files;
                    utils.uploadOrgModelDocuments(data.user_action.user_action_content_type_id, data.user_action.id, files);
                    Swal.fire({
                        title: 'Success',
                        text: 'Discount Code Batch updated successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    if(exitAfter) {
                        vm.$router.push({name: 'internal-discount-codes'});
                    }
                    var forms = document.querySelectorAll('.needs-validation');
                    Array.prototype.slice.call(forms).forEach(function (form) {
                        form.classList.remove('was-validated');
                    });
                    vm.discountCodeBatch.why = '';
                    $('#reasonFiles').val('');
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
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
        this.fetchPassTypes();
        this.fetchDiscountCodeBatch(this.$route.params['discountCodeBatchId'] );
    },
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
