module.exports = {
    GST:                                    10,
    PARKPASSES_APP_LABEL:                   'parkpasses',
    PARKPASSES_MODELS_USERACTION:           'useraction',
    PARKPASSES_MODELS_PASS:                 'pass',
    PARKPASSES_MODELS_DISCOUNT_CODE_BATCH:  'discountcodebatch',
    PARKPASSES_MODELS_PRICING_WINDOW:       'passtypepricingwindow',

    PARKAPSSES_DEFAULT_PRICING_WINDOW_NAME: 'Default',

    TITLE_SUFFIX: ' - Park Passes - Department of Biodiversity, Conservation and Attractions',

    DAY_ENTRY_PASS_NAME: 'DAY_ENTRY_PASS',
    HOLIDAY_PASS_NAME: 'HOLIDAY_PASS',
    PINJAR_PASS_NAME: 'PINJAR_OFF_ROAD_VEHICLE_AREA_ANNUAL_PASS',
    PERSONNEL_PASS_NAME: 'PERSONNEL_PASS',

    DEFAULT_SOLD_VIA: 'DBCA Website',

    PASS_PROCESSING_STATUS_CANCELLED: 'CA',
    PASS_STATUS_EXPIRED: 'Expired',
    DISCOUNT_CODE_BATCH_STATUS_INVALIDATED: 'Invalidated',

    DATATABLE_PROCESSING_HTML: '<div class="spinner-border org-primary align-items-center" style="width: 3rem; height: 3rem; margin-top:45px;" role="status"><span class="visually-hidden">Loading...</span></div>',

    ERRORS: {
        NETWORK: 'NETWORK ERROR: Make sure your internet connection is working and try again.',
        // The critical error will be shown on the client side when a critical error
        // has occured on the backend and needs the attention of the system admins.
        CRITICAL: 'SYSTEM ERROR: Our System Administrators have been notified. Please try again in an hour.'
    }
}
