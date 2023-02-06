<template lang="html">
    <Modal transition="modal fade" @ok="validateForm()" okText="Add Entry" @cancel="cancel()" title="Communication Log - Add Entry" large>
        <div class="container">
            <div class="row">
                <form id="commsForm" class="needs-validation" novalidate>
                    <div class="col">
                        <div class="container">

                            <div class="row mb-3">
                                <div class="col">
                                    <input id="to" type="text" class="form-control" name="to" v-model="comms.to"
                                        placeholder="To" aria-label="To" autofocus required>

                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <input type="text" class="form-control" name="fromm" v-model="comms.fromm"
                                        placeholder="From" aria-label="From" required>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <template v-if="entryTypes">
                                    <select class="form-control" id="type" name="type" v-model="comms.entry_type" required>
                                        <option value="" selected disabled>Select Type</option>
                                        <option v-for="entryType in entryTypes" :value="entryType.id">{{entryType.entry_type}}</option>
                                    </select>
                                    </template>

                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <input type="text" class="form-control" name="subject" v-model="comms.subject"
                                        placeholder="Subject/Description" aria-label="Subject/Description" required>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <textarea name="text" class="form-control" v-model="comms.text"
                                        placeholder="Text" required></textarea>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <input @change="listAttachments" class="form-control" type="file" id="attachments"
                                        placeholder="Attachments" multiple>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <ul class="list-group" v-if="files">
                                        <li class="list-group-item" v-for="file in files">{{ file.name }}</li>
                                    </ul>
                                </div>
                            </div>

                        </div>
                    </div>
                </form>
            </div>
        </div>
    </modal>
</template>

<script>

import Modal from '@vue-utils/BootstrapModal.vue'
import { constants, utils, apiEndpoints } from "@/utils/hooks.js"

export default {
    name: 'AddCommLog',
    components: {
        Modal,
    },
    props: {
        url: {
            type: String,
            required: true
        },
        appLabel: {
            type: String,
            required: true
        },
        model: {
            type: String,
            required: true
        },
        objectId: {
            type: Number,
            required: true
        },
        customerId: {
            type: Number,
            required: false,
        }
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            form: null,
            comms: this.getDefaultCommsObject(),
            entryTypes: null,
            addingComms: false,
            validation_form: null,
            errors: false,
            successString: '',
            success: false,
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true
            },
            files: []
        }
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
    },
    methods: {
        getDefaultCommsObject: function () {
            return {
                entry_type: '',
            }
        },
        listAttachments: function () {
            console.log('happening')
            this.files = $('#attachments').prop('files');
        },
        ok: function () {
            let vm = this;
            if ($(vm.form).valid()) {
                vm.sendData();
            }
        },
        uploadFile(target, file_obj) {
            let vm = this;
            let _file = null;
            var input = $('.' + target)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function (e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index) {
            let length = this.files.length;
            $('.file-row-' + index).remove();
            this.files.splice(index, 1);
            this.$nextTick(() => {
                length == 1 ? this.attachAnother() : '';
            });
        },
        attachAnother() {
            this.files.push({
                'file': null,
                'name': ''
            })
        },
        cancel: function () {
            this.close();
        },
        close: function () {
            this.isModalOpen = false;
            this.comms = this.getDefaultCommsObject();
            this.errors = false;
        },
        fetchEntryTypes: function () {
            let vm = this;
            fetch(apiEndpoints.entryTypes)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.entryTypes = data.results
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
                console.error("There was an error!", error);
            });
        },
        submitForm: function () {
            let vm = this;
            vm.addingComms = true;
            vm.comms.app_label = vm.appLabel
            vm.comms.model = vm.model
            vm.comms.object_id = vm.objectId
            vm.comms.customer = vm.customerId
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.comms)
            };
            fetch(vm.url, requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }

                console.log(data);
                let files = $('#attachments')[0].files;
                utils.uploadOrgModelDocuments(data.comms_log_entry_content_type, data.id, files);

                vm.addingComms = false;
                vm.close();
            })
            .catch(error => {
                this.systemErrorMessage = constants.ERRORS.SYSTEM;
                console.error("There was an error!", error);
            });
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('commsForm')

            if(form.checkValidity()){
                console.log('Form valid');
                vm.submitForm();
            } else {
                form.classList.add('was-validated');
                $('#commsForm').find(":invalid").first().focus();
                console.log($(".invalid-feedback:first"));
                //$(".invalid-feedback:visible:first").siblings('input').focus();
            }

            return false;
        },
    },
    created: function () {
        this.fetchEntryTypes();
        console.log('this.customerId = ' + this.customerId);
    },
    mounted: function () {

    }
}
</script>

<style lang="css">


select {
  color: #efefef;
}

select:invalid { color: #6c757d; }

.btn-file {
    position: relative;
    overflow: hidden;
}

.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}

.top-buffer {
    margin-top: 5px;
}

.top-buffer-2x {
    margin-top: 10px;
}
</style>
