<template>
    <div class="modal fade" id="pricingWindowModal" tabindex="-1" aria-labelledby="pricingWindowModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="pricingWindowModalLabel">Create New Discount Codes</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="datetimeStart" class="col-form-label">Valid From</label>
                            <input type="date" class="form-control"
                                :class="errors.date_start ? 'is-invalid' : ''" id="datetimeStart"
                                name="datetimeStart" v-model="discount_code_batch.datetime_start" required="required"
                                :min="startDate()" aria-describedby="validationServerDateStartFeedback">
                            <div v-if="errors.date_start"  id="validationServerDateStartFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.date_start" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerDateStartFeedback" class="invalid-feedback">
                                Please enter a date the code(s) will be valid from.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="datetimeExpiry" class="col-form-label">Valid To</label>
                            <input type="date" class="form-control"
                                :class="errors.datetime_expiry ? 'is-invalid' : ''" id="datetimeExpiry"
                                name="datetimeExpiry" v-model="discount_code_batch.datetime_expiry" required="required"
                                :min="minEndDate" aria-describedby="validationServerDateExpiryFeedback">
                            <div v-if="errors.datetime_expiry"  id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.datetime_expiry" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerDateExpiryFeedback" class="invalid-feedback">
                                Please enter a date the code(s) will be valid to.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="discountType" class="col-form-label">Discount:</label>
                            <div>
                            <div class="form-check form-check-inline">
                                <input type="radio" class="form-check-input" :class="errors.discount_percentage ? 'is-invalid' : ''"
                                    id="discountTypePercentage" name="discountType" v-model="discount_code_batch.discount_type" value="percentage"
                                    aria-describedby="validationServerDiscountTypeFeedback" required />
                                <label for="discountTypePercentage" class="col-form-label">Percentage</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input type="radio" class="form-check-input" :class="errors.discount_percentage ? 'is-invalid' : ''"
                                    id="discountTypeAmount" name="discountType" v-model="discount_code_batch.discount_type" value="amount"
                                    aria-describedby="validationServerDiscountTypeFeedback" required />
                                <label for="discountTypeAmount" class="col-form-label">Amount</label>
                            </div>
                            <input v-if="'percentage'==discount_code_batch.discount_type" type="number" class="form-control" :class="errors.discount_percentage ? 'is-invalid' : ''" id="discountPercentage"
                                name="discountPercentage" placeholder="Percentage" v-model="discount_code_batch.discount_percentage"
                                aria-describedby="validationServerNameFeedback" min="1" max="100" required />
                            <input v-if="'amount'==discount_code_batch.discount_type" type="number" class="form-control" :class="errors.discount_amount ? 'is-invalid' : ''" id="discountAmount"
                                name="discountAmount" placeholder="Amount" v-model="discount_code_batch.discount_amount"
                                aria-describedby="validationServerNameFeedback" min="1" required />
                            <div v-if="errors.discount_amount" id="validationServerDiscountTypeFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.discount_amount" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerNameFeedback" class="invalid-feedback">
                                Please enter a discount for the pricing window.
                            </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="uses" class="col-form-label">Number of times each code can be used:</label>
                            <input type="number" class="form-control" :class="errors.name ? 'is-invalid' : ''" id="uses"
                                name="uses" placeholder="&infin;" v-model="discount_code_batch.times_each_code_can_be_used"
                                aria-describedby="validationServerNameFeedback" min="1" required />
                            <div v-if="errors.times_each_code_can_be_used" id="validationServerNameFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.times_each_code_can_be_used" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerNameFeedback" class="invalid-feedback">
                                Please enter a name for the pricing window.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="codesToGenerate" class="col-form-label">Number of codes to be created:</label>
                            <input type="number" class="form-control" :class="errors.codes_to_generate ? 'is-invalid' : ''" id="codesToGenerate"
                                name="codesToGenerate" v-model="discount_code_batch.codes_to_generate"
                                aria-describedby="validationServerCodesToGenerateFeedback" min="1" required />
                            <div v-if="errors.codes_to_generate" id="validationServerCodesToGenerateFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.codes_to_generate" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerCodesToGenerateFeedback" class="invalid-feedback">
                                Please enter how many discount codes you would like to generate.
                            </div>
                        </div>
                        <div v-if="passTypes" class="mb-3">
                            <label for="validPassTypes" class="col-form-label">Valid for pass type(s):</label>
                            <Select2 v-model="discount_code_batch.valid_pass_types" :options="select2TestData" />
                            <!--
                            <select class="form-select" id="validPassTypes" name="validPassTypes" ref="validPassTypes" placeholder="&infin;" v-model="discount_code_batch.valid_pass_types"
                                aria-describedby="validationServervalidPassTypesFeedback" multiple>
                                <option selected value="">&infin;</option>
                                <option v-for="passType in passTypes">{{ passType.display_name }}</option>
                            </select>
                            -->
                            <div v-if="errors.valid_pass_types" id="validationServervalidPassTypesFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.valid_pass_types" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServervalidPassTypesFeedback" class="invalid-feedback">
                                Please select one or more valid pass types.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="name" class="col-form-label">Valid for email(s):</label>
                            <select class="form-select" id="basic-usage" placeholder="&infin;">
                                <option selected value="">&infin;</option>
                            </select>
                            <div v-if="errors.name" id="validationServerNameFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.name" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerNameFeedback" class="invalid-feedback">
                                Please select one or more valid users.
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="reason" class="col-form-label">Reason:</label>
                            <textarea class="form-control" :class="errors.reason ? 'is-invalid' : ''" id="reason" name="reason" v-model="discount_code_batch.reason" aria-describedby="validationServerReasonFeedback" required></textarea>
                            <div v-if="errors.reason" id="validationServerReasonFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.reason" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerReasonFeedback" class="invalid-feedback">
                                Please enter the reason this discount code batch is being created.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="reasonFiles" class="col-form-label">Files</label>
                            <input class="form-control" type="file" id="reasonFiles" name="reasonFiles">
                            <div v-if="errors.date_start"  id="validationServerReasonFilesFeedback" class="invalid-feedback">
                                <p v-for="(error, index) in errors.date_start" :key="index">{{ error }}</p>
                            </div>
                            <div v-else id="validationServerReasonFilesFeedback" class="invalid-feedback">
                                Please enter a valid start date.
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn licensing-btn-primary">Submit</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'
import Select2 from 'vue3-select2-component'

