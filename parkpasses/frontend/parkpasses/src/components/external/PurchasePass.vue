<template>
    <div class="container" id="shopHome">
        <div class="row">
            <div class="col-4">

            </div>
            <div class="col">
                <h1 v-if="passType">Buy a {{passType.display_name}}</h1>
                <p>
                    Add a description field to the db so we can display this info dynamically:
                </p>

                <p>
                    An annual all parks pass gives you unlimited access to all national parks
                    in Western Australia for one year. Concession disocunts are available.
                </p>

                <div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="firstName" class="col-form-label">First Name</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="firstName" name="firstName" class="form-control" ref="firstName" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="lastName" class="col-form-label">Last Name</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="lastName" name="lastName" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="email" class="col-form-label">Your Email Address</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="email" name="email" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                        </div>
                        <div class="col-auto">
                            <input type="email" id="confirmEmail" name="confirmEmail" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="mobile" class="col-form-label">Mobile Number</label>
                        </div>
                        <div class="col-auto">
                            <input type="tel" id="mobile" name="mobile" class="form-control" pattern="[0-9]{4} [0-9]{3} [0-9]{3}" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="postcode" class="col-form-label">Your Postcode</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="postcode" name="postcode" class="form-control" pattern="[0-9]{4}" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="concession" class="col-form-label">Elibible for Concession</label>
                        </div>
                        <div class="col-auto">
                            <div class="form-switch">
                                <input @change="resetPrice" class="form-check-input pl-2" type="checkbox" id="concession" name="concession" v-model="eligibleForConcession">
                            </div>
                        </div>
                    </div>
                    <div v-if="eligibleForConcession" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="postcode" class="col-form-label">Concession Type</label>
                        </div>
                        <div class="col-auto">
                            <select @change="updateConcessionDiscount" id="concessionType" name="concessionType" class="form-select" aria-label="Concession Type" required="required">
                                <option selected>Select Your Concession Type</option>
                                <option v-for="concession in concessions" value="concession.id">{{concession.concession_type}} ({{concession.discount_percentage}}% Discount)</option>
                            </select>
                        </div>
                    </div>
                    <div v-if="eligibleForConcession" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="concessionCardNumber" class="col-form-label">Concession Card Number</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="concessionCardNumber" name="concessionCardNumber" class="form-control" required="required">
                        </div>
                    </div>
                    <div v-if="passOptions" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            Duration
                        </div>
                        <div class="col-auto">
                            <select v-if="passOptions.length>1" @change="updatePrice" v-model="passOption" ref="passOption" id="passOption" name="passOption" class="form-select" aria-label="Pass Option" required="required">
                                <option v-for="passOption in passOptions" :value="passOption.id">{{passOption.name}}</option>
                            </select>
                            <span v-else>{{passOption.name}}</span>
                        </div>
                    </div>
                    <div v-if="totalPrice" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            Price
                        </div>
                        <div class="col-auto lead">
                            <strong>${{ totalPrice }}</strong>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="startDate" class="col-form-label">Start Date for Pass</label>
                        </div>
                        <div class="col-auto">
                            <input type="date" id="startDate" name="startDate" class="form-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="renewAutomatically" class="col-form-label">Automatically Renew at Expiry?</label>
                        </div>
                        <div class="col-auto">
                            <div class="form-switch">
                                <input class="form-check-input pl-2" type="checkbox" id="renewAutomatically" name="renewAutomatically">
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="vehicleRegistrationNumbersKnown" class="col-form-label">Vehicle Registration Number<span v-if="canAddAnotherVehicle">s</span> Known</label>
                        </div>
                        <div class="col-auto">
                            <div class="form-switch">
                                <input class="form-check-input pl-2" type="checkbox" id="vehicleRegistrationNumbersKnown" name="vehicleRegistrationNumbersKnown" v-model="vehicleRegistrationNumbersKnown">
                            </div>
                        </div>
                    </div>
                    <div v-if="vehicleRegistrationNumbersKnown" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="vehicleRegistration" class="col-form-label">Vehicle Registration<span v-if="vehicleInputs>1"> 1</span></label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="vehicleRegistration" name="vehicleRegistration" class="form-control short-control" required="required" maxlength="8">
                        </div>
                        <div v-if="canAddAnotherVehicle" class="col-auto">
                            <button @click="toggleExtraVehicle" class="btn btn-primary">{{extraVehicleText}}</button>
                        </div>
                    </div>
                    <div v-if="vehicleRegistrationNumbersKnown && vehicleInputs>1" class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="vehicleRegistration" class="col-form-label">Vehicle Registration 2</label>
                        </div>
                        <div class="col-auto">
                            <input type="text" id="vehicleRegistration" name="vehicleRegistration" class="form-control short-control" required="required">
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="discountCode" class="col-form-label">Discount Code</label>
                        </div>
                        <div class="col-auto">
                            <input @change="validateDiscountCode" v-model="discountCode" type="text" id="discountCode" name="discountCode" class="form-control short-control" maxlength="8">
                            <span class="text-danger">{{discountCodeError}}</span>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="voucherCode" class="col-form-label">Voucher Code</label>
                        </div>
                        <div class="col-auto">
                            <input @change="validateVoucherCode" v-model="voucherCode" type="text" id="voucherCode" name="voucherCode" class="form-control short-control" maxlength="8">
                            <span class="text-danger">{{voucherCodeError}}</span>
                        </div>
                    </div>
                    <div class="row g-3 align-items-center mb-2">
                        <div class="col-md-4">
                            <label for="voucherPin" class="col-form-label">Voucher Pin</label>
                        </div>
                        <div class="col-auto">
                            <input @change="validateVoucherPin" v-model="voucherPin" type="text" id="voucherPin" name="voucherPin" class="form-control pin-control" maxlength="6">
                            <span class="text-danger">{{voucherPinError}}</span>
                        </div>
                    </div>
                    <div class="row g-3mb-2">
                        <div class="col-md-4">
                            &nbsp;
                        </div>
                        <div class="col-auto">
                            <button @click="submitForm" class="btn btn-primary px-5" type="submit">Pay</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints } from '@/utils/hooks'

