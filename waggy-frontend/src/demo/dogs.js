/** SYNTHETIC / DEMO ONLY. Filling this profile does not create a persisted dog. */

export var DEMO_DOG = {
  name: "Dolly",
  pet_name: "Dolly",
  primary_breed: "Labrador Retriever",
  secondary_breed: "Golden Retriever",
  breeds: ["Labrador Retriever", "Golden Retriever"],
  birthday: "2021-04-15",
  as_of_date: "2026-09-09",
  weight: 30,
  sex: "Female",
  activity_level: "Moderate",
  current_environment: "Temperate Outdoor",
  observed_conditions: ["joint_stiffness", "itching"],
};

export var WORKBENCH_EXAMPLE_REQUEST = {
  name: "Dolly",
  pet_name: "Dolly",
  primary_breed: "Labrador Retriever",
  secondary_breed: "Golden Retriever",
  breeds: ["Labrador Retriever", "Golden Retriever"],
  birthday: "2021-04-15",
  as_of_date: "2026-09-09",
  weight: 30,
  sex: "Female",
  activity_level: "Moderate",
  current_environment: "Temperate Outdoor",
  observed_conditions: ["joint_stiffness", "itching"],
  correlation_id: "omega16-example-001",
  role_context: {
    groomer: { observations: "coat dryness noted at shoulders", observed_conditions: [] },
    business: { segment: "" },
  },
};
