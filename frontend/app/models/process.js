import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  dataset: DS.belongsTo('dataset'),
  method: DS.attr('string'),
  params: DS.attr(),
  summary: DS.attr(),
  createdAt: DS.attr('date')
});
