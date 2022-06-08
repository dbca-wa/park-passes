module.exports = {
    formatError: function(err) {
        let returnStr = '';
        // object {}
        if (typeof(err.body) === 'object' && !err.body.hasOwnProperty('length')) {
            for (const key of Object.keys(err.body)) {
                returnStr += `${key}: ${err.body[key]} <br/>`;
            }
        // array
        } else if (typeof(err.body) === 'object') {
            returnStr = err.body[0];
        // string
        } else {
            returnStr = err.body;
        }
        return returnStr;
    },
  apiError: function ( resp ) {
    var error_str = '';
    if ( resp.status === 400 ) {
      try {
        obj = JSON.parse( resp.responseText );
        error_str = obj.non_field_errors[ 0 ].replace( /[\[\]"]/g, '' );
      }
      catch ( e ) {
        error_str = resp.responseText.replace( /[\[\]"]/g, '' );
      }
    }
    else if ( resp.status === 404 ) {
      error_str = 'The resource you are looking for does not exist.';
    }
    else {
      error_str = resp.responseText.replace( /[\[\]"]/g, '' );
    }
    return error_str;
  },
    apiVueResourceError: function(resp){
        console.log('in apiVueResourceError')
        console.log(resp)
        var error_str = '';
        var text = null;
        if (resp.status === 400) {
            if (Array.isArray(resp.body)){
                text = resp.body[0];
            }
            else if (typeof resp.body == 'object'){
                text = resp.body;
            }
            else{
                text = resp.body;
            }

            if (typeof text == 'object'){
                if (text.hasOwnProperty('non_field_errors')) {
                    error_str = text.non_field_errors[0].replace(/[\[\]"]/g, '');
                } else{
                    console.log('text')
                    console.log(text)
                    for (let key in text){
                        error_str += key + ': ' + text[key] + '<br/>'
                    }
                }
            }
            else{
                error_str = text.replace(/[\[\]"]/g,'');
                error_str = text.replace(/^['"](.*)['"]$/, '$1');
            }
        }
        else if ( resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        console.log('error_str')
        console.log(error_str)
        return error_str;
    },

  goBack: function ( vm ) {
    vm.$router.go( window.history.back() );
  },
  copyObject: function(obj){
        return JSON.parse(JSON.stringify(obj));
  },
  getCookie: function ( name ) {
    var value = null;
    if ( document.cookie && document.cookie !== '' ) {
      var cookies = document.cookie.split( ';' );
      for ( var i = 0; i < cookies.length; i++ ) {
        var cookie = cookies[ i ].trim();
        if ( cookie.substring( 0, name.length + 1 )
          .trim() === ( name + '=' ) ) {
          value = decodeURIComponent( cookie.substring( name.length + 1 ) );
          break;
        }
      }
    }
    return value;
  },
  namePopover: function ( $, vmDataTable ) {
    vmDataTable.on( 'mouseover', '.name_popover', function ( e ) {
      $( this )
        .popover( 'show' );
      $( this )
        .on( 'mouseout', function () {
          $( this )
            .popover( 'hide' );
        } );
    } );
  },
    add_endpoint_json: function ( string, addition ) {
        let res = string.split( ".json" )
        let endpoint = res[ 0 ] + '/' + addition + '.json';
        endpoint = endpoint.replace("//", "/")  // Remove duplicated '/' just in case
        return endpoint
    },
    add_endpoint_join: function ( api_string, addition ) {
        // assumes api_string has trailing forward slash "/" character required for POST
        let endpoint = api_string + addition;
        endpoint = endpoint.replace("//", "/")  // Remove duplicated '/' just in case
        return endpoint
    },
    dtPopover: function(value,truncate_length=30,trigger='hover'){
        var ellipsis = '...',
        truncated = _.truncate(value, {
            length: truncate_length,
            omission: ellipsis,
            separator: ' '
        }),
        result = '<span>' + truncated + '</span>',
        popTemplate = _.template('<a href="#" ' +
            'role="button" ' +
            'data-toggle="popover" ' +
            'data-trigger="'+trigger+'" ' +
            'data-placement="top auto"' +
            'data-html="true" ' +
            'data-content="<%= text %>" ' +
            '>more</a>');
        if (_.endsWith(truncated, ellipsis)) {
            result += popTemplate({
                text: value
            });
        }
        return result;
    },
    dtPopoverCellFn: function(cell){
        $(cell).find('[data-toggle="popover"]')
            .popover()
            .on('click', function (e) {
                e.preventDefault();
                return true;
            });
    },
    processError: async function(err){
        console.log(err)
        let errorText = '';
        if (err.body.non_field_errors) {
            console.log('non_field_errors')
            // When non field errors raised
            for (let i=0; i<err.body.non_field_errors.length; i++){
                errorText += err.body.non_field_errors[i] + '<br />';
            }
        } else if(Array.isArray(err.body)) {
            console.log('isArray')
            // When serializers.ValidationError raised
            for (let i=0; i<err.body.length; i++){
                errorText += err.body[i] + '<br />';
            }
        } else {
            console.log('else')
            // When field errors raised
            for (let field_name in err.body){
                if (err.body.hasOwnProperty(field_name)){
                    errorText += field_name + ':<br />';
                    for (let j=0; j<err.body[field_name].length; j++){
                        errorText += err.body[field_name][j] + '<br />';
                    }
                }
            }
        }
        await swal("Error", errorText, "error");
    },
    post_and_redirect: function(url, postData) {
        /* http.post and ajax do not allow redirect from Django View (post method),
           this function allows redirect by mimicking a form submit.

           usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
        */
        var postFormStr = "<form method='POST' action='" + url + "'>";

        for (var key in postData) {
            if (postData.hasOwnProperty(key)) {
                postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
            }
        }
        postFormStr += "</form>";
        var formElement = $(postFormStr);
        $('body').append(formElement);
        $(formElement).submit();
    },
    enablePopovers: function(){
        let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
        let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            let popover = new bootstrap.Popover(popoverTriggerEl)
        })
    },
};
