<template>
    <div class="modal fade" id="passCancellationModal" tabindex="-1" aria-labelledby="passCancellationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div v-if="pass" class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="passCancellationModalLabel">Cancel Pass: {{pass.name}}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Sold Via: </label>
                            <span class="badge org-badge-primary ms-2"> {{ pass.soldViaName }} </span>
                        </div>
                        <div class="mb-3">
                            <span class="badge bg-warning ms-2 fs-6" v-if="soldViaDBCA()">When you submit this cancellation you will be automatically taken to the BPoint Refund Screen.</span>
                            <span class="badge bg-warning ms-2 fs-6" v-else>You must refund this pass manually outside the system before or after cancellation.</span>
                        </div>

                        <div v-if="soldViaDBCA()" class="mb-3">
                            <label for="pass-type" class="col-form-label">The Pro-Rata Refund Amount Will Be: </label>
                            <span class="badge bg-success ms-2"> {{ pass.proRataRefundAmountDisplay }} </span>
                        </div>
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Cancellation Reason:</label>
                            <textarea id="cancellationReason" class="form-control" v-model="cancellation.cancellation_reason" required></textarea>
                            <div id="validationServerPassTypeFeedback" class="invalid-feedback">
                                Please enter a cancellation reason.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Files:</label>
                            <input class="form-control" type="file" id="reasonFiles" name="reasonFiles" multiple>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button v-if="!loading" type="button" class="btn btn-secondary" data-bs-dismiss="modal">Exit</button>
                        <button v-if="!loading" type="submit" class="btn licensing-btn-primary">Submit Cancellation</button>
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
    name: 'PassCancellationModal',
    emits: ['cancelSuccess'],
    props: {
        pass: {
            type: Object,
            default: null,
        },
    },
    data() {
        return {
            cancellation: {},
            loading: false,
        }
    },
    components: {
        BootstrapButtonSpinner,
    },
    computed: {
    },
    methods: {
        soldViaDBCA: function () {
            return constants.DEFAULT_SOLD_VIA==this.pass.soldViaName;
        },
        submitForm: function () {
            let vm = this;
            vm.loading = true;
            vm.cancellation.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            vm.cancellation.park_pass = vm.pass.id
            //alert(JSON.stringify(vm.cancellation));
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.cancellation)
            };
            fetch(apiEndpoints.cancelPass, requestOptions)
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

                    // Pass was sold via DBCA website so a BPoint refund can occur
                    if(constants.DEFAULT_SOLD_VIA==vm.pass.soldViaName){
                        var form = document.createElement("form");
                        form.setAttribute("method", "POST");
                        form.setAttribute("action", apiEndpoints.proRataRefundPassInternal(vm.cancellation.park_pass));
                        var hiddenField = document.createElement("input");
                        hiddenField.setAttribute("type", "hidden");
                        hiddenField.setAttribute("name", "csrfmiddlewaretoken");
                        hiddenField.setAttribute("value", vm.cancellation.csrfmiddlewaretoken);
                        form.appendChild(hiddenField);
                        document.body.appendChild(form);
                        form.submit();
                    }
                    // Pass was sold by a retailer so refund will be done manually outside system
                    else {
                        vm.$emit('cancelSuccess')

                        Swal.fire({
                            title: 'Success',
                            text: 'Park Pass cancelled successfully. Please refund manually outside of system.',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });

                        var passCancellationFormModalModal = bootstrap.Modal.getInstance(document.getElementById('passCancellationModal'));
                        passCancellationFormModalModal.hide();
                        vm.loading = false;
                    }
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
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

    }
}
</script>