export default {
    name: 'DiscountCodeBatchFormModal',
    emits: ['saveSuccess'],
    props: {

    },
    data() {
        return {
            discount_code_batch: this.getDiscountCodeBatchInitialState(),
            passTypes: null,
            select2TestData: ['opt1', 'opt2', 'opt3'],
            errors: {},
        }
    },
    components: {
        Select2
    },
    computed: {
        minEndDate: function () {
            let endDate = new Date(this.discount_code_batch.date_start);
            endDate.setDate(endDate.getDate() + 1);
            return endDate;
        }
    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
        fetchDefaultOptionsForPassType: function () {

        },
        getDiscountCodeBatchInitialState() {
            return {
                pass_type: 0,
                name: '',
                discount_type: 'percentage',
                valid_pass_types: '',
                codes_to_generate: 1,
                datetime_start: this.startDate(),
                datetime_expiry: this.minEndDate,
            }
        },
        fetchPassTypes: function () {
            let vm = this;
            fetch(api_endpoints.passTypes)
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
            this.errorMessage = "ERROR: Please try again in an hour.";
            console.error("There was an error!", error);
            })
            .finally(() => {
                $(vm.$refs.validPassTypes).select2({
                    "theme": "bootstrap-5",
                    allowClear: true,
                    multiple: true,
                    minimumResultsForSearch: -1,
                })
            });
        },
        submitForm: function () {
            let vm = this;
            vm.discount_code_batch.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.discount_code_batch)
            };
            fetch(api_endpoints.savePricingWindow, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    console.log('data = ' + JSON.stringify(data));
                    this.$emit("saveSuccess", {
                            message: 'Pricing Window created successfully.',
                            pricingWindow: data,
                        }
                    );
                    $('#successMessageAlert').show();
                    vm.discount_code_batch = vm.getPricingWindowInitialState();
                    var PricingWindowFormModalModal = bootstrap.Modal.getInstance(document.getElementById('pricingWindowModal'));
                    PricingWindowFormModalModal.hide();
                })
                .catch(error => {
                    this.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                }).finally(() =>{

                });
            return false;
        },
        validateForm: function () {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation');
            Array.prototype.slice.call(forms)
                .forEach(function (form) {
                    if (form.checkValidity()) {
                        vm.submitForm();
                    } else {
                        form.classList.add('was-validated');
                        $(".invalid-feedback:visible:first").siblings('input').focus();
                    }
                });
            return false;
        }
    },
    created: function () {
        this.fetchPassTypes();
    },
}
</script>
