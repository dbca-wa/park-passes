<template lang="html">
    <div class="container" id="internalInviteRetailerGroupUser">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>Invite a Retail User</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-3">
                        <template v-if="selectedRetailerGroup">
                            <div class="retailer-group">
                                <div>Retailer</div><div>{{ selectedRetailerGroup.name }}</div>
                                <div>Address</div><div>{{ selectedRetailerGroup.address_line_1 }}</div>
                                <div v-if="selectedRetailerGroup.address_line_2"></div><div v-if="selectedRetailerGroup.address_line_2">{{ selectedRetailerGroup.address_line_2 }}</div>
                                <div>Suburb</div><div>{{ selectedRetailerGroup.suburb }}</div>
                                <div>State</div><div>{{ selectedRetailerGroup.state }}</div>
                                <div>Postcode</div><div>{{ selectedRetailerGroup.postcode }}</div>
                                <div>Commission</div><div>{{ selectedRetailerGroup.commission_percentage }}%</div>
                            </div>
                        </template>
                        <template v-else>
                            <div>1. Select a Retailer. </div>
                            <div>2. Enter an Email Address.</div>
                        </template>
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
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
                                            <div>When you click 'Invite User' an invite will be sent to the user via email.<br>
                                                They will need to take action in order to be assigned to the retailer.<br>
                                                Once they do so, you will be notified by email and will need to approve their request before they can login and make sales.</div>
                                        </div>
                                    </div>
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
    <footer class="fixed-bottom mt-auto py-3 bg-light">

    </footer>
    <div v-if="!retailerGroups">
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
    },
    methods: {
        returnToRetailerGroupUserDash: function() {
            this.$router.push({name: 'internal-retailer-group-users'});
        },
        fetchRetailerGroups: function () {
            let vm = this;
            fetch(apiEndpoints.retailerGroupListInternal)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.retailerGroups = data.results
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
            fetch(apiEndpoints.createRetailerGroupInvite, requestOptions)
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
