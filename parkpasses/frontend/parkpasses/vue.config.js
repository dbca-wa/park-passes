const path = require('path')
const webpack = require('webpack');

module.exports = {
    outputDir: path.resolve(__dirname, "../../static/parkpasses_vue"),
    publicPath: '/static/parkpasses_vue/',
    filenameHashing: false,
    //runtimeCompiler: true,
    chainWebpack: config => {
        config.resolve.alias.set('@vue-utils', path.resolve(__dirname, 'src/utils/vue'));
        config.resolve.alias.set('@common-utils', path.resolve(__dirname, 'src/components/common/'));
        //config.resolve.alias.set('datetimepicker','eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js');
        //config.resolve.alias.set('easing','jquery.easing/jquery.easing.js');
    },
    configureWebpack: {
        plugins:[
            new webpack.ProvidePlugin({
               $: "jquery",
               moment: "moment",
               swal: "sweetalert2",
               _: 'lodash',
           })
        ],
        devServer: {
            host: 'localhost',
            allowedHosts: 'all',
            devMiddleware: {
                //index: true,
                writeToDisk: true,
            },
            hot:true,
        },
        module: {
            rules: [
              /* config.module.rule('images') */
              {
                test: /\.(png|jpe?g|gif|webp|avif)(\?.*)?$/,
                type: 'asset/resource',
                generator: {
                  filename: 'img/[name][ext]'
                }
              },
              /* config.module.rule('fonts') */
              {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/i,
                type: 'asset/resource',
                generator: {
                  filename: 'fonts/[name][ext]'
                }
              },
            ]
        },
    }
};