export default {
    name: "PurchasePass",
    data: function () {
        return {
            passType: null,
            passOptions: null,
            passOption: null,
            passOptionsLength: null,
            passPrice: '',
            concessionDiscountPercentage: 0,
            concessions: [],
            eligibleForConcession: false,
            vehicleRegistrationNumbersKnown: true,
            extraVehicle: false,
            vehicleInputs: 1,
            extraVehicleText: 'Add a second vehicle',
            discountCode: '',
            discountCodeError: '',
            voucherCode: '',
            voucherPin: '',
            voucherCodeError: '',
            voucherPinError: '',
            errorMessage: null
        };
    },
    computed: {
        totalPrice() {
            let totalPrice = 0.00;
            if(!this.eligibleForConcession){
                return this.passPrice;
            }
            totalPrice = this.passPrice - ((this.concessionDiscountPercentage / 100) * this.passPrice);
            return totalPrice.toFixed(2);
        },
        canAddAnotherVehicle() {
            if(!this.passType){
                return false;
            }
            return ('HOLIDAY_PASS'==this.passType.name ? false : true)
        },
    },
    methods: {
        fetchConcessions: function () {
            let vm = this;
            fetch(api_endpoints.concessions)
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
                this.errorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        fetchPassType: function () {
            let vm = this;
            fetch(api_endpoints.passType(vm.$route.params.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.passType = data
            })
            .catch(error => {
                this.errorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        fetchPassOptions: function () {
            let vm = this;
            fetch(api_endpoints.passOptions(vm.$route.params.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.passOptions = data.results
                vm.passOption = vm.passOptions[0].id
                vm.passPrice = vm.passOptions[0].price
            })
            .catch(error => {
                this.errorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        updatePrice: function (event) {
            this.passPrice = this.passOptions[event.target.selectedIndex].price
        },
        resetPrice: function () {
            if(!this.eligibleForConcession){
                this.concessionDiscountPercentage = 0.00
                this.passPrice = this.passOptions[this.$refs.passOption.selectedIndex].price
            }
        },
        updateConcessionDiscount: function (event) {
            if(!this.eligibleForConcession){
                this.concessionDiscountPercentage = 0.00;
            } else {
                if(0==event.target.selectedIndex){
                    this.concessionDiscountPercentage = 0.00;
                } else {
                    this.concessionDiscountPercentage = this.concessions[event.target.selectedIndex-1].discount_percentage
                }
            }
        },
        toggleExtraVehicle: function () {
            this.extraVehicle = !this.extraVehicle;
            if(this.extraVehicle) {
                this.vehicleInputs = 2;
                this.extraVehicleText = 'Remove second vehicle';
            } else {
                this.vehicleInputs = 1;
                this.extraVehicleText = 'Add a second vehicle';
            }
        },
        validateDiscountCode: function () {
            console.log('this.discountCode.length = ' + this.discountCode.length)
            if(8!=this.discountCode.length){
                this.discountCodeError = 'Discount Code must be 8 characters long.'
            } else {
                this.discountCodeError = ''
            }
        },
        validateVoucherCode: function () {
            console.log('this.voucherCode.length = ' + this.voucherCode.length)
            if(8!=this.voucherCode.length){
                this.voucherCodeError = 'Voucher Code must be 8 characters long.'
                return false
            } else {
                this.voucherCodeError = ''
            }
        },
        validateVoucherPin: function () {
            console.log('this.voucherPin.length = ' + this.voucherPin.length)
            if(6!=this.voucherPin.length){
                this.voucherPinError = 'Voucher Pin must be 6 characters long.'
                return false
            } else {
                this.voucherPinError = ''
            }
            if(!/^\d+$/.test(this.voucherPin)){
                this.voucherPinError = 'Voucher Pin must contain only numbers.'
                return false
            } else {
                this.voucherPinError = ''
            }
            if(this.validateVoucherCode()){
                this.validateVoucher()
            }
        },
        validateVoucher: function () {
            let vm = this;
            fetch(api_endpoints.passOptions(vm.$route.params.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.passOptions = data.results
                vm.passOption = vm.passOptions[0].id
                vm.passPrice = vm.passOptions[0].price
            })
            .catch(error => {
                this.errorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        }
    },
    created: function () {
        this.fetchPassType();
        this.fetchConcessions();
        this.fetchPassOptions();
    },
    mounted: function () {
        this.$refs.firstName.focus();
    }
};
</script>

<style scoped>
    .short-control{
        width:140px;
    }
    .pin-control{
        width:80px;
    }
</style>
