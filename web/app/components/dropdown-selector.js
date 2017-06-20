import Ember from 'ember';

export default Ember.Component.extend({

  options: [],

  selectedKey: null,
  selectedText: 'Select...',

  callbackParams: null,
  callbackAction: null,

  actions: {
    clicked(key, text) {
      this.set('selectedKey', key);
      this.set('selectedText', text);
      this.sendAction("callbackAction", key, text, this.get('callbackParam'));
    }
  }

});
