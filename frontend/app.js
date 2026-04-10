const form = document.getElementById("predict-form");
const resultBox = document.getElementById("result");
const predictionText = document.getElementById("prediction-text");
const rawResponse = document.getElementById("raw-response");

// Replace with your actual API endpoint
const API_URL = "/predict";

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    build_age_yrs: Number(document.getElementById("build_age_yrs").value),
    building_class_category: document.getElementById("building_class_category").value,
    dist_to_station: Number(document.getElementById("dist_to_station").value),
    gross_sqft: Number(document.getElementById("gross_sqft").value),
    neighborhood: document.getElementById("neighborhood").value,
    within_half_mi: Number(document.getElementById("within_half_mi").value)
  };

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const text = await response.text();

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }

    resultBox.classList.remove("hidden");

    if (!response.ok) {
      predictionText.textContent = `Request failed with status ${response.status}`;
      rawResponse.textContent =
        typeof data === "string" ? data : JSON.stringify(data, null, 2);
      return;
    }

    const predictedPrice =
      data.predicted_price ??
      data.prediction ??
      data.predicted_sale_price;

    predictionText.textContent = predictedPrice
      ? `Predicted Price: $${Number(predictedPrice).toLocaleString()}`
      : "Prediction received.";

    rawResponse.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultBox.classList.remove("hidden");
    predictionText.textContent = "Network/browser request failed.";
    rawResponse.textContent = String(error);
  }
});