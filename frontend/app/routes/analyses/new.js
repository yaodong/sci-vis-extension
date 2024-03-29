import Ember from 'ember';

export default Ember.Route.extend({

  model(params) {
    if (!params.dataset_id) {
      return null;
    }

    const dataset = this.get('store').findRecord('dataset', params.dataset_id);
    const analysis = this.get('store').createRecord('analysis',
                                                    {dataset_id: params.dataset_id, params: {}});

    return {
      dataset: dataset,
      analysis: analysis
    };

  },

  afterModel(model, transition) {
    if (!model.dataset) {
      this.transitionTo('datasets');
    }
  },

  setupController(controller, model) {
    this._super(controller, model);
    model.dataset.then((d) => {
      controller.set('title', 'Analysis of "' + d.get('name') + '"');
    });
  }

});
