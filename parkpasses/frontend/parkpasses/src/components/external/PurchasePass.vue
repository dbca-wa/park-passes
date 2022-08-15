<template>
        <div>
            <div v-if="!passType" class="d-flex justify-content-center mt-5">
                <div v-show="!passType" class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-if="systemErrorMessage" class="alert alert-danger" role="alert">
                {{ systemErrorMessage }}
            </div>

            <div v-show="passType && !systemErrorMessage">
                <div v-if="passType">
                    <h1>Buy {{indefiniteArticle}} {{passType.display_name}}</h1>
                </div>

                <div v-if="passType" v-html="passType.description"></div>

                <div>
                    <form @submit.prevent="validateForm" @keydown.enter="$event.preventDefault()" class="needs-validation" novalidate>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="firstName" class="col-form-label">First Name</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="firstName" name="firstName" v-model="pass.first_name" class="form-control" ref="firstName" required="required" autofocus>
                                <div class="invalid-feedback">
                                    Please enter your first name.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="lastName" class="col-form-label">Last Name</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="lastName" name="lastName" v-model="pass.last_name" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter your last name.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="email" class="col-form-label">Your Email Address</label>
                            </div>
                            <div class="col-auto">
                                <input type="email" id="email" name="email" v-model="pass.email" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid email address.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="confirmEmail" class="col-form-label">Confirm Your Email</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateConfirmEmail" type="email" id="confirmEmail" name="confirmEmail" v-model="confirmEmail" ref="confirmEmail" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please make sure your confirmation email matches your email.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="mobile" class="col-form-label">Mobile Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="tel" id="mobile" name="mobile" v-model="pass.mobile" class="form-control" pattern="[0-9]{4}[0-9]{3}[0-9]{3}" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid mobile phone number.
                                </div>
                            </div>
                        </div>
                        <div v-if="isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="driversLicenceNumber" class="col-form-label">Driver's Licence Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="tel" id="driversLicenceNumber" name="driversLicenceNumber" v-model="pass.drivers_licence_number" class="form-control" pattern="[a-zA-Z0-9]{8}" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid driver's licence number.
                                </div>
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="company" class="col-form-label">Company</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="company" name="company" v-model="pass.company" class="form-control">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="address" class="col-form-label">Address</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="address" name="address" v-model="pass.address" class="form-control" required="required">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="suburb" class="col-form-label">Town / Suburb</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="suburb" name="suburb" v-model="pass.suburb" class="form-control" required="required">
                            </div>
                        </div>
                        <div v-if="isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="state" class="col-form-label">State</label>
                            </div>
                            <div class="col-auto">
                                <select id="state" name="state" v-model="pass.state" class="form-select" required="required">
                                    <option value="WA" selected="selected">Western Australia</option>
                                    <option value="NSW">New South Wales</option>
                                    <option value="VIC">Victoria</option>
                                    <option value="QLD">Queensland</option>
                                    <option value="SA">South Australia</option>
                                    <option value="ACT">Australian Capital Territory</option>
                                    <option value="TAS">Tasmania</option>
                                    <option value="NT">Northern Territory</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="isAnnualLocalPass || isGoldStarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="postcode" class="col-form-label">Your Postcode</label>
                            </div>
                            <div class="col-auto">
                                <input v-if="isAnnualLocalPass" @keyup="validatePostcode" @change="validatePostcode" type="text" id="postcode" name="postcode" ref="postcode" v-model="pass.postcode" class="form-control" pattern="6[0-9]{3}" required="required" minlength="4" maxlength="4">
                                <input v-else type="text" id="postcode" name="postcode" ref="postcode" v-model="pass.postcode" class="form-control" pattern="[0-9]{4}" required="required" minlength="4" maxlength="4">
                                <div v-if="!noParkForPostcodeError" class="invalid-feedback">
                                    Please enter a valid postcode.
                                </div>
                                <div v-else="noParkForPostcodeError" class="org-error-message">
                                    {{noParkForPostcodeError}}
                                </div>
                                <span v-if="loadingParkGroups" class="spinner-border-sm org-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </span>
                            </div>
                        </div>
                        <div v-if="parkGroups && parkGroups.length && pass.park_group" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="parkGroup" class="col-form-label">Park Group</label>
                            </div>
                            <div class="col-auto">
                                <select v-if="parkGroups.length>1" @change="updateParkGroup" v-model="pass.park_group.id" ref="parkGroup" id="parkGroup" name="parkGroup" class="form-select" aria-label="Park Group" required="required">
                                    <option v-for="parkGroup in parkGroups" :value="parkGroup.id" :key="parkGroup.id">{{parkGroup.name}}</option>
                                </select>
                                <span v-else>{{pass.park_group.name}}</span>
                            </div>
                        </div>
                        <div v-if="showParksList" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="parkGroup" class="col-form-label">Parks Included</label>
                            </div>
                            <div class="col-auto">
                                <ul class="parks-list">
                                    <li v-for="park in pass.park_group.parks" class="park"><span class="badge">{{ park.name }}</span></li>
                                </ul>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="concession" class="col-form-label">Elibible for Concession</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    <input @change="resetPrice" class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="concession" name="concession" v-model="eligibleForConcession">
                                </div>
                            </div>
                        </div>
                        <div v-if="eligibleForConcession" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="postcode" class="col-form-label">Concession Type</label>
                            </div>
                            <div class="col-auto">
                                <select @change="updateConcessionDiscount" id="concessionType" name="concessionType" v-model="pass.concession_type" class="form-select" aria-label="Concession Type" required="required">
                                    <option disabled value="0" selected>Select Your Concession Type</option>
                                    <option v-for="concession in concessions" :value="concession.id" :key="concession.id">{{concession.concession_type}} ({{concession.discount_percentage}}% Discount)</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="eligibleForConcession" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="concessionCardNumber" class="col-form-label">Concession Card Number</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="concessionCardNumber" name="concessionCardNumber" class="form-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a concession card number.
                                </div>
                            </div>
                        </div>
                        <div v-if="passOptions" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Duration
                            </div>
                            <div class="col-auto">
                                <select v-if="passOptions.length>1" @change="updatePrice" v-model="pass.option.id" ref="passOption" id="passOption" name="passOption" class="form-select" aria-label="Pass Option" required="required">
                                    <option v-for="passOption in passOptions" :value="passOption.id" :key="passOption.id">{{passOption.name}}</option>
                                </select>
                                <span v-else>{{pass.option.name}}</span>
                            </div>
                        </div>
                        <div v-if="totalPrice" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                Price
                            </div>
                            <div class="col-auto lead">
                                <strong>${{ totalPrice }}</strong>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="startDate" class="col-form-label">Start Date for Pass</label>
                            </div>
                            <div class="col-auto">
                                <input type="date" id="startDate" name="startDate" v-model="pass.datetime_start" class="form-control" required="required" :min="startDate()">
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="renewAutomatically" class="col-form-label">Automatically Renew at Expiry?</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    <input class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="renewAutomatically" name="renewAutomatically" v-model="pass.renew_automatically">
                                </div>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistrationNumbersKnown" class="col-form-label">Vehicle Registration Number<span v-if="isHolidayPass">s</span> Known</label>
                            </div>
                            <div class="col-auto">
                                <div class="form-switch">
                                    {{isPinjarPass}}<input class="form-check-input pl-2 org-form-switch-primary" type="checkbox" id="vehicleRegistrationNumbersKnown" name="vehicleRegistrationNumbersKnown" v-model="vehicleRegistrationNumbersKnown">
                                </div>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass && vehicleRegistrationNumbersKnown" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistration1" class="col-form-label">Vehicle Registration<span v-if="vehicleInputs>1"> 1</span></label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="vehicleRegistration1" name="vehicleRegistration1" v-model="pass.vehicle_registration_1" class="form-control short-control" required="required" pattern="[a-zA-Z0-9]+" maxlength="9">
                                <div class="invalid-feedback">
                                    Please enter a valid vehicle registration .
                                </div>
                            </div>
                            <div v-if="isHolidayPass" class="col-auto">
                                <button @click="toggleExtraVehicle" class="btn licensing-btn-primary">{{extraVehicleText}}</button>
                            </div>
                        </div>
                        <div v-if="!isPinjarPass && vehicleRegistrationNumbersKnown && vehicleInputs>1" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="vehicleRegistration2" class="col-form-label">Vehicle Registration 2</label>
                            </div>
                            <div class="col-auto">
                                <input type="text" id="vehicleRegistration2" name="vehicleRegistration2" v-model="pass.vehicle_registration_2" class="form-control short-control" required="required">
                                <div class="invalid-feedback">
                                    Please enter a valid vehicle registration .
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="discountCode" class="col-form-label">Discount Code</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateDiscountCode" v-model="pass.discount_code" type="text" id="discountCode" name="discountCode" ref="discountCode" class="form-control short-control" :class="{'is-invalid' : discountCodeError}" minlength="8" maxlength="8">
                                <div class="invalid-feedback">
                                    This discount code is not valid.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="voucherCode" class="col-form-label">Voucher Code</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateVoucherCode" @keyup="focusVoucherPin" v-model="pass.voucher_code" type="text" id="voucherCode" name="voucherCode" ref="voucherCode" class="form-control short-control" :class="{'is-invalid' : voucherCodeError}" minlength="8" maxlength="8">
                                <div class="invalid-feedback">
                                    This voucher code is not valid.
                                </div>
                            </div>
                        </div>
                        <div v-if="pass.voucher_code.length==8 && validateVoucherCode" class="row g-1 align-top mb-2">
                            <div class="col-md-4">
                                <label for="voucherPin" class="col-form-label">Voucher Pin</label>
                            </div>
                            <div class="col-auto">
                                <input @change="validateVoucherPin" v-model="pass.voucher_pin" type="text" id="voucherPin" name="voucherPin" ref="voucherPin" class="form-control pin-control" minlength="6" maxlength="6">
                                <div class="invalid-feedback">
                                    This voucher pin is not valid.
                                </div>
                            </div>
                        </div>
                        <div class="row g-1 mb-2">
                            <div class="col-md-4">
                                &nbsp;
                            </div>
                            <div class="col-auto">
                                <button class="btn licensing-btn-primary px-5" type="submit">Next</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
