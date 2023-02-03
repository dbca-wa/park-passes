<template>
    <div class="modal fade" id="processRetailerUserGroupInviteModal" tabindex="-1" aria-labelledby="processRetailerUserGroupInviteModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div v-if="retailerGroupUserInvite" class="modal-content">
                <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                    <div class="modal-header">
                        <h5 class="modal-title" id="processRetailerUserGroupInviteModalLabel">Process Retail User Invite</h5>
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
                            Has accepted the invitation to join the following retailer:
                        </div>
                        <div class="mb-3">
                            <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupUserInvite.retailer_group_name }}</span></div>
                        </div>
                        <div class="mb-3">
                            The retailer currently has:
                        </div>
                        <div class="mb-3">
                            <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupUserInvite.user_count_for_retailer_group }} Users</span></div>
                        </div>
                        <div class="form-check form-switch">
                            <label for="makeAdmin" class="form-check-label">Make this User an Admin</label>
                            <input class="form-check-input" type="checkbox" id="makeAdmin" name="makeAdmin" v-model="approval.is_admin" :checked="getAdminDefault" :disabled="getAdminDefault"  aria-describedby="makeAdminHelpBlock">
                        </div>
                        <div id="makeAdminHelpBlock" class="form-text">
                            Admin users can invite other users to their retailer group.
                        </div>
                        <div v-if="!retailerGroupUserInvite.user_count_for_retailer_group" class="alert alert-warning d-flex align-items-center mt-3" role="alert">
                            <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                    <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                </symbol>
                            </svg>
                            <svg class="bi flex-shrink-0 me-1" width="18" height="18" role="img" aria-label="Warning:"><use xlink:href="#exclamation-triangle-fill"/></svg>
                            <div>
                                The first user added to a group must be an admin.
                            </div>
                        </div>
                        {{ approval }}
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
    name: 'ProcessRetailerGroupUserInviteModal',
    emits: ['approvalProcessed'],
    props: {
        retailerGroupUserInvite: {
            type: Object,
            default: {
                user_count_for_retailer_group:0,
            },
        },
    },
    data() {
        return {
            approval: {
                is_admin: false,
            },
            loading: false,
        }
    },
    computed: {
        getAdminDefault: function() {
            if (this.retailerGroupUserInvite){
                console.log(this.retailerGroupUserInvite.user_count_for_retailer_group);
                if(0==this.retailerGroupUserInvite.user_count_for_retailer_group){
                    return true;
                }
            }
            console.log('returning false');
            return false;

        },
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

                var processRetailerUserGroupInviteModal = bootstrap.Modal.getInstance(document.getElementById('processRetailerUserGroupInviteModal'));
                processRetailerUserGroupInviteModal.hide();
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
                console.error("There was an error!", error);
            });
        },
    },
    mounted: function(){
        if (0==this.retailerGroupUserInvite) {
            this.approval.is_admin = true;
        } else {
            this.approval.is_admin = false;
        }
    },
}
</script>
