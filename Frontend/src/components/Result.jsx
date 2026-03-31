function Result({ data }) {
  if (!data) return null;

  const getColor = () => {
    if (data.freshness_class === "Fresh") return "#22c55e";
    if (data.freshness_class === "Semi-Rotten") return "#facc15";
    return "#ef4444";
  };

  return (
    <div className="resultCard">
      <img
        src={`data:image/jpeg;base64,${data.image_base64}`}
        className="foodImage"
      />

      <h2>{data.food_name}</h2>

      <div className="badge" style={{ background: getColor() }}>
        {data.freshness_class}
      </div>

      <p>Confidence: {(data.confidence * 100).toFixed(0)}%</p>

      <h3>Nutritional Information</h3>
      <div className="nutritionGrid">
        <div className="nutriBox">🔥 {data.nutrition.calories}<br/>Calories</div>
        <div className="nutriBox">🍞 {data.nutrition.carbs}g<br/>Carbs</div>
        <div className="nutriBox">🥩 {data.nutrition.protein}g<br/>Protein</div>
        <div className="nutriBox">🧈 {data.nutrition.fat}g<br/>Fat</div>
        <div className="nutriBox">🌿 {data.nutrition.fiber}g<br/>Fiber</div>
      </div>

      {/* 3 Boxes Side by Side */}
      <div className="sideBySide">
        <div className="infoBox">
          <h3>Health Benefits</h3>
          <p>{data.health_benefits}</p>
        </div>

        <div className="infoBox">
          <h3>Bioactive Compounds</h3>
          <div className="tags">
            {data.bioactive_compounds.map((item, index) => (
              <span key={index} className="tag">{item}</span>
            ))}
          </div>
        </div>

        <div className="infoBox">
          <h3>Health Warnings</h3>
          <p>Diabetes: {data.health_warnings.diabetes_risk}</p>
          <p>Thyroid: {data.health_warnings.thyroid_impact}</p>
          <p>BP: {data.health_warnings.blood_pressure}</p>
          <p>Cholesterol: {data.health_warnings.cholesterol}</p>
          <p>Weight: {data.health_warnings.weight_management}</p>
        </div>
      </div>
    </div>
  );
}

export default Result;