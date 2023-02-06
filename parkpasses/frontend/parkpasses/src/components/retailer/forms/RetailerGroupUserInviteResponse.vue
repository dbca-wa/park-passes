<template lang="html">
    <div v-if="retailerGroupInvite" class="container" id="internalInviteRetailerGroupUser">
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col">
                        <SectionToggle label="Respond to Retail User Invite">
                            <template v-if="'UA'==retailerGroupInvite.status">
                                <BootstrapAlert>
                                    <div>A notification of your acceptance has been sent to the Park Passes system staff.</div>
                                    <div>You will be notified by email when your invite has been approved.</div>
                                </BootstrapAlert>
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
                                    <BootstrapAlert>
                                        <div v-if="'I'==retailerGroupInvite.initiated_by">
                                            When you click 'Accept Invite' an email will be sent to the Park Passes system staff<br>
                                            They will need to approve you as a member before you can log in and take sales.<br>
                                        </div>
                                        <div v-if="'R'==retailerGroupInvite.initiated_by">
                                            When you click 'Accept Invite' you will be redirected to the retailer
                                            dashboard where you can begin to take retail sales.
                                        </div>
                                    </BootstrapAlert>
                                </div>
                            </div>
                            <div class="container mt-3 d-flex justify-content-end">
                                <BootstrapButtonSpinner v-if="loading" class="btn licensing-btn-primary me-2" />
                                <button v-else type="submit" class="btn licensing-btn-primary me-2">Accept Invite</button>
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
        <BootstrapSpinner :isLoading="true" />
    </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

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
        BootstrapButtonSpinner,
        BootstrapAlert,
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
                if('A'==vm.retailerGroupInvite.status){
                    window.location.href = '/retailer/'
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
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

                    if('A'==vm.retailerGroupInvite.status){
                        window.location.href = '/retailer/'
                    } else {
                        Swal.fire({
                            title: 'Success',
                            text: 'Retail user invite acceptance sent successfully.',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });
                    }
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.SYSTEM;
                    console.error("There was an error!", error);
                });
            return false;
        },
    },
    created: function() {
        const route = useRoute();
        this.uuid = route.params.uuid;
        this.fetchRetailerGroupInvite(this.uuid);
    },
    mounted: function () {
        if('A'==vm.retailerGroupInvite.status){
            this.$router.push({name: 'retailer'});
        }
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
