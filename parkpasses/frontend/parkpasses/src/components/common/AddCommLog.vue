<template lang="html">
    <div id="AddComms">
        <Modal transition="modal fade" @ok="ok()" okText="Add Entry" @cancel="cancel()" title="Communication Log - Add Entry" large>
            <div class="container">
                <div class="row">
                    <form name="commsForm">
                        <alert :show.sync="showError" type="danger"><strong>{{ errorString }}</strong></alert>
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
                                        <select class="form-control" id="type" name="type" v-model="comms.type" required>
                                            <option value="" selected disabled>Select Type</option>
                                            <option value="email">Email</option>
                                            <option value="mail">Mail</option>
                                            <option value="phone">Phone</option>
                                        </select>
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
    </div>
</template>

<script>
//import $ from 'jquery'
import Modal from '@vue-utils/BootstrapModal.vue'
import Alert from '@vue-utils/Alert.vue'
import { helpers, apiEndpoints } from "@/utils/hooks.js"
export default {
    name: 'Add-Comms',
    components: {
        Modal,
        Alert
    },
    props: {
        url: {
            type: String,
            required: true
        }
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            form: null,
            comms: {
                type: '',
            },
            state: 'proposed_approval',
            addingComms: false,
            validation_form: null,
            errors: false,
            errorString: '',
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
        title: function () {
            return this.processing_status == 'With Approver' ? 'Issue Comms' : 'Propose to issue approval';
        }
    },
    methods: {
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
            this.close()
        },
        close: function () {
            let vm = this;
            this.isModalOpen = false;
            this.comms = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
            let file_length = vm.files.length;
            this.files = [];
            for (var i = 0; i < file_length; i++) {
                vm.$nextTick(() => {
                    $('.file-row-' + i).remove();
                });
            }
            this.attachAnother();
        },
        sendData: function () {
            let vm = this;
            vm.errors = false;
            let comms = new FormData(vm.form);
            vm.addingComms = true;
            vm.$http.post(vm.url, comms, {
            }).then((response) => {
                vm.addingComms = false;
                vm.close();
                //vm.$emit('refreshFromResponse',response);
            }, (error) => {
                vm.errors = true;
                vm.addingComms = false;
                vm.errorString = helpers.apiVueResourceError(error);
            });
        },
    },
    mounted: function () {

    }
}
</script>

<style lang="css">

select {
  color: #efefef;
}

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
