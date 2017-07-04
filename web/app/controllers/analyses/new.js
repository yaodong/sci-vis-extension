import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['dataset_id'],
  dataset_id: null,

  title: null,

  titleChanged: Ember.observer('title', function() {
    this.set('model.analysis.title', this.get('title'));
  }),

  options: {
    processes: [
      {
        key: 'sphere_evenly_sampling',
        text: 'evenly distributed projection in 3d'
      },
      {
       key: 'search_best_linear_projection',
       text: 'search best linear projection'
      }
    ],
    searching_algorithms: [
      {
        key: 'downhill',
        text: 'downhill'
      }
    ]
  },

  processDefaults: {
    sphere_evenly_sampling: [
      ['sample_size', 200],
    ],
    search_best_linear_projection: [
      ['scaling_dimension', 3],
      ['max_iterations', 100]
    ]
  },

  resetParams(processName) {
    const defaults = this.get('processDefaults.' + processName);
    defaults.forEach((i) => {
      this.set('model.analysis.params.' + i[0], i[1]);
    });
  },

  paramsChanged(key, text, paramKey) {
    if (paramKey == 'process') {
      this.resetParams(key);
    }

    this.set('model.analysis.params.' + paramKey, key);
  },


  actions: {
    submit() {
      const that = this;
      const analysis = this.get('model.analysis');

      analysis.title = this.get('title');
      analysis.set('dataset', this.get('model.dataset'));
      analysis.save().then(() => {
        that.transitionToRoute('analyses.view', analysis.id);
      });
    }
  }

});
