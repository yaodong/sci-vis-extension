import Ember from 'ember';

export default Ember.Component.extend({

  analysis: null,

  store: Ember.inject.service(),

  init() {
    this._super(...arguments);
    const store = this.get('store');

    this.query('xxx').then((q) => {
      console.log(q);
    });

  },


  query(item) {
    return this.get('store').find('query', this.get('analysis.id') + '::' + item);
  }

});
