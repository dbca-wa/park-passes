<template>
  <div class="container" id="shopHome">
    <div class="row">
      <div class="col-4">
        <div class="list-item voucher">
          <img src="https://picsum.photos/id/1/300/150" />
          <div class="more-information">More Information</div>
          <div class="display-name">Gift Voucher</div>
        </div>
        <div class="list-item pass-type">
          <img src="https://picsum.photos/id/1016/300/150" />
          <div class="more-information">More Information</div>
          <div class="display-name">Pass Type Display Name</div>
        </div>
        <div class="list-item pass-type">
          <img src="https://picsum.photos/id/1043/300/150" />
          <div class="more-information">More Information</div>
          <div class="display-name">Pass Type Display Name</div>
        </div>
        <div class="list-item pass-type">
          <img src="https://picsum.photos/id/1039/300/150" />
          <div class="more-information">More Information</div>
          <div class="display-name">Pass Type Display Name</div>
        </div>
        <div class="list-item pass-type">
          <img src="https://picsum.photos/id/1050/300/150" />
          <div class="more-information">More Information</div>
          <div class="display-name">Pass Type Display Name</div>
        </div>
      </div>
      <div class="col">

        <h1>Park Passes</h1>

        <p class="lead">Your ticket to the natural beauty of Western Australia.</p>

        <p>Exploring Western Australia's stunning parks and reserves? Park passes offer both value for money and convenience.</p>

        <p>And why not purchase a Gift Voucher? The perfect gift for that nature lover you want to surprise!</p>

        <div class="home-options">

          <div class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/8/300/170" class="img-fluid rounded-start" alt="Frequently Asked Questions">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">FAQ</h5>
                  <p class="card-text">Click here for answers to common questions.</p>
                  <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                </div>
              </div>
            </div>
          </div>

          <div class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/7/300/170" class="img-fluid rounded-start" alt="Help">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">Help</h5>
                  <p class="card-text">Click here for help if you want to update your vehicle details or if you did not receive your park pass.</p>
                  <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                </div>
              </div>
            </div>
          </div>

          <div class="card faq-card mb-3">
            <div class="row g-0">
              <div class="col-md-4">
                <img src="https://picsum.photos/id/101/300/170" class="img-fluid rounded-start" alt="Log In">
              </div>
              <div class="col-md-8">
                <div class="card-body">
                  <h5 class="card-title">Log In</h5>
                  <p class="card-text">
                      <ul>
                        <li>View and download your current park pass</li>
                        <li>Update the vehicle details for your pass</li>
                        <li>Update your other details</li>
                      </ul>
                    </p>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ShopHome",
  data: function () {
    return {
      something: null,
    };
  },
};
</script>

<style scoped>
.card-text ul {
  font-size:.7em;
}

.card {
  opacity: 1;
}

.card:hover {
  cursor: pointer;
  opacity: 0.8;
}

.list-item {
  position: relative;
  display: inline-block;
}

.list-item img {
  opacity: 1;
}

.list-item img:hover {
  opacity: 0.8;
  cursor: pointer;
}

.display-name {
  position: absolute;
  bottom: 6px;
  left: 6px;
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px;
  border-radius: 5px;
}

.list-item,
.voucher {
  margin: 0 0 8px 0;
}

.more-information {
  display: inline-block;
  position: relative;
  margin-left: -57px;
  font-size: 1.1em;
  color: #9f9f9f;

  transform: rotate(-90deg);

  /* Legacy vendor prefixes that you probably don't need... */

  /* Safari */
  -webkit-transform: rotate(-90deg);

  /* Firefox */
  -moz-transform: rotate(-90deg);

  /* IE */
  -ms-transform: rotate(-90deg);

  /* Opera */
  -o-transform: rotate(-90deg);

  /* Internet Explorer */
  filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=3);
}
</style>
