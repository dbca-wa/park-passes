<template lang="html">
    <div class="container" id="uploadPersonnelPasses">
        <div class="row px-4">
            <div class="col-sm-12 mb-4">
                <strong>Upload Personnel Passes</strong>
            </div>
        </div>
        <div class="row px-4">
            <div class="col-sm-12">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card card-default mb-3">
                            <div class="card-header">
                                Instructions
                            </div>
                            <div class="card-body card-collapse">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="mb-2">You must upload an .xlsx file.</div>
                                        <div class="mb-2">The first worksheet must contain the data.</div>
                                        <div>With the following columns:</div>
                                        <ul>
                                            <li>First Name</li>
                                            <li>Last Name</li>
                                            <li>Email Address</li>
                                            <li>Start Date (dd/mm/yy)</li>
                                        </ul>
                                        <a href="/static/parkpasses/xlsx/personnel-pass-data-file-template.xlsx" target="_blank">Download template (.xlsx)</a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div v-if="personnelPassType && personnelPassType.options[0]">

                            <div class="card card-default">
                                <div class="card-header">
                                    {{ personnelPassType.display_name }} Details
                                </div>
                                <div class="card-body card-collapse">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <table class="table">
                                                <tbody>
                                                    <tr>
                                                        <th>Description</th>
                                                        <td v-html="personnelPassType.description"></td>
                                                    </tr>
                                                    <tr>
                                                        <th>Duration</th>
                                                        <td>{{ personnelPassType.options[0].duration }} days.</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else>
                            <BootstrapSpinner :loading="true" :centerOfScreen="false" />
                        </div>

                    </div>

                    <div class="col-md-8">
                        <SectionToggle label="Upload Personnel Passes">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-3">
                                <label class="col-sm-4 col-form-label">Personnel Data File (.xslx)</label>
                                <div class="col-sm-8">
                                   <input id="personnelDataFile" name="personnelDataFile" ref="personnelDataFile" class="form-control" type="file" accept=".xlsx" required>
                                   <div id="validationPersonnelDataFileFeedback" class="invalid-feedback">
                                        Please select a .xlsx file to upload.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <div class="col">
                                    <BootstrapAlert>Please note this may take around 5 seconds for each row in your data file.</BootstrapAlert>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-sm-4">
                                </div>
                                <div class="col-sm-8 text-end">
                                    <button v-if="!loading" type="submit" class="btn licensing-btn-primary">Upload and Process</button>
                                    <BootstrapButtonSpinner v-else class="btn licensing-btn-primary px-5" />
                                </div>
                            </div>
                            </form>

                            <div class="row" v-if="errors">
                                <div class="col mt-3">
                                    <BootstrapAlert class="" v-for="(error, index) in errors" :key="index" type="danger" icon="exclamation-triangle-fill">{{ error }}</BootstrapAlert>
                                </div>
                            </div>

                        </SectionToggle>

                    </div>
                </div>

            </div>
        </div>
        <footer class="fixed-bottom mt-auto py-3 bg-light">
        <div class="container d-flex justify-content-end">
            <template v-if="!loading">
                <button @click="returnToDash" class="btn licensing-btn-primary me-2">Exit</button>
            </template>
        </div>
    </footer>
    </div>
</template>

<script>
import { apiEndpoints, constants } from '@/utils/hooks'
import BootstrapSpinner from '@/utils/vue/BootstrapSpinner.vue'
import BootstrapButtonSpinner from '@/utils/vue/BootstrapButtonSpinner.vue'
import BootstrapAlert from '@/utils/vue/BootstrapAlert.vue'
import Swal from 'sweetalert2'
import SectionToggle from '@/components/forms/SectionToggle.vue'

export default {
    name: "UploadPersonnelPassesForm",
    props: {

    },
    data() {
        return {
            personnelDataFile: null,
            personnelPassType: null,
            loadingPersonnelPassType: false,
            loading: false,
            errors: ''
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
        returnToDash: function() {
            this.$router.push({name: 'internal-dash'});
        },
        fetchPersonnelPass: function() {
            let vm = this;
            vm.loadingPersonnelPassType = true;
            fetch(apiEndpoints.passTypeInternal("personnel-pass")).then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    vm.errors = data;
                    return Promise.reject(error);
                }
                vm.personnelPassType = data;
                vm.fetchPassOptions(vm.personnelPassType.id);
            })
            .catch(error => {
                vm.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        fetchPassOptions: function (passTypeId) {
            let vm = this;
            fetch(apiEndpoints.passOptions(passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.loadingPersonnelPassType = false;
                if(data.results.length > 0) {
                    vm.personnelPassType.options = data.results
                } else {
                    this.systemErrorMessage = constants.ERRORS.CRITICAL;
                    console.error(`SYSTEM ERROR: Unable to load options for pass type id: ${vm.passTypeId}`);
                }
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.NETWORK;
                console.error("There was an error!", error);
            });
        },
        submitForm: function () {
            let vm = this;
            vm.loading = true;
            let formData = new FormData();
            let personnelDataFile = this.$refs.personnelDataFile;
            console.log(personnelDataFile.files[0]);
            formData.append('personnelDataFile', personnelDataFile.files[0]);
            const requestOptions = {
                method: "PUT",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'multipart/form-data'
                },
                body: formData
            };
            fetch(apiEndpoints.uploadPersonnelPasses, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        this.errors = data;
                        return Promise.reject(error);
                    }
                    let results = data.results;

                    let message = `<div style="text-align:left;"><ul>`;
                    message += `<li>Processed ${results.data_row_count} rows.</li>`;
                    message += `<li>${results.park_passes_duplicates} duplicates were found.</li>`;
                    message += `<li>Created ${results.park_passes_created} new passes.</li>`;
                    message += `</ul>`;
                    message += `<ul>`;
                    if(results.park_passes_errors && results.park_passes_errors.length > 0) {
                        for(let i = 0; i < results.park_passes_errors.length; i++){
                            message += `<li>${results.park_passes_errors[i]}</li>`;
                        }
                    } else {
                        message += `<li>No errors were encountered.</li>`;
                    }
                    message += `</ul></div>`;

                    vm.loading = false;

                    Swal.fire({
                        title: 'Success',
                        html: message,
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
                    vm.loading = false;

                });
        },
        validateForm: function (exitAfter) {
            console.log('validateForm');
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
        this.fetchPersonnelPass();
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

    .align-left {
  text-align: left;
}
</style>
