import Ember from 'ember';
const $ = window.$;

export default Ember.Component.extend({

  url: '',

  // override it when you extend this class
  className: null,

  selector: Ember.computed('className', function() {
    return '.image-box.' + this.get("className");
  }),

  /* a hack to fix image url when data is changed */
  didUpdate() {
    this._super(...arguments);
    let select = $(this.get('selector'));
    select.find("img").attr("src", select.find("a").attr("href"));
  }

});
