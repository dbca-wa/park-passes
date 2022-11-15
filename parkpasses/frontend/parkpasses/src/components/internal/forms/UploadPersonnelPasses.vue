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
                    <div class="col-md-3">
                        <div class="card card-default">
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
                                            <li>End Date (dd/mm/yy)</li>
                                        </ul>
                                        <a href="">Download template (.xlsx)</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-1">

                    </div>
                    <div class="col-md-8">
                        <SectionToggle label="Upload Personnel Passes">
                            <form @submit.prevent="validateForm" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <label class="col-sm-4 col-form-label">Personnel Data File (.xslx)</label>
                                <div class="col-sm-8">
                                   <input id="personnelDataFile" name="personnelDataFile" ref="personnelDataFile" class="form-control" type="file" accept=".xlsx" required>
                                   <div id="validationPersonnelDataFileFeedback" class="invalid-feedback">
                                        Please select a .xlsx file to upload.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-sm-4">
                                </div>
                                <div class="col-sm-8">
                                    <button type="submit" class="btn licensing-btn-primary">Upload and Process</button>
                                </div>
                            </div>
                            </form>
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
        returnToDash: function() {
            this.$router.push({name: 'internal-dash'});
        },
        submitForm: function () {
            let vm = this;
            let formData = new FormData();
            let file = this.$refs.personnelDataFile;
            formData.append('personnelDataFile', file[0]);
            const requestOptions = {
                method: "POST",
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

                    Swal.fire({
                        title: 'Success',
                        text: 'Personnel data file uploaded and processed successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                })
                .catch(error => {
                    this.systemErrorMessage = constants.ERRORS.NETWORK;
                    console.error("There was an error!", error);
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
