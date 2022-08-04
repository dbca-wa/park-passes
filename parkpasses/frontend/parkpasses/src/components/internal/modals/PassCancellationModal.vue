<template>
    <div class="modal fade" id="passCancellationModal" tabindex="-1" aria-labelledby="passCancellationModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div v-if="pass" class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="passCancellationModalLabel">Cancel Pass: {{pass.name}}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Cancellation Reason:</label>
                            <textarea id="cancellationReason" class="form-control" required></textarea>
                            <div id="validationServerPassTypeFeedback" class="invalid-feedback">
                                Please enter a cancellation reason.
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="pass-type" class="col-form-label">Files:</label>
                            <div><a href="#">Attach File</a></div>
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

        }
    },
    computed: {

    },
    methods: {
        submitForm: function () {
            let vm = this;
            vm.pricing_window.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pricing_window)
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
                    vm.pricing_window = vm.getPricingWindowInitialState();
                    var PricingWindowFormModalModal = bootstrap.Modal.getInstance(document.getElementById('passCancellationModal'));
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

    }
}
</script>
