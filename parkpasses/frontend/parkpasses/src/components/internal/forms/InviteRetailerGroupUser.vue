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
                                                <tr><th width="35">Retailer</th><td>{{ selectedRetailerGroup.name }}</td></tr>
                                                <tr><th>Address</th><td>{{ selectedRetailerGroup.address_line_1 }}</td></tr>
                                                <tr v-if="selectedRetailerGroup.address_line_2"><td>&nbsp;</td><td>{{ selectedRetailerGroup.name }}</td></tr>
                                                <tr><th>Suburb</th><td>{{ selectedRetailerGroup.suburb }}</td></tr>
                                                <tr><th>State</th><td>{{ selectedRetailerGroup.state }}</td></tr>
                                                <tr><th>Postcode</th><td>{{ selectedRetailerGroup.postcode }}</td></tr>
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
                        <SectionToggle label="Invite a Retail User">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <label class="col-sm-3 col-form-label">Retailer</label>
                                <div class="col-sm-6">
                                    <select class="form-select" id="retailerGroup" name="retailerGroup" v-model="selectedRetailerGroup" required>
                                        <option value="" selected disabled>Select a Retailer</option>
                                        <option v-for="retailerGroup in retailerGroups" :key="retailerGroup.id" :value="retailerGroup">{{retailerGroup.name}}</option>
                                    </select>
                                    <div id="validationRetailerGroupFeedback" class="invalid-feedback">
                                        Please select a retailer to invite the user to.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label class="col-sm-3 col-form-label">Email Address</label>
                                <div class="col-sm-6">
                                    <input class="form-control" type="email" v-model="invite.email" required />
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
                                            <li class="list-group-item mb-2">They will need to take action in order to be assigned to the retailer.</li>
                                            <li class="list-group-item">Once they do so, you will be notified by email and will need to approve their request before they can login and make sales.</li>
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
            this.$router.push({name: 'internal-retailer-group-users'});
        },
        fetchRetailerGroups: function () {
            let vm = this;
            fetch(apiEndpoints.activeRetailerGroupListInternal)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.retailerGroups = data
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
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
            fetch(apiEndpoints.createRetailerGroupInviteInternal, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    Swal.fire({
                        title: 'Success',
                        text: 'Retail user invite sent successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    vm.$router.push({name: 'internal-retailer-group-users'});
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
