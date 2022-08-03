<template lang="html">
    <div>
        <div class="toggle_filters_wrapper">
            <div data-bs-toggle="collapse" :data-bs-target="'#' + target_elem_id" :id="button_elem_id" class="toggle_filters_button collapsed d-flex align-items-center" @click="toggleFiltersButtonClicked">
                <div class="me-auto">{{ component_title }}</div>
                <div class="">
                    <i :id="warning_icon_id" :title="warning_icon_title" class="fa-solid fa-exclamation-circle fa-2x filter_warning_icon"></i>
                </div>
                <div class="ml-2">
                    <i :id="chevron_elem_id" class="rotate_icon fa-solid fa-chevron-down"></i>
                </div>
            </div>

            <div class="collapse" :id="target_elem_id">
                <slot></slot>
            </div>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';

export default {
    name:"CollapsibleComponent",
    props: {
        component_title: {
            type: String,
            required: false,
            default: '',
        }
    },
    watch: {
        filters_expanded: function(){
            let chevron_icon = $('#' + this.chevron_elem_id)
            if (this.filters_expanded){
                chevron_icon.addClass('chev_rotated')
            } else {
                chevron_icon.removeClass('chev_rotated')
            }
        }
    },
    data:function () {
        return {
            target_elem_id: 'target_elem_' + uuid(),
            button_elem_id: 'button_elem_' + uuid(),
            chevron_elem_id: 'chevron_elem_' + uuid(),
            warning_icon_id: 'warning_elem_' + uuid(),
            warning_icon_title: '',
            display_icon: false,
            filters_expanded: null,
        }
    },
    methods: {
        toggleFiltersButtonClicked: function(e){
            // Bootstrap add a 'collapsed' class name to the element
            let filters_expanded_when_clicked = $('#' + this.button_elem_id).hasClass('collapsed')
            this.filters_expanded = !filters_expanded_when_clicked
        },
        showWarningIcon: function(show){
            let warning_icon = $('#' + this.warning_icon_id)
            if (show){
                warning_icon.css('opacity', 1)
                this.warning_icon_title = 'filter(s) applied'
            } else {
                warning_icon.css('opacity', 0)
                this.warning_icon_title = ''
            }
        },
    },
    mounted: function() {
        this.$nextTick(function(){
            this.$emit('created')
        })
    },
}
</script>

<style lang="css">
.toggle_filters_wrapper {
    background: #efefee;
    padding: 0.5em;
    display: grid;
}
.toggle_filters_button {
    cursor: pointer;
}
.filter_warning_icon {
    color: #ffc107;
    transition: 0.5s;
}
.rotate_icon {
    transition: 0.5s;
}
.chev_rotated {
    transform: rotate(180deg);
}
</style>
