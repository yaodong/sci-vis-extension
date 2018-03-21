import Ember from 'ember';
const $ = window.$;

export default Ember.Component.extend({

  url: '',

  // override it when you extend this class
  className: '',

  group: 'image-box',

  title: null,

  /* a hack to fix image url when data is changed */
  didUpdate() {
    this._super(...arguments);
    let emberView = $('#' + this.elementId);
    emberView.find("img").attr("src", emberView.find("a").attr("href"));
  }

});
