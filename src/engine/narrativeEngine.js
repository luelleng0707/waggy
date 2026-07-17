'use strict';

function composePreventativeNarrative({
  dogName,
  trait,
  breed,
  biologicalPurpose,
  currentClimate,
  prevalencePercent,
  condition,
  samplePopulation,
  sourceName,
  activityName,
  nutrient,
  targetDose
}) {
  return `${dogName} inherited a ${trait} from their ${breed} ancestry. While advantageous for ${biologicalPurpose}, in a ${currentClimate} environment, this trait presents specific management considerations, such as a ${prevalencePercent}% incidence of ${condition} observed in ${samplePopulation} (Source: ${sourceName}). To proactively manage this, lifestyle modifications including ${activityName} are recommended. Furthermore, based on veterinary physiology, targeted nutritional intervention with ${nutrient} is required at a dosage of ${targetDose} to support long-term health.`;
}

module.exports = { composePreventativeNarrative };

