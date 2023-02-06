<template lang="html">
    <div v-if="retailerGroups" class="container" id="internalInviteRetailerGroupUser">
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card card-default">
                            <div class="card-header">
                                <strong>Retailer</strong>
                            </div>
                            <div class="card-body card-collapse">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <template v-if="selectedRetailerGroup">
                                            <table class="table table-striped table-sm table-bordered">
                                                <tbody>
                                                <tr><th width="35">Retailer</th><td>{{ selectedRetailerGroup.ledger_organisation_name }}</td></tr>
                                                <tr><th>Commission</th><td>{{ selectedRetailerGroup.commission_percentage }}%</td></tr>
                                                </tbody>
                                            </table>
                                        </template>
                                        <template v-else>
                                            <div>Select a Retailer...</div>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-7">
                        <SectionToggle label="Invite a User">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <label class="col-sm-3 col-form-label">Retailer</label>
                                <div class="col-sm-6">
                                    <select v-if="retailerGroups && retailerGroups.length>1" class="form-select" id="retailerGroup" name="retailerGroup" v-model="selectedRetailerGroup" required>
                                        <option value="" selected disabled>Select a Retailer</option>
                                        <option v-for="retailerGroup in retailerGroups" :key="retailerGroup.id" :value="retailerGroup">{{retailerGroup.ledger_organisation_name}}</option>
                                    </select>
                                    <span class="form-text text-dark">{{retailerGroups[0].ledger_organisation_name}}</span>
                                    <div id="validationRetailerGroupFeedback" class="invalid-feedback">
                                        Please select a retailer to invite the user to.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label class="col-sm-3 col-form-label">Email Address</label>
                                <div class="col-sm-6">
                                    <input class="form-control" type="email" name="email" ref="email" v-model="invite.email" required :autofocus="retailerGroups && retailerGroups.length==1" />
                                    <div id="validationRetailerGroupFeedback" class="invalid-feedback">
                                        Please enter the email of the user to invite.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col">
                                    <BootstrapAlert>
                                        <ol class="list-group list-group-numbered">
                                            <li class="list-group-item mb-2">When you click 'Invite User' an invite will be sent to the user via email.</li>
                                            <li class="list-group-item">They will need to take action in order to log in and take sales.</li>
                                        </ol>
                                    </BootstrapAlert>
                                </div>
                            </div>
                            <div class="container mt-3 d-flex justify-content-end">
                                <template v-if="!loading">
                                    <button @click="returnToRetailerGroupUserDash" class="btn licensing-btn-primary me-2">Exit</button>
                                    <button @click="validateForm()" class="btn licensing-btn-primary me-2">Invite User</button>
                                </template>
                                <template v-else>
                                    <button class="btn licensing-btn-primary px-4 ms-2">
                                        <div class="spinner-border spinner-border-sm text-light" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                    </button>
                                </template>
                            </div>
                            </form>
                        </SectionToggle>
                    </div>
                </div>

            </div>
        </div>

    </div>

    <div v-if="!retailerGroups">
        <BootstrapSpinner :isLoading="true" />
    </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { apiEndpoints, constants, helpers } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'

import Swal from 'sweetalert2'
import SectionToggle from '@/components/forms/SectionToggle.vue'

export default {
    name: "InviteRetailUserForm",
    props: {

    },
    data() {
        return {
            selectedRetailerGroup: '',
            invite: {
                email: '',
                retailer_group: '',
            },
            retailerGroups: null,
            loading: false,
        }
    },
    computed: {

    },
    components: {
        SectionToggle,
        BootstrapSpinner,
        BootstrapAlert,
    },
    methods: {
        returnToRetailerGroupUserDash: function() {
            this.$router.push({name: 'retailer-retailer-group-users'});
        },
        fetchRetailerGroups: function () {
            let vm = this;
            fetch(apiEndpoints.retailerGroupsForUser)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.retailerGroups = data
                if(vm.retailerGroups && vm.retailerGroups.length==1){
                    vm.selectedRetailerGroup = vm.retailerGroups[0];
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
            vm.invite.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            vm.invite.retailer_group = vm.selectedRetailerGroup.id;
            console.log(vm.invite);
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.invite)
            };
            fetch(apiEndpoints.createRetailerGroupInviteRetailer, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    Swal.fire({
                        title: 'Success',
                        text: 'User invite sent successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    vm.$router.push({name: 'retailer-retailer-group-users'});
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.SYSTEM;
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
    created: function() {
        const route = useRoute();
        this.fetchRetailerGroups();
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
