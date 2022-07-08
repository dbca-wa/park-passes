<template>
    <div>
        <h1>Buy a Park Pass Voucher</h1>

        <p>
            Enter the details of the person receiving the voucher, the voucher details
            and your own details and we will send the couvher with your text to the
            recipient at the selected date.
        </p>

        <div>
            <form>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="amount" class="col-form-label">Voucher Amount</label>
                </div>
                <div class="col-auto">
                    <input type="number" id="amount" name="amount" v-model="voucher.amount" class="form-control" ref="amount" min="5" step="5" required="required" autofocus>
                </div>
            </div>
            <div class="row g-3 mb-2">
                <div class="col-md-4 mt-auto align-top">
                    <label for="recipientName" class="col-form-label">Recipient Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="recipientName" name="recipientName" v-model="voucher.recipient_name" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="recipientEmail" class="col-form-label">Recipient Email Address</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="recipientEmail" name="recipientEmail" v-model="voucher.recipient_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="confirmRecipientEmail" class="col-form-label">Confirm Recipient Email Address</label>
                </div>
                <div class="col-auto">
                    <input @change="validateConfirmRecipientEmail" type="email" id="confirmRecipientEmail" name="confirmRecipientEmail" v-model="confirm_recipient_email" class="form-control" required="required">
                    <div v-if="errors.validateConfirmRecipientEmailError" class="col-auto alert alert-danger ml-2"><i class="fa fa-exclamation-triangle" aria-hidden="true"></i> {{errors.validateConfirmRecipientEmailError}}</div>
                </div>
            </div>
            <div class="row g-3 align-top mb-2">
                <div class="col-md-4">
                    <label for="personalMessage" class="col-form-label">Message to Recipient</label>
                </div>
                <div class="col-auto">
                    <textarea id="personalMessage" name="personalMessage" v-model="voucher.personal_message" class="form-control personalMessage" required="required"></textarea>
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4 align-top">
                    <label for="datetimeToEmail" class="col-form-label">Date to Send the Voucher</label>
                </div>
                <div class="col-auto">
                    <input type="date" id="datetimeToEmail" name="datetimeToEmail" v-model="voucher.datetime_to_email" class="form-control" required="required" :min="startDate()" :max="endDate()">
                </div>
                <div class="col-auto">
                    <i class="fa-solid fa-circle-question icon-help" data-bs-toggle="tooltip" data-bs-placement="right" title="Leave as today to have the voucher sent immediately"></i>
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="firstName" class="col-form-label">Your First Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="firstName" name="firstName" v-model="voucher.purchaser_first_name" class="form-control" ref="firstName" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="lastName" class="col-form-label">Your Last Name</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="lastName" name="lastName" v-model="voucher.purchaser_last_name" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="email" class="col-form-label">Your Email Address</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="email" name="email" v-model="voucher.purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                </div>
                <div class="col-auto">
                    <input type="email" id="confirmEmail" name="confirmEmail" v-model="confirm_purchaser_email" class="form-control" required="required">
                </div>
            </div>
            <div class="row g-3 align-items-center mb-2">
                <div class="col-md-4">
                    <label for="postcode" class="col-form-label">Your Postcode</label>
                </div>
                <div class="col-auto">
                    <input type="text" id="postcode" name="postcode" class="form-control" pattern="[0-9]{4}">
                </div>
            </div>
            <div class="row g-3mb-2">
                <div class="col-md-4">
                    &nbsp;
                </div>
                <div class="col-auto">
                    <button @click="submitForm" class="btn btn-primary px-5" type="button">Pay</button>
                </div>
            </div>
            </form>
        </div>
    </div>
</template>

<script>
import { api_endpoints } from '@/utils/hooks'

export default {
    name: "PurchaseVoucher",
    data: function () {
        return {
            voucher: {
                amount: 5,
                datetime_to_email: this.startDate()
            },
            confirm_recipient_email: '',
            confirm_purchaser_email: '',
            errors: {
                validateConfirmRecipientEmailError: ""
            },
        };
    },
    components: {
        api_endpoints
    },
    computed: {

    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
        endDate: function () {
            let today = new Date();
            today.setFullYear(today.getFullYear() + 1);
            return today.toISOString().split('T')[0];
        },
        validateConfirmRecipientEmail: function () {
            if(this.voucher.recipient_email===this.confirm_recipient_email){
                this.errors.validateConfirmRecipientEmailError = '';
                return true;
            }
            this.errors.validateConfirmRecipientEmailError = 'Must match recipient email address';
            return false;
        },
        submitForm: function () {
            let vm = this;
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.voucher)
            };
            fetch(api_endpoints.createVoucher, requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.concessions = data.results
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
            console.log(this.voucher);
            return false;
        }
    },
    created: function () {

    },
    mounted: function () {
        this.$refs.amount.focus();
    }
};
</script>

<style scoped>
    .personalMessage{
        width:275px;
        height:200px;
    }
</style>
