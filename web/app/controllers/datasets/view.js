import Ember from 'ember';

export default Ember.Controller.extend({

  relatedAnalyses: Ember.computed("model", function() {
    return this.get('store').query('analysis', {
      dataset: this.get('model.id')
    });
  })

});
