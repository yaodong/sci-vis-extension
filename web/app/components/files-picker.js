import Ember from 'ember';

export default Ember.Component.extend({

  actions: {

    passName() {
      let fileName = Ember.$("#file-picker-pass-name").val();
      this.sendAction("fileNameChanged", fileName);
    }

  }

});
