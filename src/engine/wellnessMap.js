'use strict';

const WELLNESS_GOALS = {
  joint_health: {
    id: 'joint_health',
    title: 'Joint Health',
    why_template: 'elevated lifetime joint-support needs based on body conformation, size, and published veterinary prevalence studies',
    conditions: ['hip_dysplasia', 'ivdd', 'cruciate_ligament_rupture', 'osteoarthritis', 'luxating_patella', 'elbow_dysplasia']
  },
  skin_health: {
    id: 'skin_health',
    title: 'Skin Health',
    why_template: 'additional skin-barrier and coat support may provide long-term comfort based on coat biology and dermatology evidence',
    conditions: ['atopic_dermatitis', 'dry_skin', 'hot_spots', 'immune_mediated_dermatosis', 'pyoderma']
  },
  dental_health: {
    id: 'dental_health',
    title: 'Dental Health',
    why_template: 'preventative oral care may reduce plaque burden common in companion breeds with compact dentition',
    conditions: ['dental_disease', 'periodontal_disease']
  },
  digestive_health: {
    id: 'digestive_health',
    title: 'Digestive Health',
    why_template: 'digestive resilience support aligns with breed GI sensitivity patterns in published cohort studies',
    conditions: ['chronic_enteropathy', 'ibd', 'food_sensitivities', 'colitis']
  },
  weight_management: {
    id: 'weight_management',
    title: 'Weight Management',
    why_template: 'metabolic and activity biology suggests proactive weight management may improve long-term mobility',
    conditions: ['obesity']
  },
  immune_support: {
    id: 'immune_support',
    title: 'Immune Support',
    why_template: 'immune-modulating nutrition may support breeds with documented immune-mediated predispositions',
    conditions: ['immune_mediated_dermatosis']
  },
  respiratory_comfort: {
    id: 'respiratory_comfort',
    title: 'Respiratory Comfort',
    why_template: 'airway-friendly lifestyle and nutrition may benefit brachycephalic or heat-sensitive conformation',
    conditions: ['boas', 'heat_stress_syndrome', 'tracheal_collapse']
  },
  eye_health: {
    id: 'eye_health',
    title: 'Eye Health',
    why_template: 'ocular antioxidant support may benefit breeds with documented eye-health prevalence patterns',
    conditions: ['cataracts', 'tear_staining', 'corneal_ulceration', 'progressive_retinal_atrophy']
  },
  cardiac_support: {
    id: 'cardiac_support',
    title: 'Cardiac Support',
    why_template: 'cardiovascular nutritional support may benefit breeds with elevated cardiac prevalence in registry data',
    conditions: ['degenerative_valve_disease', 'dilated_cardiomyopathy', 'heart_murmur']
  },
  activity_support: {
    id: 'activity_support',
    title: 'Activity Support',
    why_template: 'structured activity and recovery nutrition may support high-drive working and sporting biology',
    conditions: ['exercise_induced_collapse', 'cruciate_ligament_rupture']
  }
};

const CONDITION_TO_GOAL = {};
for (const goal of Object.values(WELLNESS_GOALS)) {
  for (const c of goal.conditions) {
    CONDITION_TO_GOAL[c] = goal.id;
  }
}

function goalForCondition(conditionKey) {
  return CONDITION_TO_GOAL[conditionKey] || 'general_wellness';
}

function friendlyTraitLabel(category, value) {
  const labels = {
    size: `Large body`,
    body_type: `${value} build`,
    weakness_group: `${value} genetic architecture`,
    energy: `${value} activity biology`,
    function_group: `${value} working lineage`,
    coat_type: `${value} coat`,
    climate: `${value} climate adaptation`,
    lifespan: `${value} lifespan profile`,
    skull_type: `${value} skull conformation`
  };
  if (category === 'size' && value === 'Large') return 'Large body';
  if (category === 'size' && value === 'Medium') return 'Medium frame';
  if (category === 'body_type' && value === 'Athletic') return 'Sporting build';
  if (category === 'body_type' && value === 'Chondrodysplastic') return 'Long-spine conformation';
  return labels[category] || `${value}`;
}

module.exports = { WELLNESS_GOALS, CONDITION_TO_GOAL, goalForCondition, friendlyTraitLabel };
