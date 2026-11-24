(() => {
  const lat = document.getElementById("id_latitude");
  const lng = document.getElementById("id_longitude");
  const state = document.getElementById("location-state");
  const button = document.getElementById("capture-location");
  if (!lat || !lng || !button) return;
  let map = window.L ? L.map("location-map").setView([25.3, 74.6], 12) : null;
  let marker = null;
  if (map) L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap" }).addTo(map);
  button.addEventListener("click", () => {
    state.textContent = "Finding your location…";
    if (!navigator.geolocation) { state.textContent = "Geolocation is not supported by this browser."; return; }
    navigator.geolocation.getCurrentPosition(async position => {
      const latitude = position.coords.latitude.toFixed(6), longitude = position.coords.longitude.toFixed(6);
      lat.value = latitude; lng.value = longitude;
      if (map) { map.setView([latitude, longitude], 16); if (marker) marker.setLatLng([latitude, longitude]); else marker = L.marker([latitude, longitude]).addTo(map); }
      state.textContent = "Location captured. Looking up address…";
      try {
        const response = await fetch("https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=" + encodeURIComponent(latitude) + "&lon=" + encodeURIComponent(longitude));
        if (response.ok) { const data = await response.json(); const address = document.getElementById("id_address"); if (address && data.display_name) address.value = data.display_name.slice(0, 255); }
      } catch (_) {}
      state.textContent = "Location captured: " + latitude + ", " + longitude;
    }, error => {
      state.textContent = error.code === 1 ? "Location permission denied. Enable location access and retry." : error.code === 3 ? "Location request timed out. Please retry." : "Unable to get your location. Try again.";
    }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
  });
})();
