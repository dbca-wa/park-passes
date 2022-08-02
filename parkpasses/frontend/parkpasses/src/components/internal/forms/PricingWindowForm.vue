<template>
    <div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Add a New Pricing Window</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
            <form>
                <div class="mb-3">
                    <label for="recipient-name" class="col-form-label">Recipient:</label>
                    <select class="form-control" v-model="pricing_window.pass_type">
                        <option value="" selected="selected" disabled="disabled">Select a Pass Type</option>
                        <option v-for="passType in passTypesDistinct" :value="passType.code">{{ passType.description }}</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="name" class="col-form-label">Name:</label>
                    <input type="text" class="form-control" id="name" name="name" v-model="pricing_window.name" />
                </div>
                <div class="mb-3">
                    <label for="datetimeStart" class="col-form-label">Date Start</label>
                    <input type="date" id="datetimeStart" name="datetimeStart" v-model="pricing_window.datetime_start" class="form-control" required="required" :min="startDate()">
                </div>
                <div class="mb-3">
                    <label for="datetimeExpiry" class="col-form-label">Date End</label>
                    <input type="date" id="datetimeExpiry" name="datetimeExpiry" v-model="pricing_window.datetime_expiry" class="form-control" required="required" :min="minEndDate">
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary">Submit</button>
        </div>
        </div>
    </div>
    </div>
</template>

<script>
export default {
    name: 'PricingWindowForm',
    props: {
        passTypesDistinct: Array,

    },
    data(){
        return {
            pricing_window: {
                pass_type: '',
                name: '',
                datetime_start: this.startDate(),
                datetime_expiry: '',
            }
        }
    },
    computed: {
        minEndDate: function() {
            let endDate = new Date(this.pricing_window.datetime_start);
            endDate.setDate(endDate.getDate() + 1);
            return endDate;
        }
    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
    }
}
</script>
