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
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Exit</button>
                        <button type="submit" class="btn licensing-btn-primary">Submit Cancellation</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, helpers, utils } from '@/utils/hooks'
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
            cancellation: {}
        }
    },
    computed: {

    },
    methods: {
        submitForm: function () {
            let vm = this;
            vm.cancellation.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            vm.cancellation.park_pass = vm.pass.id
            alert(JSON.stringify(vm.cancellation));
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

                    vm.$emit('cancelSuccess')

                    Swal.fire({
                        title: 'Success',
                        text: 'Park Pass cancelled successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    });

                    var passCancellationFormModalModal = bootstrap.Modal.getInstance(document.getElementById('passCancellationModal'));
                    passCancellationFormModalModal.hide();
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
