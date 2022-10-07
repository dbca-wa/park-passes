<template lang="html">
    <div v-if="retailerGroupInvite" class="container" id="internalInviteRetailerGroupUser">
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col">
                        <SectionToggle label="Respond to Retail User Invite">
                            <template v-if="'UA'==retailerGroupInvite.status">
                                <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                    <symbol id="check-circle-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                                    </symbol>
                                    <symbol id="info-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                                    </symbol>
                                    <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                    </symbol>
                                    </svg>
                                    <div class="alert alert-primary d-flex align-items-center" role="alert">
                                        <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                                        <div>
                                            <div>
                                                <div>A notification of your acceptance has been sent to the Park Passes system staff.</div>
                                                <div>You will be notified by email when your invite has been approved.</div>
                                            </div>
                                        </div>
                                    </div>
                            </template>
                            <template v-else>
                            <form @submit.prevent="submitForm" class="needs-validation" novalidate>
                            <div class="row mb-3 mt-3 align-items-center">
                                <div class="col">
                                    Your account with email:
                                </div>
                            </div>
                            <div class="row mb-3 align-items-center">
                                <div class="col-sm-6">
                                    <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupInvite.email }}</span></div>
                                </div>
                            </div>
                            <div class="row mb-3 align-items-center">
                                <div class="col">
                                   Has been invited to be a member of the following retailer:
                                </div>
                            </div>
                            <div class="row mb-5 align-items-center">
                                <div class="col-sm-6 align-middle">
                                    <div class="lead"><span class="badge org-badge-primary">{{ retailerGroupInvite.retailer_group_name }}</span></div>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                    <symbol id="check-circle-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                                    </symbol>
                                    <symbol id="info-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                                    </symbol>
                                    <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                    </symbol>
                                    </svg>
                                    <div class="alert alert-primary d-flex align-items-center" role="alert">
                                        <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                                        <div>
                                            <div>
                                                When you click 'Accept Invite' an email will be sent to the Park Passes system staff<br>
                                                They will need to approve you as a member before you can log in and take sales.<br>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="container mt-3 d-flex justify-content-end">
                                <button type="submit" class="btn licensing-btn-primary me-2">Accept Invite</button>
                            </div>
                            </form>
                            </template>
                        </SectionToggle>
                    </div>
                </div>

            </div>
        </div>

    </div>

    <div v-if="!retailerGroupInvite">
        <BootstrapSpinner isLoading="true" />
    </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import Swal from 'sweetalert2'
import SectionToggle from '@/components/forms/SectionToggle.vue'

export default {
    name: "InviteRetailUserForm",
    props: {

    },
    data() {
        return {
            uuid: null,
            retailerGroupInvite: null,
            loading: false,
        }
    },
    computed: {

    },
    components: {
        SectionToggle,
        BootstrapSpinner,
    },
    methods: {
        returnToRetailerGroupUserDash: function() {
            this.$router.push({name: 'internal-retailer-group-users'});
        },
        fetchRetailerGroupInvite: function (uuid) {
            let vm = this;
            vm.loading = true;
            fetch(apiEndpoints.retailerGroupInviteRetrieveExternal(uuid))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.retailerGroupInvite = data
                vm.loading = false;
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        submitForm: function () {
            let vm = this;
            vm.loading = true;
            vm.retailerGroupInvite.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.retailerGroupInvite);
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.retailerGroupInvite)
            };
            fetch(apiEndpoints.acceptRetailerGroupInvite(this.uuid), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    vm.retailerGroupInvite = data
                    Swal.fire({
                        title: 'Success',
                        text: 'Retail user invite acceptance sent successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                });
            return false;
        },
    },
    created: function() {
        const route = useRoute();
        this.uuid = route.params.uuid;
        this.fetchRetailerGroupInvite(this.uuid);
    }
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

    .retailer-group {
        display:grid;
        gap:10px;
        grid-template-columns:1fr 1fr;
    }
</style>
