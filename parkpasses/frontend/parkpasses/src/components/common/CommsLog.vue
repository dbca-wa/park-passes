<template id="CommsLogs">
    <div class="">
        <div class="card card-default">
            <div class="card-header">
                Logs
            </div>
            <div class="card-body card-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Communications</strong><br/>
                        <div class="row">
                            <div class="col-sm-5">
                                <a tabindex="2" ref="showCommsBtn" @click.prevent="" class="actionBtn">Show</a>
                            </div>
                            <template v-if="!disableAddEntry">
                                <div class="col-sm-1">
                                    <span>|</span>
                                </div>
                                <div class="col-sm-5">
                                    <a ref="addCommsBtn" @click="addComm()" class="actionBtn pull-right">Add Entry</a>
                                </div>
                            </template>
                        </div>
                    </div>
                    <div class="col-sm-12 top-buffer-s">
                        <strong>Actions</strong><br/>
                        <a tabindex="2" ref="showActionBtn" @click.prevent="" class="actionBtn">Show</a>
                    </div>
                </div>
            </div>
        </div>
        <AddCommLog id="AddComms" ref="addComm" :url="commAddUrl" :appLabel="appLabel" :model="model" :objectId="objectId" :customerId="customerId" />
    </div>
</template>

<script>
import AddCommLog from './AddCommLog.vue'
import {
    apiEndpoints,
    helpers,
    constants,
}from '@/utils/hooks'
import { v4 as uuid } from 'uuid';

