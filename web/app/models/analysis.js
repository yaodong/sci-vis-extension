import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  dataset: DS.belongsTo('dataset'),
  params: DS.attr(),
  createdAt: DS.attr('date')
});
