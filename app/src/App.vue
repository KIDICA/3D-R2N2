<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark static-top bg-primary">
      <div class="container">
        <a class="navbar-brand rubik branding" href="#">3D-R2N2</a>
        <!--
        <button
            class="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarResponsive"
            aria-controls="navbarResponsive"
            aria-expanded="false"
            aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ml-auto" style="display: none"></ul>
        </div>
        -->
      </div>
    </nav>

    <div class="main container">
      <router-view ref="view"></router-view>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'app',
    components: {}
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
  }
  .navbar {
    z-index: 1;
  }
</style>
