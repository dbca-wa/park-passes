<template>
    <div class="modal fade" id="retailerUserGroupInviteApprovalModal" tabindex="-1" aria-labelledby="retailerUserGroupInviteApprovalModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div v-if="retailerGroupUserInvite" class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="retailerUserGroupInviteApprovalModalLabel">Approve or Deny Retail User Invite</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            The account with email:
                        </div>
                        <div class="mb-3">
                            <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupUserInvite.email }}</span></div>
                        </div>
                        <div class="mb-3">
                            Was invited to join the following retailer:
                        </div>
                        <div class="mb-3">
                            <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupUserInvite.retailer_group_name }}</span></div>
                        </div>
                        <div class="form-check form-switch">
                            <label for="makeAdmin" class="form-check-label">Make this User an Admin</label>
                            <input class="form-check-input" type="checkbox" id="makeAdmin" name="makeAdmin" v-model="approval.is_admin" aria-describedby="makeAdminHelpBlock">
                        </div>
                        <div id="makeAdminHelpBlock" class="form-text">
                            Admin users can invite other users to their retailer group.
                        </div>

                    </div>
                    <div class="modal-footer">
                        <template v-if="loading">
                            <BootstrapButtonSpinner class="btn btn-secondary" isLoading="loading" disabled />
                            <BootstrapButtonSpinner class="btn btn-danger" isLoading="loading" disabled />
                            <BootstrapButtonSpinner class="btn btn-success" isLoading="loading" disabled />
                        </template>
                        <template v-else>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Exit</button>
                            <button type="button" @click="processApproval(false)" class="btn btn-danger">Deny</button>
                            <button type="button" @click="processApproval(true)" class="btn btn-success">Approve</button>
                        </template>
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
    name: 'RetailerGroupUserInviteApproveModal',
    emits: ['approvalProcessed'],
    props: {
        retailerGroupUserInvite: {
            type: Object,
            default: null,
        },
    },
    data() {
        return {
            approval: {
                is_admin:false,
            },
            loading: false,
        }
    },
    components: {
        BootstrapButtonSpinner,
    },
    methods: {
        processApproval: function (approved) {
            let vm = this;
            vm.loading = true;
            vm.approval.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            vm.approval.approved = approved;
            alert(JSON.stringify(vm.approval));
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.approval)
            };
            fetch(apiEndpoints.processRetailerGroupInvite(this.retailerGroupUserInvite.id), requestOptions).then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    this.errors = data;
                    return Promise.reject(error);
                }
                vm.$emit('approvalProcessed')

                Swal.fire({
                    title: 'Success',
                    text: 'Retail User Invite Processed successfully.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                });

                vm.loading = false;

                var retailerUserGroupInviteApprovalModal = bootstrap.Modal.getInstance(document.getElementById('retailerUserGroupInviteApprovalModal'));
                retailerUserGroupInviteApprovalModal.hide();
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
    },
}
</script>
