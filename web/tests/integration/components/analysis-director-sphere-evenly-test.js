import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('analysis-director-sphere-evenly', 'Integration | Component | analysis director sphere evenly', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{analysis-director-sphere-evenly}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#analysis-director-sphere-evenly}}
      template block text
    {{/analysis-director-sphere-evenly}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
