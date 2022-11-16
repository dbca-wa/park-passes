<template>
    <div class="modal fade" id="discountCodeBatchInvalidationModal" tabindex="-1" aria-labelledby="discountCodeBatchInvalidationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div v-if="discountCodeBatch" class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="discountCodeBatchInvalidationModalLabel">Invalidate Discount Code Batch: {{discountCodeBatch.discount_code_batch_number}}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="discountCodeBatch-type" class="col-form-label">Invalidation Reason:</label>
                            <textarea id="invalidationReason" class="form-control" v-model="invalidation.invalidation_reason" required></textarea>
                            <div id="validationServerDiscountCodeBatchTypeFeedback" class="invalid-feedback">
                                Please enter the reason you are invalidating this discount code batch.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="discountCodeBatch-type" class="col-form-label">Files:</label>
                            <input class="form-control" type="file" id="invalidationReasonFiles" name="invalidationReasonFiles" multiple>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button v-if="!loading" type="button" class="btn btn-secondary" data-bs-dismiss="modal">Exit</button>
                        <button v-if="!loading" type="submit" class="btn licensing-btn-primary">Submit Invalidation</button>
                        <BootstrapButtonSpinner v-else class="btn licensing-btn-primary px-5" />
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, constants, helpers, utils } from '@/utils/hooks'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'

import Swal from 'sweetalert2'

export default {
    name: 'DiscountCodeBatchInvalidationModal',
    emits: ['invalidateSuccess'],
    props: {
        discountCodeBatch: {
            type: Object,
            default: null,
        },
    },
    data() {
        return {
            invalidation: {},
            loading: false,
        }
    },
    components: {
        BootstrapButtonSpinner,
    },
    computed: {
    },
    methods: {
        submitForm: function () {
            let vm = this;
            vm.loading = true;
            vm.invalidation.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            vm.invalidation.discount_code_batch_id = vm.discountCodeBatch.id
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.invalidation)
            };
            fetch(apiEndpoints.internalInvalidateDiscountCodeBatch(vm.discountCodeBatch.id), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }

                    console.log(data);
                    let files = $('#invalidationReasonFiles')[0].files;
                    utils.uploadOrgModelDocuments(data.user_action.user_action_content_type_id, data.user_action.id, files);

                    Swal.fire({
                        title: 'Success',
                        text: 'Discount Code Batch invalidated successfully.',
                        icon: 'success',
                        showConfirmButton: false,
                        timer: 1500
                    });

                    vm.$emit('invalidateSuccess')

                    var discountCodeBatchInvalidationFormModalModal = bootstrap.Modal.getInstance(document.getElementById('discountCodeBatchInvalidationModal'));
                    discountCodeBatchInvalidationFormModalModal.hide();
                    vm.loading = false;
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
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

    }
}
</script>
