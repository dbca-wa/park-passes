<template lang="html">
    <div>
        <div class="form-group">
            <!--label :id="id" for="label" class="inline" >{{ label }}</label-->
            <!--ckeditor v-model="detailsText" :config="editorConfig" :read-only="readonly" :name="name" :required="isRequired" ></ckeditor-->
            <ckeditor
            :editor="editor"
            v-model="detailsText"
            :config="editorConfig"
            :read-only="readonly"
            :name="name"
            :required="isRequired"
            />
        </div>
    </div>
</template>

<script>

/*
import CommentBlock from './comment_block.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
import { mapActions } from 'vuex';
*/

import ClassicEditor from '@ckeditor/ckeditor5-build-classic'

export default {
    //props:["type","name","id", "field_data","isRequired","help_text","label","readonly", "help_text_url", "can_view_richtext_src"],
    props:["id", "name", "proposalData", "isRequired", "label", "readonly", "can_view_richtext_src"],
    //components: {CommentBlock, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        if (vm.can_view_richtext_src) {
            var remove_buttons = ''
	} else {
            var remove_buttons = 'Source,About'
	}

        return {
            /*
            editorConfig: {
                // The configuration of the editor.
                removeButtons: remove_buttons,

		// below line removes toolbar
                //toolbar: [],

                // remove bottom bar
                removePlugins: 'elementspath',
                resize_enabled: false,
            },
            */
            editorConfig: {
                language: 'en',
            },
            detailsText: '',
            editor: ClassicEditor,
        }
    },
    methods: {
        /*
        ...mapActions([
            'setFormValue',
        ]),
        */
    },
    computed: {
    },
    created: function() {
        if (this.proposalData) {
            this.detailsText = this.proposalData;
        }
    },
}
</script>

<style lang="css">
</style>
