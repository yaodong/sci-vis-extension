import Ember from 'ember';

export default Ember.Controller.extend({

  actions: {
    directionChanged(data) {
      console.log("directionChanged", data);
    }
  }

});
