import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('analysis-ui-view', 'Integration | Component | analysis ui view', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{analysis-ui-view}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#analysis-ui-view}}
      template block text
    {{/analysis-ui-view}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
