<template>
    <div>
        <input type="range" :min="min" :max="max" v-model="my_value" class="slider" :id="my_id">
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';

export default {
    name: 'RangeSlider',
    props: {
        min: {
            type: Number,
            default: 0,
        },
        max: {
            type: Number,
            default: 100,
        },
        value:{
            type: Number,
            required: false,
            default: 50,
            validator: function(val) {
                return true
            }
        },
    },
    watch: {
        my_value: function(){
            this.$emit('valueChanged', this.my_value)
        }
    },
    data: function() {
        return {
            my_id: uuid(),
            my_value: null,
        }
    },
    created: function(){
        this.my_value = this.value
    },
    mounted: function(){

    },
    methods: {

    }
}
</script>

<style scoped>
</style>

