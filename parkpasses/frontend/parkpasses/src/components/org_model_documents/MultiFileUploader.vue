<template>
    <label :for="$attrs.name" class="col-form-label">{{ label }}</label>
    <input
        @change="processFiles($event.target.name, $event.target.files)"
        class="form-control"
        type="file"
        v-bind="$attrs"
        multiple
    >
</template>

<script>
export default {
    name: 'MultiFileUploader',
    inheritAttrs: false,
    props: {
        label: {
            type: String,
            required: true,
        },
        appLabel: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            count: 0
        }
    },
    methods: {
        processFiles: function(name, files) {
            for(let i=0;i<files.length;i++) {
                console.log(files[i].name);
            }
        }
    }
}
</script>
<style scoped>

</style>