export default {
    name: 'CommsLogSection',
    props: {
        commsUrl:{
            type: String,
            required: true
        },
        logsUrl:{
            type: String,
            required: true
        },
        commAddUrl:{
            type: String,
            required: true
        },
        disableAddEntry: {
            type: Boolean,
            default: false
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
    data() {
        let vm = this;
        return {
            uuid: uuid(),
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            actionsTable: null,
            popoversInitialised: false,
            actionsDtOptions:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[2, 'desc']], // order the non-formatted date as a hidden column
                dom:
                    "<'row'<'col-sm-4'l><'col-sm-8'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                serverSide: true,
                ajax: {
                    "url": vm.logsUrl,
                    "dataSrc": 'data',
                },
                columns:[
                    {
                        title: 'Who',
                        data:"who",
                        orderable: false
                    },
                    {
                        title: 'What',
                        data:"what",
                        orderable: false
                    },
                    {
                        title: 'When',
                        data:"when",
                        orderable: true,
                        mRender:function(data,type,full){
                            return moment(data).format(vm.dateFormat);
                        }
                    },
                    {
                        title: 'Why',
                        data:"why",
                        orderable: false,
                        mRender:function(data,type,full){
                            return full.why ? full.why : "N/A";
                        }
                    },
                    {
                        title: 'Documents',
                        data: "documents",
                        orderable: false,
                        mRender:function(data,type,full){
                            if(full.documents && 1<full.documents.length){
                                console.log(full.documents)
                                let documentsHtml = '';
                                // Need to add a call to an api here to access documents in protected media
                                for(let i=0;i<full.documents.length;i++){
                                    documentsHtml += `<a href="${apiEndpoints.retrieveOrgModelDocument(full.documents[i].id)}" target="_blank">${full.documents[i].file_name}</a><br />`;
                                }
                                return documentsHtml;
                            } else {
                                return 'No Files'
                            }
                        }
                    },
                    {
                        data: 'when',
                        visible: false
                    }
                ]
            },
            commsDtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[8, 'desc']], // order the non-formatted date as a hidden column
                processing:true,
                dom:
                    "<'row'<'col-sm-4'l><'col-sm-8'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                ajax: {
                    "url": vm.commsUrl,
                    "dataSrc": 'data',
                },
                columns:[
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            //return moment(date).format("DD-MMM-YYYY HH:mm:ss");
                            //return moment(date).format(vm.DATE_TIME_FORMAT);
                            return moment(date).format(vm.dateFormat);
                        }
                    },
                    {
                        title: 'Type',
                        data: 'entry_type_display_name'
                    },
                    /*{
                        title: 'Reference',
                        data: 'reference'
                    },*/
                    {
                        title: 'To',
                        data: 'to',
                        //render: vm.commaToNewline
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            console.log('in createdCell of TO')
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            //$(cell).popover();
                        }
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        //render: vm.commaToNewline
                          'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },

                        'createdCell': function (cell) {
                            console.log('in createdCell of CC')
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            //$(cell).popover();
                        }
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject',
                          'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            console.log('in createdCell of Subject/Desc')
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            //$(cell).popover();
                        }
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            console.log('in createdCell of Text')
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            //$(cell).popover();
                        }
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        mRender:function(data,type,full){
                            if(full.documents && 1<full.documents.length){
                                console.log(full.documents)
                                let documentsHtml = '';
                                // Need to add a call to an api here to access documents in protected media
                                for(let i=0;i<full.documents.length;i++){
                                    documentsHtml += `<a href="${apiEndpoints.retrieveOrgModelDocument(full.documents[i].id)}" target="_blank">${full.documents[i].file_name}</a><br />`;
                                }
                                return documentsHtml;
                            } else {
                                return 'No Files'
                            }
                        }
                    },
                    {
                        title: 'Created',
                        data: 'created',
                        visible: false
                    }
                ]
            },
            commsTable : null,
        }
    },
    components:{
        AddCommLog
    },
    watch:{
    },
    computed: {
    },
    methods:{
        initialiseCommLogs: function(){
            // To allow table elements (ref: https://getbootstrap.com/docs/5.1/getting-started/javascript/#sanitizer)
            var myDefaultAllowList = bootstrap.Tooltip.Default.allowList
            myDefaultAllowList.table = []

            let vm = this;
            let commsLogId = 'comms-log-table' + vm.uuid;
            let popover_name = 'popover-' + vm.uuid + '-comms';
            let popover_elem = $(vm.$refs.showCommsBtn)[0]
            let my_content = '<table id="' + commsLogId + '" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%"></table>'
            let my_template = '<div class="popover ' + popover_name +'" role="tooltip"><div class="popover-arrow" style="top:110px;"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'

            new bootstrap.Popover(popover_elem, {
                sanitize: false,
                html: true,
                content: my_content,
                template: my_template,
                title: 'Communication logs',
                container: 'body',
                placement: 'right',
                trigger: "click",
            })
            popover_elem.addEventListener('inserted.bs.popover', () => {
                // when the popover template has been added to the DOM
                vm.commsTable = $('#' + commsLogId).DataTable(vm.commsDtOptions);

                vm.commsTable.on('draw', function () { // Draw event - fired once the table has completed a draw.

                    var popoverTriggerList = [].slice.call(document.querySelectorAll('#' + commsLogId + ' [data-bs-toggle="popover"]'))
                    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
                        return new bootstrap.Popover(popoverTriggerEl)
                    })
                })
            })
            popover_elem.addEventListener('shown.bs.popover', () => {
                // when the popover has been made visible to the user
                let el = vm.$refs.showCommsBtn
                var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
                var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
                var diff = el_bounding_top - popover_bounding_top;
                var x = diff + 5;
                $('.'+popover_name).children('.arrow').css('top', x + 'px');

            })

        },
        initialiseActionLogs: function(){
            // To allow table elements (ref: https://getbootstrap.com/docs/5.1/getting-started/javascript/#sanitizer)
            var myDefaultAllowList = bootstrap.Tooltip.Default.allowList
            myDefaultAllowList.table = []

            let vm = this;
            let actionLogId = 'actions-log-table' + vm.uuid;
            let popover_name = 'popover-'+ vm.uuid + '-logs';
            let popover_elem = $(vm.$refs.showActionBtn)[0]
            let my_content = '<table id="' + actionLogId + '" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%"></table>'
            let my_template = '<div class="popover ' + popover_name +'" role="tooltip"><div class="popover-arrow" style="top:110px;"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'

            new bootstrap.Popover(popover_elem, {
                html: true,
                content: my_content,
                template: my_template,
                title: 'Action logs',
                container: 'body',
                placement: 'right',
                trigger: "click",
            })
            popover_elem.addEventListener('inserted.bs.popover', () => {
                // when the popover template has been added to the DOM
                vm.actionsTable = $('#' + actionLogId).DataTable(this.actionsDtOptions);
                vm.actionsTable.on('draw', function () {
                    var popoverTriggerList = [].slice.call(document.querySelectorAll('#' + actionLogId + ' [data-bs-toggle="popover"]'))
                    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
                        return new bootstrap.Popover(popoverTriggerEl)
                    })
                })
            })
            popover_elem.addEventListener('shown.bs.popover', () => {
                // when the popover has been made visible to the user
                let el = vm.$refs.showActionBtn
                var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
                var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
                var diff = el_bounding_top - popover_bounding_top;
                var x = diff + 5;
                $('.'+popover_name).children('.arrow').css('top', x + 'px');
                $('#to').focus();
            })

        },
        initialisePopovers: function(){
            if (!this.popoversInitialised){
                console.log(this.uuid)
                this.initialiseActionLogs();
                this.initialiseCommLogs();
                this.popoversInitialised = true;
            }
        },
        addComm(){
            this.$refs.addComm.isModalOpen = true;
        }
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.initialisePopovers();
        });
        var addComms = document.getElementById('AddComms');
        addComms.addEventListener('shown.bs.modal', function (event) {
            alert('test');
            $('#to').focus();
        });
    }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}


</style>
