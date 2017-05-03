import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  params: DS.attr(),
  status: DS.attr("number"),
  createdAt: DS.attr('date'),
  results: DS.attr(),
});
