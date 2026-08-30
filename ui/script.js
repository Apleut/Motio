document.getElementById('faceTracking').addEventListener('change', (e) => {
  if (window.pywebview) {
    window.pywebview.api.update_setting('face_tracking', e.target.checked);
  }
});

function setupSlider(id, valueId, key, decimals = 2) {
  const el = document.getElementById(id);
  const valueEl = document.getElementById(valueId);
  el.addEventListener('input', () => {
    const val = parseFloat(el.value);
    valueEl.textContent = val.toFixed(decimals);
    if (window.pywebview) {
      window.pywebview.api.update_setting(key, val);
    }
  });
}

setupSlider('zoomMargin', 'zoomMarginValue', 'zoom_margin');
setupSlider('smoothing', 'smoothingValue', 'tracking_smoothing_alpha');

document.getElementById('resetBtn').addEventListener('click', () => {
  if (window.pywebview) {
    window.pywebview.api.reset_settings().then(applySettings);
  }
});

document.getElementById('cameraSelect').addEventListener('change', (e) => {
  if (window.pywebview) {
    window.pywebview.api.set_camera_device(parseInt(e.target.value, 10));
  }
});

function populateCameraList(devices) {
  const select = document.getElementById('cameraSelect');
  select.innerHTML = '';
  devices.forEach((d) => {
    const opt = document.createElement('option');
    opt.value = d.index;
    opt.textContent = d.name || `Camera ${d.index}`;
    select.appendChild(opt);
  });
}

function applySettings(settings) {
  document.getElementById('faceTracking').checked = settings.face_tracking;

  const zoomMargin = document.getElementById('zoomMargin');
  zoomMargin.value = settings.zoom_margin;
  document.getElementById('zoomMarginValue').textContent = settings.zoom_margin.toFixed(2);

  const smoothing = document.getElementById('smoothing');
  smoothing.value = settings.tracking_smoothing_alpha;
  document.getElementById('smoothingValue').textContent =
    settings.tracking_smoothing_alpha.toFixed(2);

  if (settings.camera_device !== undefined) {
    document.getElementById('cameraSelect').value = settings.camera_device;
  }
}


function updateVirtualCamStatus(status) {
  const el = document.getElementById('virtualCamStatus');
  if (!el) return;

  if (status.ok) {
    el.textContent = '';
    el.classList.remove('status--error');
  } else {
    el.textContent = status.error;
    el.classList.add('status--error');
  }
}

window.addEventListener('pywebviewready', () => {
  window.pywebview.api.get_settings().then(applySettings);
  window.pywebview.api.list_cameras().then(populateCameraList);
});