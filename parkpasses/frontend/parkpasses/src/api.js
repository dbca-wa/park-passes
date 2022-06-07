
module.exports = {
    proposals_paginated_list: '/api/proposal_paginated', // both for external and internal
    discard_proposal: function (id) {
        return `/api/proposal/${id}.json`;
    },
    application_types_dict:"/api/application_types_dict",
    application_statuses_dict:"/api/application_statuses_dict",
}
