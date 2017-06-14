import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('analysis-panel-sphere', 'Integration | Component | analysis panel sphere', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{analysis-panel-sphere}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#analysis-panel-sphere}}
      template block text
    {{/analysis-panel-sphere}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
