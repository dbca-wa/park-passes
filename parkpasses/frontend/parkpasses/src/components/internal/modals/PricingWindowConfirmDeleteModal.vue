<template>
    <div class="modal fade" id="pricingWindowConfirmDeleteModal" tabindex="-1" aria-labelledby="pricingWindowConfirmDeleteModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="pricingWindowConfirmDeleteModalLabel">Confirm Delete of Pricing Window</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="m-3">
                        Are you sure you want to delete the following pricing window?
                    </div>
                    <table v-if="pricingWindow" class="table table-striped">
                        <tbody>
                            <tr><th>Pass Type</th><td>{{pricingWindow.pass_type_display_name}}</td></tr>
                            <tr><th>Name</th><td>{{pricingWindow.name}}</td></tr>
                            <tr><th>Date Start</th><td>{{pricingWindow.date_start}}</td></tr>
                            <tr><th>Date End</th><td>{{pricingWindow.date_expiry}}</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button @click="deletePricingWindow(pricingWindow.id)" type="button" class="btn btn-danger">Confirm</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { apiEndpoints, helpers } from '@/utils/hooks'

export default {
    name: 'pricingWindowConfirmDeleteModal',
    emits: ['deleteSuccess'],
    props: {
        pricingWindow: Object,
    },
    methods: {
        deletePricingWindow: function (pricingWindowId) {
            let vm = this;
            vm.pricingWindow.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            fetch(apiEndpoints.deletePricingWindow(pricingWindowId), {method: "DELETE"})
                .then(async response => {
                    // check for error response
                    if (!response.ok) {
                        return Promise.reject(`ERROR: Unable to delete pricing window with id ${pricingWindowId}`);
                    }
                    this.$emit("deleteSuccess", {
                            message: 'Pricing Window deleted successfully.',
                            pricingWindow: vm.pricingWindow,
                        }
                    );
                    $('#successMessageAlert').show();
                    var pricingWindowConfirmDeleteModalModal = bootstrap.Modal.getInstance(document.getElementById('pricingWindowConfirmDeleteModal'));
                    pricingWindowConfirmDeleteModalModal.hide();
                })
                .catch(error => {
                    this.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                });
            return false;
        },
    }
}
</script>
