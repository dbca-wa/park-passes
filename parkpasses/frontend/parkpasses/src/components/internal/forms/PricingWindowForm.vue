<template lang="html">
    <div v-if="pricingWindow" class="container" id="internalPricingWindow">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>{{ pricingWindowTitle() }}</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-3">
                        <StatusPanel :status="pricingWindow.status" :badge="true" :badgeClass="badgeClass" class="pt-3" />
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
                        <SectionToggle :label="pricingWindow.name">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Pass Type</label>
                                <div class="col-sm-8">
                                    <span class="form-text">{{ pricingWindow.pass_type_display_name }}</span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">name</label>
                                <div class="col-sm-8">
                                    <span v-if="isDefaultPricingWindow" class="form-text">{{ pricingWindow.name }}</span>
                                    <input v-else class="form-control" name="name" type="text" v-model="pricingWindow.name" required>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="startDate" class="col-sm-4 col-form-label">Start Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input class="form-control" ref="startDate" name="startDate" type="date" v-model="pricingWindow.date_start" :disabled="hasPricingWindowExpired" :max="maxStartDate" required>
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="expiryDate" class="col-sm-4 col-form-label">End Date</label>
                                <div class="col-sm-8">
                                    <span class="form-text">
                                        <input v-if="pricingWindow.date_expiry" class="form-control" name="expiryDate" type="date" v-model="pricingWindow.date_expiry" :required="!isDefaultPricingWindow">
                                        <span v-else class="form-text">
                                            <span class="form-text">A Default Pricing Window never ends.</span>
                                        </span>
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <label for="options" class="col-sm-4 col-form-label">Options</label>
                                <div class="col-sm-8">
                                    <template v-if="pricingWindow.options && pricingWindow.options.length > 0">
                                        <table class="table table-stiped">
                                            <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Duration (Days)</th>
                                                    <th>Price</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(option, index) in pricingWindow.options" :key="option.id">
                                                    <td>
                                                        <span class="form-text">{{ option.name }}</span>
                                                    </td>
                                                    <td>
                                                        <span class="form-text">{{ option.duration }}</span>
                                                    </td>
                                                    <td>
                                                        <input @change="addDecimalPlaces(option.price, index)" class="form-control" :id="'option' + option.id" :name="'option' + option.id" type="number" v-model="option.price" required>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </template>
                                    <span v-else class="form-text">Pricing window has no options. THIS IS BAD.</span>
                                </div>
                            </div>
                            </form>
                        </SectionToggle>

                    </div>
                </div>

            </div>
        </div>

    </div>
    <footer v-if="pricingWindow" class="fixed-bottom mt-auto py-3 bg-light">
        <div class="container d-flex justify-content-end">
            <template v-if="!loading">
                <button @click="returnToPricingWindowDash" class="btn licensing-btn-primary me-2">Exit</button>
                <button v-if="!hasPricingWindowExpired" @click="validateForm(true)" class="btn licensing-btn-primary me-2">Save and Exit</button>
                <button v-if="!hasPricingWindowExpired" @click="validateForm(false)" class="btn licensing-btn-primary">Save and Continue Editing</button>
            </template>
            <template v-else>
                <button class="btn licensing-btn-primary px-4 ms-2">
                    <div class="spinner-border spinner-border-sm text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </button>
            </template>
        </div>
    </footer>
    <div v-if="!pricingWindow">
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
import CommsLog from '@/components/common/CommsLog.vue'
import StatusPanel from '@/components/common/StatusPanel.vue'

export default {
    name: "PricingWindowForm",
    props: {

    },
    data() {
        return {
            pricingWindowId: null,
            pricingWindow: null,
            listUserActionsLogUrl: null,
            listCommsUrl: null,
            maxStartDate: null,
            createCommUrl: apiEndpoints.createCommunicationsLogEntry,
            pdfUrl: null,
            appLabel: constants.PARKPASSES_APP_LABEL,
            model: constants.PARKPASSES_MODELS_PRICING_WINDOW,
            loading: false,
        }
    },
    computed: {
        isDefaultPricingWindow: function () {
            return constants.PARKAPSSES_DEFAULT_PRICING_WINDOW_NAME === this.pricingWindow.name;
        },

        hasPricingWindowExpired: function () {
            return constants.PASS_STATUS_EXPIRED==this.pricingWindow.processing_status_display_name;
        },
        badgeClass: function () {
            return helpers.getStatusBadgeClass(this.pricingWindow.status);
        },
    },
    components: {
        SectionToggle,
        CommsLog,
        BootstrapSpinner,
        BootstrapAlert,
        StatusPanel,
    },
    methods: {
        returnToPricingWindowDash: function() {
            this.$router.push({name: 'internal-pricing-windows'});
        },
        pricingWindowTitle: function () {
            let originalPricingWindow = Object.assign({}, this.pricingWindow);
            let name = originalPricingWindow.name;
            const title = `${name} Pricing Window for ${originalPricingWindow.pass_type_display_name}`;
            return title;
        },
        addDecimalPlaces: function (price, index) {
            if (price) {
                this.pricingWindow.options[index].price = parseFloat(price).toFixed(2);
            }
        },
        fetchPricingWindow: function (pricingWindowId) {
            let vm = this;
            fetch(apiEndpoints.retrievePricingWindowInternal(pricingWindowId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.pricingWindow = data
                //vm.pricingWindow.options = Object.assign({}, data.options)
                console.log(vm.pricingWindow);

                vm.listUserActionsLogUrl = apiEndpoints.listUserActionsLog(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_PRICING_WINDOW,
                    vm.pricingWindow.id
                )
                vm.listCommsUrl = apiEndpoints.listCommunicationsLogEntries(
                    constants.PARKPASSES_APP_LABEL,
                    constants.PARKPASSES_MODELS_PRICING_WINDOW,
                    vm.pricingWindow.id
                )
                if(constants.PARKAPSSES_DEFAULT_PRICING_WINDOW_NAME==vm.pricingWindow.name){
                    let yesterday = new Date();
                    yesterday.setDate(yesterday.getDate() - 1);
                    this.maxStartDate = yesterday.toLocaleDateString('en-ca');
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        submitForm: function (exitAfter) {
            let vm = this;
            vm.loading = true;
            vm.pricingWindow.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            console.log(vm.pricingWindow);
            const requestOptions = {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pricingWindow)
            };
            fetch(apiEndpoints.updatePricingWindowInternal(vm.pricingWindow.id), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }

                    Swal.fire({
                        title: 'Success',
                        text: 'Park Pricing Window updated successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    if(exitAfter) {
                        vm.returnToPricingWindowDash();
                    }
                    vm.pricingWindow.date_expiry = data.date_expiry
                    var forms = document.querySelectorAll('.needs-validation');
                    Array.prototype.slice.call(forms).forEach(function (form) {
                        form.classList.remove('was-validated');
                    });
                    vm.pricingWindow.why = '';
                    $('#reasonFiles').val('');
                    vm.loading = false;
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                });
            return false;
        },
        validateForm: function (exitAfter) {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation');
            Array.prototype.slice.call(forms)
                .forEach(function (form) {
                    if (form.checkValidity()) {
                        vm.submitForm(exitAfter);
                    } else {
                        form.classList.add('was-validated');
                        $(".invalid-feedback:visible:first").siblings('input').focus();
                    }
                });
            return false;
        }
    },
    created: function() {
        const route = useRoute()
        this.fetchPricingWindow(route.params['pricingWindowId']);
    },
    mounted: function () {
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
</style>
