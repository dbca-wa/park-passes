<template>
    <div class="modal fade" id="discountCodeBatchModal" aria-labelledby="discountCodeBatchModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="discountCodeBatchModalLabel">Create New Discount Codes</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="container">
                            <div class="row">
                                <div class="col">
                                    <label for="datetimeStart" class="col-form-label">Valid From</label>
                                    <input type="datetime-local" class="form-control"
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
                                <div class="col">
                                    <label for="datetimeExpiry" class="col-form-label">Valid To</label>
                                    <input type="datetime-local" class="form-control"
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
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <label for="discountType" class="col-form-label">Discount:</label>
                                    <div>
                                        <div class="form-check form-check-inline">
                                            <input @change="discountTypeChanged" type="radio" class="form-check-input" :class="errors.discount_percentage ? 'is-invalid' : ''"
                                                id="discountTypePercentage" name="discountType" v-model="discount_code_batch.discount_type" value="percentage"
                                                aria-describedby="validationServerDiscountTypeFeedback" required />
                                            <label for="discountTypePercentage" class="col-form-label">Percentage</label>
                                        </div>
                                        <div class="form-check form-check-inline">
                                            <input @change="discountTypeChanged" type="radio" class="form-check-input" :class="errors.discount_percentage ? 'is-invalid' : ''"
                                                id="discountTypeAmount" name="discountType" v-model="discount_code_batch.discount_type" value="amount"
                                                aria-describedby="validationServerDiscountTypeFeedback" required />
                                            <label for="discountTypeAmount" class="col-form-label">Amount</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-8">
                                    <label for="discountPercentage" class="col-form-label">&nbsp;</label>
                                    <div>
                                        <input v-if="'percentage'==discount_code_batch.discount_type" type="number" class="form-control" :class="errors.discount_percentage ? 'is-invalid' : ''" id="discountPercentage"
                                            name="discountPercentage" placeholder="Percentage" v-model="discount_code_batch.discount_percentage"
                                            aria-describedby="validationServerNameFeedback" min="1" max="100" required />
                                        <input v-if="'amount'==discount_code_batch.discount_type" type="number" class="form-control" :class="errors.discount_amount ? 'is-invalid' : ''" id="discountAmount"
                                            name="discountAmount" placeholder="Amount" v-model="discount_code_batch.discount_amount"
                                            aria-describedby="validationServerNameFeedback" min="1" required />
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
                                <div class="col">
                                    <label for="uses" class="col-form-label">Number of times each code can be used:</label>
                                    <input type="number" class="form-control" :class="errors.name ? 'is-invalid' : ''" id="uses"
                                        name="uses" placeholder="Unlimited" v-model="discount_code_batch.times_each_code_can_be_used"
                                        aria-describedby="validationServerNameFeedback" min="1" />
                                    <div v-if="errors.times_each_code_can_be_used" id="validationServerNameFeedback" class="invalid-feedback">
                                        <p v-for="(error, index) in errors.times_each_code_can_be_used" :key="index">{{ error }}</p>
                                    </div>
                                </div>
                                <div class="col">
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
                            </div>
                            <div v-if="passTypes" class="mb-3">
                                <label for="validPassTypes" class="col-form-label">Valid for pass type(s):</label>

                                <select class="form-select" id="validPassTypes" name="validPassTypes" ref="validPassTypes" placeholder="All Pass Types" v-model="discount_code_batch.valid_pass_types"
                                    aria-describedby="validationServervalidPassTypesFeedback" multiple>
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

                                <select class="form-select" id="validUsers" name="validUsers" ref="validUsers" placeholder="All Users" v-model="discount_code_batch.valid_users"
                                    aria-describedby="validationServerValidUsersFeedback" multiple>
                                </select>

                                <div v-if="errors.name" id="validationServervalidUsersFeedback" class="invalid-feedback">
                                    <p v-for="(error, index) in errors.valid_users" :key="index">{{ error }}</p>
                                </div>
                                <div v-else id="validationvalidUsersFeedback" class="invalid-feedback">
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
                                <input class="form-control" type="file" id="reasonFiles" name="reasonFiles" multiple>
                                <div v-if="errors.date_start"  id="validationServerReasonFilesFeedback" class="invalid-feedback">
                                    <p v-for="(error, index) in errors.date_start" :key="index">{{ error }}</p>
                                </div>
                                <div v-else id="validationServerReasonFilesFeedback" class="invalid-feedback">
                                    Please enter a valid start date.
                                </div>
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

export default {
    name: 'DiscountCodeBatchFormModal',
    emits: ['saveSuccess'],
    props: {

    },
    data() {
        return {
            discount_code_batch: this.getDiscountCodeBatchInitialState(),
            passTypes: null,
            errors: {},
        }
    },
    components: {

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
            return today.toISOString();
        },
        discountTypeChanged: function (event) {
            if('percentage'==event.target.value) {
                this.discount_code_batch.discount_amount = '';
            } else {
                this.discount_code_batch.discount_percentage = '';
            }
        },
        fetchDefaultOptionsForPassType: function () {

        },
        getDiscountCodeBatchInitialState() {
            return {
                id: null,
                pass_type: 0,
                name: '',
                discount_type: 'percentage',
                valid_pass_types: [],
                valid_users: [],
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
                vm.$nextTick(() =>{
                    var dropdownParentEl = $('#discountCodeBatchModal > .modal-dialog > .modal-content')
                    $(vm.$refs.validPassTypes).select2({
                        dropdownParent: dropdownParentEl,
                        "theme": "bootstrap-5",
                        multiple: true,
                        placeholder: "All Pass Types",
                    });
                });
            });
        },
        submitForm: function () {
            let vm = this;
            vm.discount_code_batch.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.discount_code_batch);
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.discount_code_batch)
            };
            fetch(api_endpoints.saveDiscountCodeBatch, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    console.log('data = ' + JSON.stringify(data));
                    this.$emit("saveSuccess", {
                            message: 'Discount code(s) created successfully.',
                            discountCodeBatch: data,
                        }
                    );
                    $('#successMessageAlert').show();
                    vm.discount_code_batch = vm.getDiscountCodeBatchInitialState();
                    var discountCodeBatchFormModal = bootstrap.Modal.getInstance(document.getElementById('discountCodeBatchModal'));
                    discountCodeBatchModal.hide();
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
    mounted: function () {
        let vm = this;
        var dropdownParentEl = $('#discountCodeBatchModal > .modal-dialog > .modal-content')
        $(vm.$refs.validUsers).select2({
            ajax: {
                url: api_endpoints.select2Customers,
                dataType: 'json'
            },
            dropdownParent: dropdownParentEl,
            "theme": "bootstrap-5",
            multiple: true,
            placeholder: "All Users",
        });
    }
}
</script>

<style scoped>
.select2-search__field{
    width:100%!important;
}
</style>