</template>

<script>
import { apiEndpoints } from '@/utils/hooks'
import { constants } from '@/utils/hooks'
import { helpers } from '@/utils/hooks'
import { useStore } from '@/stores/state'

export default {
    name: "PurchasePass",
    props: {
        passTypeId: {
            type: Number
        }
    },
    data: function () {
        return {
            store: useStore(),
            pass: {
                first_name: '',
                concession_type: 0,
                datetime_start: this.startDate(),
                discount_code: '',
                voucher_code: '',
                voucher_pin: '',
                state: 'WA',
                park_group: null
            },
            passType: null,
            passOptions: null,
            passOptionsLength: null,
            passPrice: '',
            parkGroups: [],
            loadingParkGroups: false,
            concessionDiscountPercentage: 0,
            concessions: [],
            confirmEmail: '',
            eligibleForConcession: false,
            vehicleRegistrationNumbersKnown: true,
            extraVehicle: false,
            vehicleInputs: 1,
            extraVehicleText: 'Add a second vehicle',
            discountCodeError: '',
            voucherCodeError: '',
            voucherPinError: '',
            systemErrorMessage: null,
            noParkForPostcodeError: '',
        };
    },
    components: {
        apiEndpoints,
        constants,
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
        isHolidayPass() {
            if(!this.passType){
                return false;
            }
            return ('HOLIDAY_PASS'==this.passType.name ? true : false)
        },
        isAnnualLocalPass() {
            if(!this.passType){
                return false;
            }
            return ('ANNUAL_LOCAL_PASS'==this.passType.name ? true : false)
        },
        isGoldStarPass() {
            if(!this.passType){
                return false;
            }
            return ('GOLD_STAR'==this.passType.name ? true : false)
        },
        indefiniteArticle() {
            return ('A'==this.passType.display_name.substring(0,1) ? 'an' : 'a' )
        },
        showParksList() {
            if(this.pass.park_group){
                const parksInParkGroupName = this.pass.park_group.name.split('/').length;
                if(this.pass.park_group.parks.length > parksInParkGroupName){
                    return true;
                }
            }
            return false;
        },
        isPinjarPass() {
            if(!this.passType){
                return false;
            }
            return ('PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS'==this.passType.name ? true : false)
        }
    },
    methods: {
        startDate: function () {
            const today = new Date();
            return today.toISOString().split('T')[0];
        },
        fetchConcessions: function () {
            let vm = this;
            fetch(apiEndpoints.concessions)
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
        },
        fetchPassType: function () {
            let vm = this;
            fetch(apiEndpoints.passType(vm.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                vm.passType = data
                vm.$nextTick(() => {
                    if(!vm.pass.first_name.length){
                        vm.$refs.firstName.focus();
                    } else {
                        vm.$refs.confirmEmail.focus();
                    }
                });
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        fetchPassOptions: function () {
            let vm = this;
            fetch(apiEndpoints.passOptions(vm.passTypeId))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }
                if(data.results.length > 0) {
                    vm.passOptions = data.results
                    vm.pass.option = Object.assign({}, vm.passOptions[0]);
                    vm.passPrice = vm.passOptions[0].price
                } else {
                    this.systemErrorMessage = constants.ERRORS.CRITICAL;
                    console.error(`SYSTEM ERROR: Unable to load options for pass type id: ${vm.passTypeId}`);
                }
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        fetchParkGroups: function () {
            let vm = this;
            vm.loadingParkGroups = true;
            fetch(apiEndpoints.parkGroupsForPostcode(vm.pass.postcode))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error)
                    return Promise.reject(error);
                }

                if (data.results.length >= 1) {
                    vm.parkGroups = data.results
                    console.log(vm.parkGroups);
                    vm.pass.park_group = Object.assign({}, vm.parkGroups[0]);
                    vm.$nextTick( function() {
                        if(vm.parkGroups.length>1){
                            vm.$refs.parkGroup.focus();
                        }
                    });
                } else {
                    console.log('Something goes here.')
                    vm.noParkForPostcodeError = "Unfortunately there are no local parks for your postcode.";
                    this.$refs.postcode.setCustomValidity("Invalid field.");
                }
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            }).finally(() => (this.loadingParkGroups = false));
        },
        updatePrice: function (event) {
            this.passPrice = this.passOptions[event.target.selectedIndex].price
        },
        updateParkGroup: function (event) {
            this.pass.park_group = {...this.parkGroups[event.target.selectedIndex]};
        },
        resetPrice: function () {
            if(!this.eligibleForConcession){
                this.concessionDiscountPercentage = 0.00
                if(this.passOptions.length>1){
                    this.passPrice = this.passOptions[this.$refs.passOption.selectedIndex].price
                } else {
                    this.passPrice = this.passOptions[0].price
                }

            } else {
                console.log('happening');
                this.pass.concession_type = 0;
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
        toggleExtraVehicle: function (e) {
            e.preventDefault();
            this.extraVehicle = !this.extraVehicle;
            if(this.extraVehicle) {
                this.vehicleInputs = 2;
                this.extraVehicleText = 'Remove second vehicle';
            } else {
                this.vehicleInputs = 1;
                this.extraVehicleText = 'Add a second vehicle';
            }
        },
        validateConfirmEmail: function () {
            if(this.confirmEmail!=this.pass.email){
                this.$refs.confirmEmail.setCustomValidity("Invalid field.");
                return false;
            } else {
                this.$refs.confirmEmail.setCustomValidity("");
            }
        },
        validateDiscountCode: function () {
            if(this.pass.discount_code.length && (8!=this.pass.discount_code.length)){
                this.$refs.discountCode.setCustomValidity("Invalid field.");
                return false;
            } else {
                this.$refs.discountCode.setCustomValidity("");
            }
        },
        validateVoucherCode: function () {
            console.log('this.pass.voucher_code.length = ' + this.pass.voucher_code.length)
            if(this.pass.voucher_code.length && 8!=this.pass.voucher_code.length){
                console.log('voucher code is invalid')
                this.$refs.voucherCode.setCustomValidity("Invalid field.");
                return false;
            } else {
                console.log('voucher code is not invalid')
                this.$refs.voucherCode.setCustomValidity("");
                return true;
            }
        },
        validatePostcode: function () {
            /*
                This validation only occurs for local park passes (due to logic in the template)
            */
            let vm = this;
            vm.noParkForPostcodeError = '';
            if(vm.pass.postcode.length==4){
                /*
                const firstNumber = vm.pass.postcode.substring(0,1);
                if('6'==firstNumber){

                } else {
                    vm.$refs.postcode.setCustomValidity("Invalid field.");
                    vm.parkGroups = []
                    vm.pass.park_group = null
                    return false;
                }*/
                fetch(apiEndpoints.isPostcodeValid(vm.pass.postcode))
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error);
                        return Promise.reject(error);
                    }
                    const isPostcodeValid = data.is_postcode_valid
                    console.log('isPostcodeValid = ' + isPostcodeValid)
                    if(!isPostcodeValid){
                        vm.$refs.postcode.setCustomValidity("Invalid field.");
                        vm.parkGroups = []
                        vm.pass.park_group = null
                        return false;
                    }
                    vm.$refs.postcode.setCustomValidity("");
                    vm.fetchParkGroups();
                    return true;
                })
                .catch(error => {
                    this.systemErrorMessage = "ERROR: Please try again in an hour.";
                    console.error("There was an error!", error);
                });
            } else {
                vm.$refs.postcode.setCustomValidity("Invalid field.");
                vm.parkGroups = []
                vm.pass.park_group = null
                return false;
            }
        },
        focusVoucherPin: function() {
            if(this.pass.voucher_code.length==8){
                this.$nextTick(() => {
                     this.$refs.voucherPin.focus();
                });
            }
        },
        validateVoucherPin: function () {
            console.log('this.pass.voucher_pin.length = ' + this.pass.voucher_pin.length)
            if(6!=this.pass.voucher_pin.length){
                console.log('Pin is not valid.')
                this.$refs.voucherPin.setCustomValidity("Invalid field.");
                return false;
            } else {
                console.log('Pin is valid.')
                if(this.pass.voucher_pin.length && !/^\d+$/.test(this.pass.voucher_pin)){
                    this.$refs.voucherPin.setCustomValidity("Invalid field.");
                    return false;
                } else {
                    this.$refs.voucherPin.setCustomValidity("");
                }
            }

        },
        validateVoucherCodeBackend: function () {
            let vm = this;
            fetch(apiEndpoints.isVoucherValid(vm.pass.recipient_email, vm.pass.voucher_code, vm.pass.voucher_pin))
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                const is_voucher_code_valid_for_user = data
                console.log('is_voucher_code_valid_for_user = ' + is_voucher_code_valid_for_user)
                if(!is_voucher_code_valid_for_user){
                    this.$refs.voucherCode.setCustomValidity("Invalid field.");
                } else {
                    this.$refs.voucherCode.setCustomValidity("");
                }
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
        },
        submitForm: function() {
            let vm = this;
            vm.pass.csrfmiddlewaretoken = helpers.getCookie('csrftoken');
            let start_date = new Date(vm.pass.datetime_start)
            vm.pass.datetime_start = start_date.toISOString();
            console.log('vm.pass.datetime_start = ' + vm.pass.datetime_start);
            vm.pass.option = vm.pass.option.id;
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pass)
            };
            fetch(apiEndpoints.createPass, requestOptions)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    const error = (data && data.message) || response.statusText;
                    console.log(error);
                    return Promise.reject(error);
                }
                // Do something after adding the voucher to the database and the users cart
                window.location.href = 'checkout/';
            })
            .catch(error => {
                this.systemErrorMessage = "ERROR: Please try again in an hour.";
                console.error("There was an error!", error);
            });
            console.log(this.voucher);
            return false;
        },
        validateForm: function () {
            let vm = this;
            var forms = document.querySelectorAll('.needs-validation')

            this.validateDiscountCode();
            this.validateConfirmEmail();
            let voucherCodeValid = this.validateVoucherCode();
            let voucherPinValid = false;
            if(this.pass.voucher_code.length && voucherCodeValid){
                voucherPinValid = this.validateVoucherPin();
            }

            if(voucherCodeValid && voucherPinValid){
                this.validateVoucherCodeBackend();
            }

            Array.prototype.slice.call(forms)
            .forEach(function (form) {
                if(form.checkValidity()){
                    //Call some api with the valid data.
                    vm.submitForm();
                } else {
                    form.classList.add('was-validated');
                    //app.getElement('.invalid-feedback:first').focus();
                    console.log($(".invalid-feedback:first"));
                    $(".invalid-feedback:visible:first").siblings('input').focus();
                }

            });

            console.log(this.pass);
            return false;
        }
    },
    created: function () {
        this.fetchPassType();
        this.fetchConcessions();
        this.fetchPassOptions();
    },
    mounted: function () {
        if(this.store.userData.user){
            this.pass.email = this.store.userData.user.email
            this.pass.first_name = this.store.userData.user.first_name
            this.pass.last_name = this.store.userData.user.last_name
            this.$refs.confirmEmail.focus();
        }
    }
};
</script>

<style scoped>

    .form-control.no-validate:valid {
        border-color: #ced4da;
        padding-right: .75rem;
        background: none;
    }
    .short-control{
        width:180px;
    }
    .pin-control{
        width:120px;
    }
    .parks-list{
        max-width:400px;
        margin:0;
        padding:0;
    }
    .parks-list li {
        list-style-type: none;
        display:inline-flex;
        margin-right:3px;
    }

    .parks-list li span.badge {
        color: #fff;
        background-color: #337ab7;
    }
</style>
